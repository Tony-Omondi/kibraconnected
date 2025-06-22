from django.contrib import admin
from .models import NewsArticle, Comment, Like

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at', 'comment_count', 'like_count')
    list_filter = ('created_at', 'updated_at', 'author__role')
    search_fields = ('title', 'content', 'author__email')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def comment_count(self, obj):
        return obj.comments.count()
    comment_count.short_description = 'Comments'

    def like_count(self, obj):
        return obj.likes.count()
    like_count.short_description = 'Likes'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'content', 'created_at')
    list_filter = ('created_at', 'article')
    search_fields = ('content', 'user__email', 'article__title')
    ordering = ('-created_at',)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'created_at')
    list_filter = ('created_at', 'article')
    search_fields = ('user__email', 'article__title')
    ordering = ('-created_at',)