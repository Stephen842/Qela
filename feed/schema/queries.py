import graphene
from graphql import GraphQLError
from django.db.models import Count

from feed.models import Post, Bookmark, Follow, Share, UserAnalytics, PostDailyMetrics
from .types import PostType, ShareType, UserAnalyticsType, PostDailyMetricsType

#------------------------------
# Queries (READ DATA)
#------------------------------

class Query(graphene.ObjectType):
    all_posts = graphene.List(
        PostType,
        first=graphene.Int(),
        after=graphene.String(),
        sort_by=graphene.String()
    )

    post_by_id = graphene.Field(PostType, id=graphene.ID(required=True))

    my_feed = graphene.List(
        PostType,
        first=graphene.Int(),
        after=graphene.String()
    )

    my_bookmarks = graphene.List(PostType)

    post_shares = graphene.List(
        ShareType,
        post_id=graphene.ID(required=True)
    )

    my_analytics = graphene.Field(UserAnalyticsType)

    post_metrics = graphene.List(
        PostDailyMetricsType,
        post_id=graphene.ID(required=True)
    )

    # --------- Resolver -----------
    def resolve_all_posts(self, info, first=10, after=None, sort_by='latest'):
        qs = (
            Post.objects
            .annotate(
                likes_count=Count('likes'),
                comments_count=Count('comments'),
                shares_count=Count('shares'),
            )
            .select_related('author')
            .prefetch_related('comments', 'likes', 'shares')
            .order_by('-created_at')
        )

        if sort_by == 'latest':
            qs = qs.order_by('-created_at')
        elif sort_by == 'popular':
            qs = qs.order_by('-likes_count')
        elif sort_by == 'engagement':
            qs = qs.order_by('-comments_count', '-likes_count')

        if after:
            qs = qs.filter(created_at__lt=after)
        
        return qs[:first]
    
    def resolve_post_by_id(self, info, id):
        return(
            Post.objects
            .annotate(
                likes_count=Count('likes'),
                comments_count=Count('comments'),
                shares_count=Count('shares'),
            )
            .select_related('author')
            .prefetch_related('comments', 'likes', 'shares')
            .filter(id=id)
            .first()
        )
    
    def resolve_my_feed(self, info, limit=10, offset=0):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Authentication required')
        
        following_users = Follow.objects.filter(follower=user).values_list('following', flat=True)

        return(
            Post.objects
            .filter(author__in=following_users)
            .annotate(
                likes_count=Count('likes'),
                comments_count=Count('comments'),
                shares_count=Count('shares'),
            )
            .select_related('author')
            .prefetch_related('comments', 'likes', 'shares')[offset: offset + limit]
        )
    
    def resolve_my_bookmarks(self, info):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Authentication required')
        
        bookmarked_posts = Bookmark.objects.filter(user=user).values_list('post', flat=True)

        return(
            Post.objects
            .filter(id__in=bookmarked_posts)
            .annotate(
                likes_count=Count('likes'),
                comments_count=Count('comments'),
                shares_count=Count('shares'),
            )
            .select_related('author')
            .prefetch_related('comments', 'likes', 'shares')
        )
    
    def resolve_post_shares(self, info, post_id):
        return Share.objects.filter(
            original_post_id=post_id
        ).select_related('shared_by', 'original_post')
    
    def resolve_my_analytics(self, info):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('Authentication required')

        analytics, _ = UserAnalytics.objects.get_or_create(user=user)
        return analytics
    
    def resolve_post_metrics(self, info, post_id):
        return PostDailyMetrics.objects.filter(post_id=post_id).order_by('-date')