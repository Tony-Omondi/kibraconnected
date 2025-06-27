from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Ad(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='ads/', null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ads')
    link = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title