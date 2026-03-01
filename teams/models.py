import uuid
from django.db import models
from cloudinary.models import CloudinaryField

class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    description = models.TextField()

    logo = CloudinaryField('logo_image', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class MembershipApplication(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)

    department = models.CharField(max_length=150)
    year_of_study = models.PositiveIntegerField()

    team_preference = models.CharField(max_length=100)

    motivation = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.status}"

class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='projects'
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    media_url = models.URLField(blank=True, null=True)

    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Achievement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='achievements'
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    media_url = models.URLField(blank=True, null=True)

    created_by = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "events"
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["created_by"]),
        ]

    def __str__(self):
        return self.title


class EventRegistration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registrations"
    )

    full_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=255)
    department = models.CharField(max_length=150)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "event_registrations"
        indexes = [
            models.Index(fields=["event"]),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.event.title}"


