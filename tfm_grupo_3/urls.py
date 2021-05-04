"""tfm_grupo_3 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from blog.urls import posts_patterns
from studies.urls import estudios_patterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('posts/',include(posts_patterns)),
    #Path de auth
    path('', include('django.contrib.auth.urls')),
    path('',include('pages.urls')),
    path('contact/',include('contact.urls')),
    path('estudios/', include(estudios_patterns)),
]

"""
Permite mostrar las imagenes que se suben a la web, estas están almacenadas en la carpeta media 
"""
from django.conf.urls.static import static
from django.conf import settings
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)