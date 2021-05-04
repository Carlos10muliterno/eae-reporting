from django.urls import path
from .views import EstudioListView, EstudioDelete, EstudioDetailView, EstudioUpdate,CategoryDetailView
from . import views

estudios_patterns = ([
    path('', EstudioListView.as_view(), name='estudios'),
    path('create/', views.EstudioCreate, name='create'),
    path('<int:pk>/<slug:page_slug>/', EstudioDetailView.as_view(), name='estudio'),
    path('update/<int:pk>/', EstudioUpdate.as_view(), name='update'),
    path('delete/<int:pk>/', EstudioDelete.as_view(), name='delete'),
    path('tipo-empresa/<int:pk>/', CategoryDetailView.as_view(), name='category'),
    path('report-pdf/<int:pk>/', views.RenderPDFView , name='pdf'),
], 'estudios')