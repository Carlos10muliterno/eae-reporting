from django.contrib import admin
from .models import Estudio, Category

# Register your models here.
class EstudioAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    # Inyectamos nuestro fichero css
    class Media:
        css = {
            'all': ('pages/css/custom_ckeditor.css',)
        }

class CategoryAdmin(admin.ModelAdmin):
    #Pasamos los campos que queremos mostrar como solo lectura
    readonly_fields = ('created','updated')
    search_fields = ('name','')#El username al ser de otra tabla hay que usar esa sintaxis

admin.site.register(Category,CategoryAdmin)
       
#admin.site.register(Estudio, EstudioAdmin)