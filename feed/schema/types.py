import graphene
from graphene_django import DjangoObjectType
from feed.models import Post, Comment, Like, Bookmark, Follow, Share

#---------------------------
# GRAPHQL TYPES
#---------------------------


class PostType(DjangoObjectType):
    likes_count = graphene.Int()
    comments_count = graphene.Int()
    shares_count = graphene.Int()
    liked_by_me = graphene.Boolean()
    bookmarked_by_me = graphene.Boolean()
    shared_by_me = graphene.Boolean()

    class Meta:
        model = Post
        fields = ('id', 'author', 'content', 'created_at', 'updated_at')

    def resolve_likes_count(self, info):
        return getattr(self, 'likes_count', self.likes.count())
    
    def resolve_comments_count(self, info):
        return getattr(self, 'comments_count', self.comments.count())
    
    def resolve_shares_count(self, info):
        return getattr(self, 'shares_count', self.shares.count())
    
    def resolve_liked_by_me(self, info):
        user = info.context.user
        if not user.is_authenticated:
            return False
        return Like.objects.filter(user=user, post=self).exists()
    
    def resolve_bookmarked_by_me(self, info):
        user = info.context.user
        if not user.is_authenticated:
            return False
        return Bookmark.objects.filter(user=user, post=self).exists()
    
    def resolve_shared_by_me(self, info):
        user = info.context.user
        if not user.is_authenticated:
            return False
        return Share.objects.filter(original_post=self, shared_by=user).exists()


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = ('id', 'post', 'author', 'content', 'created_at')


class LikeType(DjangoObjectType):
    class Meta:
        model = Like
        fields = ('id', 'user', 'post', 'created_at')


class BookmarkType(DjangoObjectType):
    class Meta:
        model = Bookmark
        fields = ('id', 'user', 'post', 'created_at')


class FollowType(DjangoObjectType):
    class Meta:
        model = Follow
        fields = ('id', 'follower', 'following', 'created_at')


class ShareType(DjangoObjectType):
    class Meta:
        model = Share
        fields = ('id', 'original_post', 'shared_by', 'created_at')