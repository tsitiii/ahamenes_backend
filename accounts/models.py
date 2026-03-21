from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'super_admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('approval_status', 'approved')
        extra_fields.setdefault('is_active', True)
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('member', 'Approved Member'),
        ('team_admin', 'Team Admin'),
        ('super_admin', 'Super Admin'),
    ]
    
    TEAM_CHOICES = [
        ('space_technology', 'Space Technology'),
        ('software', 'Software'),
        ('astronomy', 'Astronomy'),
        ('social_media', 'Social Media'),
    ]
    
    APPROVAL_STATUS = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    # Required fields
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    # Approval status
    approval_status = models.CharField(
        max_length=20, 
        choices=APPROVAL_STATUS, 
        default='pending'
    )
    rejection_reason = models.TextField(blank=True, null=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_users'
    )
    
    # Role and team (only set after approval)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='member')
    team = models.CharField(max_length=50, choices=TEAM_CHOICES, blank=True, null=True)
    
    # Profile
    profile_picture = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, max_length=500)
    skills = models.TextField(blank=True, help_text='Comma-separated list of skills')
    
    # Personal info
    phone_number = models.CharField(max_length=20, blank=True)
    student_id = models.CharField(max_length=50, blank=True)
    year_of_study = models.IntegerField(null=True, blank=True)
    department = models.CharField(max_length=100, blank=True)
    
    # Social links
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    personal_website = models.URLField(blank=True)
    
    # Django required fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name
    
    @property
    def can_login(self):
        """Check if user can login"""
        return self.approval_status == 'approved' and self.is_active
    
    @property
    def skills_list(self):
        """Return skills as a list"""
        if self.skills:
            return [skill.strip() for skill in self.skills.split(',')]
        return []
    
    def approve(self, admin_user, team=None, role='member'):
        """Approve this user"""
        self.approval_status = 'approved'
        self.approved_at = timezone.now()
        self.approved_by = admin_user
        if team:
            self.team = team
        self.role = role
        self.is_active = True
        self.save()
    
    def reject(self, admin_user, reason=""):
        """Reject this user"""
        self.approval_status = 'rejected'
        self.rejection_reason = reason
        self.approved_by = admin_user
        self.is_active = False
        self.save()