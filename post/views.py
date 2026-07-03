from django.shortcuts import render
from rest_framework import generics, viewsets, permissions
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from .models import (Post,
                     PostLike,
                     PostComment,
                     CommentLike)
from .serializers import (
                    PostSerializer,
                    PostLikeSerializer,
                    CommentLikeSerializer,
                    CommentSerializer)

class PostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Post.objects.all()
