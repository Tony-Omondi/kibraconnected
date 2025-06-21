from django.contrib import admin
from .models import Post, Comment, Like

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'content_preview', 'created_at', 'image', 'likes_count')
    list_filter = ('created_at', 'author__role')
    search_fields = ('author__email', 'content')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def content_preview(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_preview.short_description = 'Content'

    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Likes'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'text_preview', 'created_at')
    list_filter = ('created_at', 'user__role')
    search_fields = ('user__email', 'text', 'post__content')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def text_preview(self, obj):
        return obj.text[:50] + ('...' if len(obj.text) > 50 else '')
    text_preview.short_description = 'Text'

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'post_content')
    list_filter = ('user__role',)
    search_fields = ('user__email', 'post__content')
    ordering = ('post',)

    def post_content(self, obj):
        return obj.post.content[:50] + ('...' if len(obj.post.content) > 50 else '')
    post_content.short_description = 'Post Content'