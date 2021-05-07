from django.db import models
from ckeditor.fields import RichTextField


leng_choices = (
    ('es','Español'),
    ('en', 'Inglés'),
    ('pt','Portugués'),
)


#Tenemos que crear cada columna de la BBDD aqui
class Tweet(models.Model):
    text = models.CharField(max_length=300, verbose_name="Texto del tweet")
    name = models.CharField(max_length=300, verbose_name="Nombre del usuario", default="Anónimo")
    username = models.CharField(max_length=300, verbose_name="Username", default="Anónimo")
    picture = models.URLField(blank=True, null=True)
    retweets = models.IntegerField()
    likes = models.IntegerField()
    quotes = models.IntegerField()
    replies = models.IntegerField()
    neg_sen = models.FloatField()
    neu_sen = models.FloatField()
    pos_sen = models.FloatField()
    placeID = models.IntegerField(blank=True,null=True)    
    created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación de la publicación") #Solo lo hace la primera vez que sea crea la instancia en la BBDD
    updated = models.DateTimeField(auto_now=True, verbose_name="Fecha de la última edición") #Se actualiza cada vez que cambiamos algo del portfolio asociado

class Review(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    rating = models.IntegerField()
    reting_total = models.IntegerField()
    latitud = models.IntegerField(blank=True,null=True)
    longitud = models.IntegerField(blank=True,null=True)
    placeID = models.IntegerField(blank=True,null=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación de la review") #Solo lo hace la primera vez que sea crea la instancia en la BBDD
    updated = models.DateTimeField(auto_now=True, verbose_name="Fecha de la última edición") #Se actualiza cada vez que cambiamos algo del portfolio asociado    

#Tenemos que crear cada columna de la BBDD aqui
class Category(models.Model):
    name = models.CharField(max_length=100,unique=True, verbose_name="Nombre de la categoría")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación de la categoria") #Solo lo hace la primera vez que sea crea la instancia en la BBDD
    updated = models.DateTimeField(auto_now=True, verbose_name="Fecha de la última edición") #Se actualiza cada vez que cambiamos algo del portfolio asociado

    #Pasamos los nombres que se muestran en el panel de administrador ademas de el criterio de ordenación
    class Meta:
        verbose_name = "sector"
        verbose_name_plural = "sectores"
        #Ordenamos las categorías por orden de creación (De más nuevas a más antiguas)
        ordering = ["-created"] 
    
    #Definimos que el nombre de la categoria es el mismo que se define en el titulo
    def __str__(self): 
        return self.name


class Estudio(models.Model):
    title = models.CharField(verbose_name="Título", max_length=200)
    fintech = models.CharField(verbose_name="Nombre de la Fintech", max_length=50,default='None')
    #lenguaje = models.CharField(max_length=10,choices=leng_choices,default='es',verbose_name='Lenguaje de estudio de tweets')
    content = RichTextField(verbose_name="Contenido")
    #Definimos el nombre de la relacion para usarla en el HTML de category e inyectar los posts
    categories = models.ManyToManyField(Category, verbose_name="Tipo de empresa", related_name="get_estudios") 
    order = models.SmallIntegerField(verbose_name="Orden", default=0)
    created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated = models.DateTimeField(auto_now=True, verbose_name="Fecha de edición")
    tweets = models.ManyToManyField(Tweet, verbose_name="Tweet", related_name="get_tweets")
    sen_predominant = models.CharField(blank=True, null=True, max_length=8)
    neu_sen = models.FloatField(blank=True, null=True)
    pos_sen = models.FloatField(blank=True, null=True)
    neg_sen = models.FloatField(blank=True, null=True)
    graph1 = models.TextField(blank=True, null=True)
    graph2 = models.TextField(blank=True, null=True)
    graph3 = models.TextField(blank=True, null=True)
    graph4 = models.TextField(blank=True, null=True)
    graph5 = models.TextField(blank=True, null=True)
    graph6 = models.TextField(blank=True, null=True)
    graph7 = models.TextField(blank=True, null=True)
    graph8 = models.TextField(blank=True, null=True)
    graph9 = models.TextField(blank=True, null=True)
    graph10 = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    success = models.BooleanField(default=False)
    error = models.CharField(verbose_name="Error", max_length=10, blank=True, null=True)

    class Meta:
        verbose_name = "estudio"
        verbose_name_plural = "estudios"
        ordering = ['order', 'title']

    def __str__(self):
        return self.title