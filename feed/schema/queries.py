import graphene
from graphql import GraphQLError
from django.db.models import Count

from feed.models import Post, Bookmark, Follow, Share
from .types import PostType, ShareType

#------------------------------
# Queries (READ DATA)
#------------------------------

class Query(graphene.ObjectType):
    all_posts = graphene.List(
        PostType,
        limit=graphene.Int(default_value=10),
        offset=graphene.Int(default_value=0),
    )

    post_by_id = graphene.Field(PostType, id=graphene.ID(required=True))

    my_feed = graphene.List(
        PostType,
        limit=graphene.Int(default_value=10),
        offset=graphene.Int(default_value=0),
    )

    my_bookmarks = graphene.List(PostType)

    post_shares = graphene.List(
        ShareType,
        post_id=graphene.ID(required=True)
    )

    # --------- Resolver -----------
    def resolve_all_posts(self, info, limit=10, offset=0):
        return(
            Post.objects
            .annotate(
                likes_count=Count('likes'),
                comments_count=Count('comments'),
                shares_count=Count('shares'),
            )
            .select_related('author')
            .prefetch_related('comments', 'likes', 'shares')
            .all()[offset: offset + limit]
        )
    
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