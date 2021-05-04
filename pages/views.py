from django.shortcuts import render

# Create your views here.
from django.views.generic.base import TemplateView


class HomePageView(TemplateView):
    template_name =  "pages/home.html"
    
    #Redefinir el diccionario de contexto
    def get(self,request, *args,**kwargs):
        return render(request,self.template_name,{'title':"TFM Analisis de FINTECHS",'content':"Web del grupo 3 para el TFM del EAE"})

class AboutPageView(TemplateView):
    template_name =  "pages/about.html"
    #Redefinir el diccionario de contexto
    def get(self,request, *args,**kwargs):
        return render(request,self.template_name,{'title':"Sobre Nosotros",'content':"Somos el grupo 3"})

