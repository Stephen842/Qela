from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'Post {self.id} by {self.author}'
    

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post']),
            models.Index(fields=['author']),
            models.Index(fields=['post', 'created_at']),
        ]

    def __str__(self):
        return f'Comment {self.id} on Post {self.post_id}'
    

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                name='unique_user_post_like'
            )
        ]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['post']),
        ]

    def __str__(self):
        return f'{self.user.username} liked Post {self.post_id}'
    

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                name='unique_user_saved_post'
            )
        ]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['post']),
        ]

    def __str__(self):
        return f'{self.user} bookmarked Post {self.post_id}'
    

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'following'],
                name='unique_follow_relationship'
            )
        ]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['follower']),
            models.Index(fields=['following']),
        ]

    def __str__(self):
        return f'{self.follower} follows {self.following}'
    


class Share(models.Model):
    original_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='shares')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_post')
    created_at = models.DateTimeField(auto_now_add=True)