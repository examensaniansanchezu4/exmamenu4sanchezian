from rest_framework import serializers
from .models import Categoria, Autor, Libro, Prestamo
from django.contrib.auth.models import User


class CategoriaSerializer(serializers.ModelSerializer):
    """Serializer para Categoría"""
    
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'activo', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion']


class AutorSerializer(serializers.ModelSerializer):
    """Serializer para Autor"""
    
    nombre_completo = serializers.ReadOnlyField()
    total_libros = serializers.SerializerMethodField()
    
    class Meta:
        model = Autor
        fields = ['id', 'nombre', 'apellido', 'nombre_completo', 
                 'fecha_nacimiento', 'pais_origen', 'biografia', 
                 'foto', 'total_libros', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion']
    
    def get_total_libros(self, obj):
        return obj.libros.filter(activo=True).count()


class LibroSerializer(serializers.ModelSerializer):
    """Serializer para Libro"""
    
    autor_nombre = serializers.CharField(source='autor.nombre_completo', read_only=True)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    esta_disponible = serializers.ReadOnlyField()
    
    class Meta:
        model = Libro
        fields = [
            'id', 'titulo', 'subtitulo', 'isbn',
            'autor', 'autor_nombre',
            'categoria', 'categoria_nombre',
            'editorial', 'fecha_publicacion', 'paginas', 'idioma',
            'descripcion', 'imagen_portada',
            'stock', 'estado', 'esta_disponible',
            'precio', 'valoracion',
            'activo', 'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']
    
    def validate_isbn(self, value):
        """Validar que ISBN tenga 13 dígitos"""
        isbn = value.replace('-', '').replace(' ', '')
        if not isbn.isdigit():
            raise serializers.ValidationError("ISBN debe contener solo números")
        if len(isbn) != 13:
            raise serializers.ValidationError("ISBN debe tener 13 dígitos")
        return value
    
    def validate_precio(self, value):
        """Validar que precio sea positivo"""
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a 0")
        return value


class PrestamoSerializer(serializers.ModelSerializer):
    """Serializer para Préstamo"""
    
    libro_titulo = serializers.CharField(source='libro.titulo', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    dias_prestamo = serializers.ReadOnlyField()
    esta_atrasado = serializers.ReadOnlyField()
    
    class Meta:
        model = Prestamo
        fields = [
            'id', 'libro', 'libro_titulo',
            'usuario', 'usuario_nombre',
            'fecha_prestamo', 'fecha_devolucion_esperada', 'fecha_devolucion_real',
            'estado', 'dias_prestamo', 'esta_atrasado', 'notas'
        ]
        read_only_fields = ['id', 'fecha_prestamo']
    
    def validate(self, data):
        """Validar que el libro esté disponible antes de prestar"""
        if self.instance is None:  # Solo en creación
            libro = data.get('libro')
            if not libro.esta_disponible:
                raise serializers.ValidationError({
                    'libro': 'Este libro no está disponible para préstamo'
                })
        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializer para Usuario"""
    
    total_prestamos = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'is_staff', 'date_joined', 'total_prestamos']
        read_only_fields = ['id', 'date_joined']
    
    def get_total_prestamos(self, obj):
        return obj.prestamos.count()