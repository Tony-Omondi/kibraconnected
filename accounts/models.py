from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
import uuid

class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
        ('politician', 'Politician'),
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    is_email_verified = models.BooleanField(default=False)  # Renamed for clarity
    verification_code = models.CharField(max_length=6, blank=True, null=True, unique=True)  # Added for verification

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def clean(self):
        if not self.email:
            raise ValidationError("Email is required.")
        if User.objects.filter(email=self.email).exclude(id=self.id).exists():
            raise ValidationError("This email is already registered.")
        super().clean()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, max_length=500)  # Added max_length for control
    location = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"Profile for {self.user.email}"

    def clean(self):
        if self.bio and len(self.bio) > 500:
            raise ValidationError("Bio must not exceed 500 characters.")
        super().clean()

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')
        indexes = [
            models.Index(fields=['follower', 'followed']),
            models.Index(fields=['followed']),  # Added for better query performance
        ]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(follower=models.F('followed')),
                name='prevent_self_follow'
            ),
        ]

    def __str__(self):
        return f"{self.follower.email} follows {self.followed.email}"

    def clean(self):
        if self.follower == self.followed:
            raise ValidationError("Users cannot follow themselves.")
        super().clean()