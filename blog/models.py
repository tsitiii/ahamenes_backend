import uuid
from django.db import models
from cloudinary.models import CloudinaryField


class BlogPost(models.Model):

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    author_id = models.UUIDField(null=True, blank=True) # will be replaced with actual user from accounts

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

    published_at = models.DateTimeField(null=True, blank=True)

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
        return f"{self.title} by {self.author_id}"


class Comment(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    user_id = models.UUIDField(null=True, blank=True) # will be replaced by actual user from accounts

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