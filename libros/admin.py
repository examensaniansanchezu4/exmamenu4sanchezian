from django.contrib import admin
from .models import Categoria, Autor, Libro, Prestamo


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo', 'fecha_creacion']
    list_filter = ['activo']
    search_fields = ['nombre']


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'pais_origen', 'fecha_nacimiento']
    search_fields = ['nombre', 'apellido']
    list_filter = ['pais_origen']


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'autor', 'isbn', 'estado', 'stock', 'precio']
    list_filter = ['estado', 'categoria', 'autor']
    search_fields = ['titulo', 'isbn', 'descripcion']
    list_editable = ['stock', 'estado']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ['libro', 'usuario', 'fecha_prestamo', 
                   'fecha_devolucion_esperada', 'estado']
    list_filter = ['estado', 'fecha_prestamo']
    search_fields = ['libro__titulo', 'usuario__username']
    readonly_fields = ['fecha_prestamo']