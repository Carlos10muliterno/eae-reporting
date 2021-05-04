from django import forms
from .models import Estudio

class EstudioForm(forms.ModelForm):

    class Meta:
        model = Estudio
        fields = ['title','fintech','content','categories']
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control','placeholder':'Titulo del estudio'}),
            'fintech': forms.TextInput(attrs={'class':'form-control','placeholder':'Fintech'}),
            'content': forms.Textarea(attrs={'class':'form-control'}),
            'order': forms.NumberInput(attrs={'class':'form-control','placeholder':'Importancia'}),
            'categories': forms.SelectMultiple(attrs={'class':'form-control'}),
        }
        labels = {
            'title': '',
            'fintech': 'Nombre de la Fintech que se quiere estudiar',
            'content':'Descripción del estudio que desea realizar',
            'order': '',
        }