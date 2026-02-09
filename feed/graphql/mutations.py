import graphene
from graphql import GraphQLError
from django.utils import timezone

from feed.models import Post, Comment, Like, Bookmark, Follow, Share, UserAnalytics, PostDailyMetrics
from .types import PostType, CommentType

#-----------------------------
# Mutation (WRITE DATA)
#-----------------------------

class CreatePost(graphene.Mutation):
    class Arguments:
        content = graphene.String(required=True)

    post = graphene.Field(PostType)

    def mutate(self, info, content):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Authentication required')
        
        post = Post.objects.create(author=user, content=content)

        analytics, _ = UserAnalytics.objects.get_or_create(user=user)
        analytics.total_posts += 1
        analytics.save()

        return CreatePost(post=post)
    

class EditPost(graphene.Mutation):
    class Arguments:
        post_id = graphene.ID(required=True)
        content = graphene.String(required=True)

    post = graphene.Field(PostType)

    def mutate(self, info, post_id, content):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Authentication required')
        
        try:
            post = Post.objects.get(id=post_id, author=user)
        except Post.DoesNotExist:
            raise GraphQLError('Post not found or not yours')
        
        post.content = content
        post.save()

        return EditPost(post=post)


class DeletePost(graphene.Mutation):
    class Arguments:
        post_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, post_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Authentication required')

        try:
            post = Post.objects.get(id=post_id, author=user)
        except Post.DoesNotExist:
            raise GraphQLError('Post not found or not yours')
        
        # Capture counts before deletion
        likes_count = post.likes.count()
        comments_count = post.comments.count()
        shares_count = post.shares.count()

        # Delete the post
        post.delete()

        # Update user analytics
        analytics = UserAnalytics.objects.get(user=user)
        analytics.total_posts = max(0, analytics.total_posts - 1)
        analytics.total_likes_recieved = max(0, analytics.total_likes_recieved - likes_count)
        analytics.total_comments_recieved = max(0, analytics.total_comments_recieved - comments_count)
        analytics.total_shares_recieved = max(0, analytics.total_shares_recieved - shares_count)
        analytics.save()
        
        return DeletePost(ok=True)
    

class AddComment(graphene.Mutation):
    class Arguments:
        post_id = graphene.ID(required=True)
        content = graphene.String(required=True)

    comment = graphene.Field(CommentType)

    def mutate(self, info, post_id, content):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Authentication required')

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise GraphQLError('Post not found')

        comment = Comment.objects.create(post=post, author=user, content=content)

        analytics = UserAnalytics.objects.get(user=post.author)
        analytics.total_comments_recieved += 1
        analytics.save()

        metric, _ = PostDailyMetrics.objects.get_or_create(post=post, date=timezone.now().date())
        metric.comments += 1
        metric.save()

        return AddComment(comment=comment)
    

class EditComment(graphene.Mutation):
    class Arguments:
        comment_id = graphene.ID(required=True)
        content = graphene.String(required=True)

    comment = graphene.Field(CommentType)

    def mutate(self, info, comment_id, content):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Authentication required')
        
        try:
            comment = Comment.objects.get(id=comment_id, author=user)
        except Comment.DoesNotExist:
            raise GraphQLError('Comment not found or not yours')
        
        comment.content = content
        comment.save()

        return EditComment(comment=comment)
    

class DeleteComment(graphene.Mutation):
    class Arguments:
        comment_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, comment_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Authentication required')

        try:
            comment = Comment.objects.get(id=comment_id, author=user)
        except Comment.DoesNotExist:
            raise GraphQLError('Comment not found or not yours')
        post = comment.post
        comment.delete()

        analytics = UserAnalytics.objects.get(user=post.author)
        analytics.total_comments_recieved = max(0, analytics.total_comments_recieved - 1)
        analytics.save()

        metric, _ = PostDailyMetrics.objects.get_or_create(post=post, date=timezone.now().date())
        metric.comments = max(0, metric.comments - 1)
        metric.save()
        
        return DeleteComment(ok=True)


class LikePost(graphene.Mutation):
    class Arguments:
        post_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, post_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Authentication required')
        
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise GraphQLError('Post not found')

        like, created = Like.objects.get_or_create(user=user, post=post)

        if created:
            creator = post.author
            analytics = UserAnalytics.objects.get(user=creator)
            analytics.total_likes_recieved += 1
            analytics.save()

            metric, _ = PostDailyMetrics.objects.get_or_create(post=post, date=timezone.now().date())
            metric.likes += 1
            metric.save()

        return LikePost(ok=True)
    

class UnlikePost(graphene.Mutation):
    class Arguments:
        post_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, post_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Authentication required')

        deleted, _ = Like.objects.filter(user=user, post_id=post_id).delete()

        if deleted:
            post = Post.objects.get(id=post_id)
            analytics = UserAnalytics.objects.get(user=post.author)
            analytics.total_likes_recieved -= 1
            analytics.save()

            metric, _ = PostDailyMetrics.objects.get_or_create(post=post, date=timezone.now().date())
            metric.likes = max(0, metric.likes - 1)
            metric.save()
            
        return UnlikePost(ok=True)
    

class BookmarkPost(graphene.Mutation):
    class Arguments:
        post_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, post_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Authentication required')
        
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise GraphQLError('Post not found')

        Bookmark.objects.get_or_create(user=user, post=post)
        return BookmarkPost(ok=True)
    

class UnbookmarkPost(graphene.Mutation):
    class Arguments:
        post_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, post_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Authentication required')

        Bookmark.objects.filter(user=user, post_id=post_id).delete()
        return UnbookmarkPost(ok=True)
    

class FollowUser(graphene.Mutation):
    class Arguments:
        user_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, user_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Authentication required')
        
        if str(user.id) == str(user_id):
            raise GraphQLError('You cannot follow yourself')
        
        Follow.objects.get_or_create(follower=user, following_id=user_id)
        return FollowUser(ok=True)
    

class UnfollowUser(graphene.Mutation):
    class Arguments:
        user_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, user_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Authentication required')
        
        Follow.objects.filter(follower=user, following_id=user_id).delete()
        return UnfollowUser(ok=True)
    

class SharePost(graphene.Mutation):
    class Arguments:
        post_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, post_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Authentication required')

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise GraphQLError('Post not found')

        share, created = Share.objects.get_or_create(original_post=post, shared_by=user)

        if created:
            analytics = UserAnalytics.objects.get(user=post.author)
            analytics.total_shares_recieved += 1
            analytics.save()

            metric, _ = PostDailyMetrics.objects.get_or_create(post=post, date=timezone.now().date())
            metric.shares += 1
            metric.save()

        return SharePost(ok=True)

class Mutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    edit_post = EditPost.Field()
    delete_post = DeletePost.Field()

    add_comment = AddComment.Field()
    edit_comment = EditComment.Field()
    delete_comment = DeleteComment.Field()

    like_post = LikePost.Field()
    unlike_post = UnlikePost.Field()

    bookmark_post = BookmarkPost.Field()
    unbookmark_post = UnbookmarkPost.Field()

    follow_user = FollowUser.Field()
    unfollow_user = UnfollowUser.Field()

    share_post = SharePost.Field()