from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.utils.timezone import now
# Create your models here.

#Método que nos permite borrar las fotos antiguas y dar el path nuevo de las imagenes
def custom_upload_to(instance,filename):
    try:
        old_instance = Post.objects.get(pk=instance.pk)
        old_instance.image.delete()
        return 'blog/' + filename
    except:
        return 'blog/' + filename
    

#Tenemos que crear cada columna de la BBDD aqui
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre de la categoría")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación de la publicación") #Solo lo hace la primera vez que sea crea la instancia en la BBDD
    updated = models.DateTimeField(auto_now=True, verbose_name="Fecha de la última edición") #Se actualiza cada vez que cambiamos algo del portfolio asociado

    #Pasamos los nombres que se muestran en el panel de administrador ademas de el criterio de ordenación
    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        #Ordenamos las categorías por orden de creación (De más nuevas a más antiguas)
        ordering = ["-created"] 
    
    #Definimos que el nombre de la categoria es el mismo que se define en el titulo
    def __str__(self): 
        return self.name


#Creamos los campos que va tener un post
class Post(models.Model):
    #Título
    title = models.CharField(max_length=200, verbose_name="Título")
    #Cuerpo de la publicación
    content = RichTextField(verbose_name= "Contenido de la publicación")
    #Fecha en la que se publica el post
    published = models.DateTimeField(verbose_name="Fecha de publicación",default=now)
    #Imagen opcional para unir al post
    image = models.ImageField(verbose_name= "Imagen", upload_to=custom_upload_to,null=True,blank=True)
    #Definimos el user que ha creado el post
    author = models.ForeignKey(User, verbose_name="Autor",on_delete=models.CASCADE)
    #Definimos el nombre de la relacion para usarla en el HTML de category e inyectar los posts
    categories = models.ManyToManyField(Category, verbose_name="Categorías", related_name="get_posts") 
    #Guardamos la fecha de creación del post 
    created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de publicación") 
    #Guarda la fecha en la cual se realiza una actualización
    updated = models.DateTimeField(auto_now=True, verbose_name="Fecha de la última edición") 

    #Pasamos los nombres que se muestran en el panel de administrador ademas de el criterio de ordenación
    class Meta:
        verbose_name = "entrada"
        verbose_name_plural = "entradas"
        ordering = ["-created"]

    #El titulo que se muestra en el panel de admin es el titulo que el user le ha dado
    def __str__(self): 
        return self.title

# Receive the pre_delete signal and delete the file associated with the model instance.
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

@receiver(pre_delete, sender=Post)
def post_delete(sender, instance, **kwargs):
    instance.image.delete(False)


def pass_the_user_to_form(sender,instance,**kwargs):
    
    print('\n\n\n Dentro 2\n\n\n {}')
    user = User.objects.all().filter(pk=instance.pk)
    print(User.pk)
    
    return User.objects.all().filter(pk=instance.pk)