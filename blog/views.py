from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from .models import Post, Category
from .forms import PostForm
from django.contrib.auth.models import User


# Create your views here.
class PostListView(ListView):
    model = Post
    template_name = 'blog/posts_list.html'
    paginate_by = 3


#Clase para ver tan solo un post
class PostDetailView(DetailView):
    model = Post


@method_decorator(staff_member_required, name="dispatch")
class PostCreate(CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('posts:posts')

    #Pasamos el user para que se incluya en la relacion ManyToOne del autor (con el User)
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)



@method_decorator(staff_member_required, name="dispatch")
class PostUpdate(UpdateView):
    model = Post
    form_class = PostForm
    template_name_suffix = '_update_form'

    #Redefinimos la url para poder poner el argumento de ok, detectarlo en el HTML y mostrar el link al post actualizado
    def get_success_url(self):
        return reverse_lazy('posts:update',args=[self.object.id])+'?ok'


@method_decorator(staff_member_required, name="dispatch")
class PostDelete(DeleteView):
    model = Post
    success_url = reverse_lazy('posts:posts')


#Este es un caso especial, usamos un DetailView ya que solo queremos devolver una categoria (Esta categoria ya contiene todos los posts relacionados con ella)
#Al no ser un List view no se puede realizar la paginacion
class CategoryDetailView(DetailView):
    model = Category
    template_name = 'blog/category_list.html'