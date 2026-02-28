from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from decimal import Decimal


class Categoria(models.Model):
    """Categorías de libros (Ficción, No Ficción, Ciencia, etc.)"""
    
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categorías"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Autor(models.Model):
    """Autores de libros"""
    
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    pais_origen = models.CharField(max_length=100, blank=True)
    biografia = models.TextField(blank=True)
    foto = models.URLField(blank=True, help_text="URL de la foto del autor")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Autores"
        ordering = ['apellido', 'nombre']
        unique_together = ['nombre', 'apellido']  # No duplicar autor
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"


class Libro(models.Model):
    """Modelo principal de libros"""
    
    # Estados del libro
    DISPONIBLE = 'disponible'
    PRESTADO = 'prestado'
    MANTENIMIENTO = 'mantenimiento'
    PERDIDO = 'perdido'
    
    ESTADOS = [
        (DISPONIBLE, 'Disponible'),
        (PRESTADO, 'Prestado'),
        (MANTENIMIENTO, 'En Mantenimiento'),
        (PERDIDO, 'Perdido'),
    ]
    
    # Información básica
    titulo = models.CharField(max_length=100)
    subtitulo = models.CharField(max_length=100, blank=True)
    isbn = models.CharField(max_length=13, unique=True, 
                           help_text="ISBN de 13 dígitos")
    
    # Relaciones
    autor = models.ForeignKey(Autor, on_delete=models.PROTECT, 
                             related_name='libros')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, 
                                 null=True, related_name='libros')
    
    # Detalles de publicación
    editorial = models.CharField(max_length=100, blank=True)
    fecha_publicacion = models.DateField(null=True, blank=True)
    paginas = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1)]
    )
    idioma = models.CharField(max_length=50, default='Español')
    
    # Descripción y contenido
    descripcion = models.TextField(blank=True)
    imagen_portada = models.URLField(blank=True)
    
    # Inventario
    stock = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(0)],
        help_text="Cantidad de ejemplares disponibles"
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, 
                             default=DISPONIBLE)
    
    # Precio y valoración
    precio = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Precio en Lempiras (L)"
    )
    valoracion = models.DecimalField(
        max_digits=3, 
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('5.00'))
        ],
        help_text="Valoración de 0 a 5 estrellas"
    )
    
    # Metadata
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='libros_creados'
    )
    
    class Meta:
        verbose_name_plural = "Libros"
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['isbn']),
            models.Index(fields=['titulo']),
            models.Index(fields=['autor']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.autor.nombre_completo}"
    
    @property
    def esta_disponible(self):
        """Verifica si el libro está disponible para préstamo"""
        return self.estado == self.DISPONIBLE and self.stock > 0
    
    def actualizar_stock(self, cantidad):
        """Actualiza el stock del libro"""
        self.stock += cantidad
        if self.stock < 0:
            self.stock = 0
        if self.stock == 0:
            self.estado = self.PRESTADO
        elif self.stock > 0 and self.estado == self.PRESTADO:
            self.estado = self.DISPONIBLE
        self.save()


class Prestamo(models.Model):
    """Registro de préstamos de libros"""
    
    # Estados del préstamo
    ACTIVO = 'activo'
    DEVUELTO = 'devuelto'
    ATRASADO = 'atrasado'
    PERDIDO = 'perdido'
    
    ESTADOS = [
        (ACTIVO, 'Activo'),
        (DEVUELTO, 'Devuelto'),
        (ATRASADO, 'Atrasado'),
        (PERDIDO, 'Perdido'),
    ]
    
    libro = models.ForeignKey(Libro, on_delete=models.PROTECT, 
                             related_name='prestamos')
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, 
                               related_name='prestamos')
    
    fecha_prestamo = models.DateTimeField(auto_now_add=True)
    fecha_devolucion_esperada = models.DateField()
    fecha_devolucion_real = models.DateTimeField(null=True, blank=True)
    
    estado = models.CharField(max_length=20, choices=ESTADOS, 
                             default=ACTIVO)
    notas = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Préstamos"
        ordering = ['-fecha_prestamo']
    
    def __str__(self):
        return f"{self.libro.titulo} - {self.usuario.username}"
    
    @property
    def dias_prestamo(self):
        """Calcula días que lleva el préstamo"""
        from django.utils import timezone
        if self.fecha_devolucion_real:
            return (self.fecha_devolucion_real - self.fecha_prestamo).days
        return (timezone.now() - self.fecha_prestamo).days
    
    @property
    def esta_atrasado(self):
        """Verifica si el préstamo está atrasado"""
        from django.utils import timezone
        if self.fecha_devolucion_real:
            return False
        return timezone.now().date() > self.fecha_devolucion_esperada