from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics, viewsets, permissions, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from shared.custom_pagination import CustomPagination

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
    pagination_class = CustomPagination

    def get_queryset(self):
        return Post.objects.all()


class PostCreateView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PostRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def put(self, request   , *args, **kwargs):
        post = self.get_object()
        serializer = self.serializer_class(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'success': True,
            'message': 'Post successfully updated!',
        }, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        post.delete()
        return Response({
            'success': True,
            'message': 'Post successfully deleted!',

        }, status=status.HTTP_204_NO_CONTENT)