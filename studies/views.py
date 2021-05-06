from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from .models import Estudio, Tweet, Review, Category
from .forms import EstudioForm
from .funciones import collectData #, dataTreatment
from django import forms
import time
import sys
import threading

class EstudioListView(ListView):
    model = Estudio
    paginate_by = 3
    #titulo = MultiplicarTitulo(model.title)
    #print ('\n\n\nEl nombre editado es: ',estudio.title,'\n\n\n')
    def get_queryset(self):
        filter_val = self.request.GET.get('filter', '')
        #empresa
        if  filter_val.strip():
            new_context = Estudio.objects.filter(
                title__contains=filter_val) | Estudio.objects.filter(fintech__contains=filter_val).order_by('-pk')
        else:
            new_context = Estudio.objects.all().order_by('-pk')
        return new_context

    def get_context_data(self, **kwargs):
        context = super(EstudioListView, self).get_context_data(**kwargs)
        filtro = self.request.GET.get('filter', '')
        if  filtro.strip():
            context['filter'] = filtro        
        return context

class EstudioDetailView(DetailView):
    model = Estudio

    #Funcion para editar el conetexto que se le pasa a la web
    def get_context_data(self, **kwargs):
        context = super(EstudioDetailView, self).get_context_data(**kwargs)
        return context


@method_decorator(staff_member_required, name="dispatch")
class EstudioUpdate(UpdateView):
    model = Estudio
    form_class = EstudioForm
    template_name_suffix = '_update_form'
    def get_form(self, form_class=None):
         form = super().get_form(form_class)
         form.fields['fintech'].widget = forms.HiddenInput()
         return form

    def get_success_url(self):
        return reverse_lazy('estudios:update',args=[self.object.id])+'?ok'

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'studies/category_list.html'
    

@method_decorator(staff_member_required, name="dispatch")
class EstudioDelete(DeleteView):
    model = Estudio
    success_url = reverse_lazy('estudios:estudios')

def EstudioCreate(request):
    #time.sleep(3)
    if request.method == 'GET':
        form = EstudioForm()
    else:
        form = EstudioForm(request.POST)
        if form.is_valid():
            try:

                #intentamos guardar el estudio
                empresa = request.POST.get('fintech','')
                
                empresa = str(empresa)

                data_obj = form.save()
                # Llamamos a la función para que edite el nombre

                t = threading.Thread(target=collectData, args=[empresa, data_obj.pk])
                t.setDaemon(True)
                t.start()

                print('sigue sin parar la vaina')

                return redirect(reverse('estudios:estudios')+"?ok")
            except Exception as e:
                print('El error es: ',e)
                print(e.with_traceback)
                print("Oops!", sys.exc_info()[0], "occurred.")
                return redirect(reverse('estudios:estudios')+"?fail")

    return render(request, "studies/estudio_form.html", {'form': form})




import os
import base64
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def RenderPDFView(request,pk):
    estudio = get_object_or_404(Estudio,pk=pk)
    template_path = 'studies/report_PDF.html'
    '''
    with open('pages/static/pages/img/studies-bg.jpg', 'rb') as img_f:
        encoded_string = base64.b64encode(img_f.read())
    context = {'estudio': estudio,
            'carlos': encoded_string}
    '''
    context = {'estudio': estudio}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    
    response['Content-Disposition'] = 'attachment; filename=report_'+ estudio.fintech + '.pdf'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response