from django.contrib import admin
#importamos los modelos de datos que hemos creado
from .models import Category, Post

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    #Pasamos los campos que queremos mostrar como solo lectura
    readonly_fields = ('created','updated')
    
class PostAdmin(admin.ModelAdmin):

    class Media:
        css = {
            'all': ('../blog/css/custom_ckeditor.css',)
        }

    #Pasamos los campos que queremos mostrar como solo lectura
    readonly_fields = ('created','updated')
    #Pasamos los campos que queremos mostrar en el panel de administrador
    list_display = ('title','author','published','post_categories')
    ordering = ('author','published')#Si solo queremos dejarlo con uno tiene que ser asi ('author',) sino, da error y no detecta como una tupla
    search_fields = ('title','author__username','categories__name')#El username al ser de otra tabla hay que usar esa sintaxis
    date_hierarchy = 'published' #Esto nos permite crear una jerarquia de entradas para navegar por anos, meses y dias
    list_filter = ('author__username','categories__name') #Permite filtros a la derecha en funcion del username, las categorias...

    #Esta funcion nos permite incluir las ManyToMany a la lista de datos que se muestran de un post, de otra forma fallaria
    def post_categories(self,obj):
        return ", ".join([c.name for c in obj.categories.all().order_by("name")])
    post_categories.short_description = "Categorias"

    

admin.site.register(Category,CategoryAdmin)
admin.site.register(Post,PostAdmin)
