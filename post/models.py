from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator, MaxLengthValidator
from django.db import models

from shared.models import BaseModel

User = get_user_model()

class Post(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='posts_images', validators=[FileExtensionValidator(['jpg', 'png'])] )
    caption = models.TextField(validators=[MaxLengthValidator(5000)])

    class Meta:
        db_table = 'posts'
        verbose_name = 'post'
        verbose_name_plural = 'posts'


class PostComment(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField(validators=[MaxLengthValidator(1000)])
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='child')

class PostLike(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'post'],
                name='unique_post_like'
            )
        ]

class CommentLike(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment  = models.ForeignKey(PostComment, on_delete=models.CASCADE, related_name='likes')
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'comment'],
                name='unique_comment_like'
            )
        ]
