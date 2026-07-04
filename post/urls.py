import code
from django.urls import path
from .views import (PostListView,
                    PostCreateView,
                    PostRetrieveUpdateDestroyAPIView,
                    PostCommentListView,
                    PostCommentCreateView,
                    CommentListCreateView,
                    CommentRetrieveAPIView,
                    PostLikeListView,
                    CommentLikeListView,
                    PostLikeAPIView,
                    CommentLikeAPIView
                    )

urlpatterns = [
    path('list/', PostListView.as_view()),
    path('create/', PostCreateView.as_view()),
    path('<uuid:pk>/', PostRetrieveUpdateDestroyAPIView.as_view() ),
    path('<uuid:pk>/comments/', PostCommentListView.as_view()),
    path('<uuid:pk>/comments/create/', PostCommentCreateView.as_view()), # idga ulangan holda yaratish

    path('comments/', CommentListCreateView.as_view()), # id si ham jo'natilganda yaratish
    path('<uuid:pk>/likes/', PostLikeListView.as_view()),
    path('comments/<uuid:pk>/', CommentRetrieveAPIView.as_view()),
    path('comments/<uuid:pk>.likes/', PostLikeListView.as_view()),
    path('comments/<uuid:pk>/likes/', CommentLikeListView.as_view()),
    path('<uuid:pk>/create-delete-likes/', PostLikeAPIView.as_view()),
    path('comments/<uuid:pk>/create-delete-likes/', CommentLikeAPIView.as_view()),
    

]