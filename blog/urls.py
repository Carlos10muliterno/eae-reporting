from django.urls import path
from .views import PostListView, PostDetailView, PostCreate, PostDelete, PostUpdate, CategoryDetailView

posts_patterns = ([
    path('', PostListView.as_view(), name='posts'),
    path('<int:pk>/<slug:post_slug>/', PostDetailView.as_view(), name='post'),
    path('create/', PostCreate.as_view(), name='create'),
    path('delete/<int:pk>/', PostDelete.as_view(), name='delete'),
    path('update/<int:pk>/', PostUpdate.as_view(), name='update'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category'),
], 'posts')