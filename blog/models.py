import uuid
from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField


class BlogPost(models.Model):

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts',
        null=True,
        blank=True
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    content = models.TextField()
    category = models.CharField(max_length=100, null=True, blank=True)

    featured_image = CloudinaryField('blog_image', blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    published_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "blog_posts"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["category"]),
            models.Index(fields=["published_at"]),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.author}"


class Comment(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        null=True,
        blank=True
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "comments"
        indexes = [
            models.Index(fields=["post"]),
        ]
    
    def __str__(self):
        return self.post.title