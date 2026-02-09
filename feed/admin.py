from django.contrib import admin
from .models import Post, Comment, Like, Bookmark, Follow, Share, UserAnalytics, PostDailyMetrics

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "created_at", "updated_at")
    list_filter = ("created_at", "author")
    search_fields = ("content", "author__username")
    ordering = ("-created_at",)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "author", "created_at")
    list_filter = ("created_at", "author")
    search_fields = ("content",)
    ordering = ("-created_at",)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "created_at")
    list_filter = ("created_at", "user")
    search_fields = ("user__username",)

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "created_at")
    list_filter = ("created_at", "user")

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "following", "created_at")
    list_filter = ("created_at",)
    search_fields = ("follower__username", "following__username")

@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ("original_post", "shared_by", "created_at")
    list_filter = ("created_at",)

@admin.register(UserAnalytics)
class UserAnalyticsAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "total_posts",
        "total_likes_recieved",
        "total_comments_recieved",
        "total_shares_recieved",
        "updated_at",
    )
    search_fields = ("user__username",)

@admin.register(PostDailyMetrics)
class PostDailyMetricsAdmin(admin.ModelAdmin):
    list_display = ("post", "date", "likes", "comments", "shares")
    list_filter = ("date",)
