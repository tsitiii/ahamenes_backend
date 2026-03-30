from rest_framework import serializers
from .models import BlogPost, Comment


class BlogPostSerializer(serializers.ModelSerializer):
    featured_image = serializers.ImageField(required=False)
    author_name = serializers.ReadOnlyField(source='author.full_name')

    class Meta:
        model = BlogPost
        fields = "__all__"
        read_only_fields = ('id', 'author', 'published_at', 'created_at', 'updated_at')


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ('id', 'post', 'user', 'created_at', 'updated_at')