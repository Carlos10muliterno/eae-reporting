from django import forms
from .models import Post

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['title','content','image','categories']
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control','placeholder':'Titulo de la pagina'}),
            'content': forms.TextInput(attrs={'class':'form-control'}),
        }
        labels = {
            'title': '',
            'content':'Contenido del post',
        }