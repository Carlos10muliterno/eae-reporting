from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.mail import send_mail
#Importamos el formulario que hemos creado en forms.py
from .forms import  ContactForm 
import traceback

# Create your views here.
#send_mail('Subject here','Here is the message.','carlos10muliterno@gmail.com',['carlos10muliterno@gmail.com'],fail_silently=False,)

"""
Función para recibir el formulario de contacto y poder enviar un mail al usuario informando que se ha enviado el mail correctamente
y enviar un mail al admin para que sepa que se debe de realizar un contacto con un usuario
"""
def contactFormView(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            name = request.POST.get('name','')
            email = request.POST.get('email','')
            content = request.POST.get('content','')
            email_subject = '¡Hemos recibido tu mensaje!'
            email_body = "De {} <{}>\n\n{}".format(name,email,content)
            email_sender = 'fintechsanalyzer@gmail.com'
            print(name,email,content)
            try:
                #intentamos enviar el email, si es exitoso se informa al usuario
                send_mail(email_subject,
                email_body,
                email_sender,
                [email],
                fail_silently=False,)

                #Enviamos el mail al admin
                send_mail('Nuevo contacto que requiere de respuesta',
                    'Mensaje del usuario \n'+email_body,
                    email_sender,
                    [email_sender],
                    fail_silently=False,)
                return redirect(reverse('contact')+"?ok")
            except Exception as e: 
                trace_back = traceback.format_exc()
                message = str(e)+ " " + str(trace_back)
                print (message)
                #Algo ha fallado al enviar el mail

                return redirect(reverse('contact')+"?fail")

    return render(request, "contact/contact_form.html", {'form': form})