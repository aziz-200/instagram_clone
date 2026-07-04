from django.shortcuts import render
from phonenumbers.tzdata.data0 import data
from rest_framework.response import Response
from rest_framework import generics, viewsets, permissions, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.views import APIView

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

class PostCommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs['pk']
        queryset = PostComment.objects.filter(post_id=post_id)

class PostCommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.kwargs['pk']
        serializer.save(author=self.request.user, post_id=post_id)


# class CommentCreateView(generics.CreateAPIView):
#     serializer_class = CommentSerializer
#     permission_classes = [IsAuthenticated]
#
#     def perform_create(self, serializer):
#         serializer.save(author=self.request.user, post_id=self.kwargs['pk'])


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        return self.queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class CommentRetrieveAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]
    queryset = PostComment.objects.all()



class PostLikeListView(generics.ListAPIView):
    serializer_class = PostLikeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        post_id = self.kwargs['pk']
        return Post.objects.filter(post_id=post_id)


class CommentLikeListView(generics.ListAPIView):
    serializer_class = CommentLikeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        comment_id = self.kwargs['pk']
        return CommentLike.objects.filter(comment_id=comment_id)

class PostLikeAPIView(APIView):
    def post(self, request, pk):
        try:
            post_like = PostLike.objects.create(
                author=self.request.user,
                post_id=pk)
            serializer = PostLikeSerializer(post_like)
            data = {
                'success': True,
                'message': 'Post successfully updated!',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            post_like = PostLike.objects.get(
                author =self.request.user,
                pk=pk)
            post_like.delete()
            data = {
                'success': True,
                'message': 'Post successfully deleted!',
                'data': None
            }
            return Response(data, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)



class CommentLikeAPIView(APIView):
    # Toggle like section
    def post(self, request, pk):
        try:
            post_like = PostLike.objects.get(
                author =self.request.user,
                post_id=pk
            )
            post_like.delete()
            data = {
                'success': True,
                'message': 'Comment successfully deleted!',
            }
            return Response(data, status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            post_like = PostLike.objects.create(
                author=self.request.user,
                post_id=pk
            )
            serializer = PostLikeSerializer(post_like)
            data = {
                'success': True,
                'message': 'Comment successfully created!',
                'data': serializer.data
            }
            return Response(data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'success': False,
                'message': str(e),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)




# simple like section

        # try:
        #     comment_like = CommentLike.objects.create(
        #         author=self.request.user,
        #         comment_id=pk
        #     )
        #     serializer = CommentLikeSerializer(comment_like)
        #     data = {
        #         'success': True,
        #         'message': 'Comment successfully updated!',
        #         'data': serializer.data
        #     }
        #     return Response(data, status=status.HTTP_200_OK)
        # except Exception as e:
        #     return Response({
        #         'success': False,
        #         'message': str(e),
        #         'data': None
        #     })


    def delete(self, request, pk):
        try:
            comment_like = CommentLike.objects.get(
                author =self.request.user,
                comment_id=pk
            )
            comment_like.delete()
            data = {
                'success': True,
                'message': 'Comment successfully deleted!',
                'data': None
            }
            return Response(data, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e),
                'data': None
            })
