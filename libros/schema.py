import graphene
from graphene_django import DjangoObjectType
from .models import Libro, Autor, Categoria


# ===== TYPES (Tipos de Datos) =====

class AutorType(DjangoObjectType):
    class Meta:
        model = Autor
        fields = '__all__'


class CategoriaType(DjangoObjectType):
    class Meta:
        model = Categoria
        fields = '__all__'


class LibroType(DjangoObjectType):
    class Meta:
        model = Libro
        fields = '__all__'
    
    esta_disponible = graphene.Boolean()
    
    def resolve_esta_disponible(self, info):
        return self.esta_disponible


# ===== QUERIES (Consultas) =====

class Query(graphene.ObjectType):
    # Queries simples
    all_libros = graphene.List(LibroType)
    all_autores = graphene.List(AutorType)
    all_categorias = graphene.List(CategoriaType)
    
    # Queries con argumentos
    libro = graphene.Field(
        LibroType,
        id=graphene.Int(),
        isbn=graphene.String()
    )
    
    libros_por_autor = graphene.List(
        LibroType,
        autor_id=graphene.Int(required=True)
    )
    
    libros_disponibles = graphene.List(LibroType)
    
    buscar_libros = graphene.List(
        LibroType,
        titulo=graphene.String(required=True)
    )
    
    # Resolvers
    def resolve_all_libros(self, info):
        return Libro.objects.filter(activo=True)
    
    def resolve_all_autores(self, info):
        return Autor.objects.all()
    
    def resolve_all_categorias(self, info):
        return Categoria.objects.all()
    
    def resolve_libro(self, info, id=None, isbn=None):
        if id:
            return Libro.objects.get(pk=id)
        if isbn:
            return Libro.objects.get(isbn=isbn)
        return None
    
    def resolve_libros_por_autor(self, info, autor_id):
        return Libro.objects.filter(
            autor_id=autor_id,
            activo=True
        )
    
    def resolve_libros_disponibles(self, info):
        return Libro.objects.filter(
            estado=Libro.DISPONIBLE,
            stock__gt=0,
            activo=True
        )
    
    def resolve_buscar_libros(self, info, titulo):
        return Libro.objects.filter(
            titulo__icontains=titulo,
            activo=True
        )


# ===== MUTATIONS (Modificaciones) =====

class ActualizarStockLibro(graphene.Mutation):
    class Arguments:
        libro_id = graphene.Int(required=True)
        cantidad = graphene.Int(required=True)
    
    libro = graphene.Field(LibroType)
    mensaje = graphene.String()
    
    def mutate(self, info, libro_id, cantidad):
        libro = Libro.objects.get(pk=libro_id)
        libro.actualizar_stock(cantidad)
        
        return ActualizarStockLibro(
            libro=libro,
            mensaje=f"Stock actualizado a {libro.stock}"
        )


class CrearAutor(graphene.Mutation):
    class Arguments:
        nombre = graphene.String(required=True)
        fecha_nacimiento = graphene.Date(required=True)
        pais_origen = graphene.String(required=True)
        biografia = graphene.String()
    
    autor = graphene.Field(AutorType)
    
    def mutate(self, info, nombre, fecha_nacimiento, pais_origen, biografia=None):
        autor = Autor.objects.create(
            nombre=nombre,
            fecha_nacimiento=fecha_nacimiento,
            pais_origen=pais_origen,
            biografia=biografia
        )
        return CrearAutor(autor=autor)


class Mutation(graphene.ObjectType):
    actualizar_stock_libro = ActualizarStockLibro.Field()
    crear_autor = CrearAutor.Field()


# ===== SCHEMA =====

schema = graphene.Schema(query=Query, mutation=Mutation)