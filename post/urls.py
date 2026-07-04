import code
from django.urls import path
from .views import (PostListView,
                    PostCreateView,
                    PostRetrieveUpdateDestroyAPIView)

urlpatterns = [
    path('posts/', PostListView.as_view()),
    path('post/create/', PostCreateView.as_view()),
    path('post/<uuid:pk>/', PostRetrieveUpdateDestroyAPIView.as_view() ),

    
]