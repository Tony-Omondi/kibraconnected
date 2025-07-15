from django.db.models.signals import post_save
from django.dispatch import receiver
from posts.models import Comment
from notifications.models import Notification
from django.contrib.auth.models import User

@receiver(post_save, sender=Comment)
def notify_post_comment(sender, instance, created, **kwargs):
    if created:
        post_author = instance.post.author
        if instance.user != post_author:  # Don't notify the commenter themselves
            message = f"{instance.user.email} commented on your post: {instance.text[:50]}"
            Notification.objects.create(
                user=post_author,
                message=message,
                related_post=instance.post,
                notification_type='comment'
            )