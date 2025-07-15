import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from posts.models import Like as PostLike, Comment as PostComment
from news.models import Like as NewsLike, Comment as NewsComment
from campaigns.models import CampaignSupport, CampaignComment
from marketplace.models import Order
from accounts.models import Follow
from .models import Notification

logger = logging.getLogger(__name__)

@receiver(post_save, sender=PostLike)
def notify_post_like(sender, instance, created, **kwargs):
    logger.debug(f"PostLike post_save signal triggered: like_id={instance.id}, created={created}")
    try:
        if created and instance.user != instance.post.author:
            Notification.objects.create(
                sender=instance.user,
                recipient=instance.post.author,
                notification_type='like',
                content_type=ContentType.objects.get_for_model(instance.post),
                object_id=instance.post.id,
                message=f"{instance.user.email} liked your post: {instance.post.content[:50]}"
            )
            logger.debug("PostLike notification created successfully")
    except Exception as e:
        logger.error(f"Error in notify_post_like: {str(e)}", exc_info=True)
        raise

@receiver(post_save, sender=PostComment)
def notify_post_comment(sender, instance, created, **kwargs):
    logger.debug(f"PostComment post_save signal triggered: comment_id={instance.id}, created={created}")
    try:
        if created and instance.user != instance.post.author:
            Notification.objects.create(
                sender=instance.user,
                recipient=instance.post.author,
                notification_type='comment',
                content_type=ContentType.objects.get_for_model(instance.post),
                object_id=instance.post.id,
                message=f"{instance.user.email} commented on your post: {instance.text[:50]}"
            )
            logger.debug("PostComment notification created successfully")
    except Exception as e:
        logger.error(f"Error in notify_post_comment: {str(e)}", exc_info=True)
        raise

@receiver(post_save, sender=NewsLike)
def notify_news_like(sender, instance, created, **kwargs):
    logger.debug(f"NewsLike post_save signal triggered: like_id={instance.id}, created={created}")
    try:
        if created and instance.user != instance.article.author:
            Notification.objects.create(
                sender=instance.user,
                recipient=instance.article.author,
                notification_type='like',
                content_type=ContentType.objects.get_for_model(instance.article),
                object_id=instance.article.id,
                message=f"{instance.user.email} liked your article: {instance.article.title}"
            )
            logger.debug("NewsLike notification created successfully")
    except Exception as e:
        logger.error(f"Error in notify_news_like: {str(e)}", exc_info=True)
        raise

@receiver(post_save, sender=NewsComment)
def notify_news_comment(sender, instance, created, **kwargs):
    logger.debug(f"NewsComment post_save signal triggered: comment_id={instance.id}, created={created}")
    try:
        if created and instance.user != instance.article.author:
            Notification.objects.create(
                sender=instance.user,
                recipient=instance.article.author,
                notification_type='comment',
                content_type=ContentType.objects.get_for_model(instance.article),
                object_id=instance.article.id,
                message=f"{instance.user.email} commented on your article: {instance.text[:50]}"
            )
            logger.debug("NewsComment notification created successfully")
    except Exception as e:
        logger.error(f"Error in notify_news_comment: {str(e)}", exc_info=True)
        raise

@receiver(post_save, sender=CampaignSupport)
def notify_campaign_support(sender, instance, created, **kwargs):
    logger.debug(f"CampaignSupport post_save signal triggered: support_id={instance.id}, created={created}")
    try:
        if created and instance.user != instance.campaign.creator:
            Notification.objects.create(
                sender=instance.user,
                recipient=instance.campaign.creator,
                notification_type='campaign_support',
                content_type=ContentType.objects.get_for_model(instance.campaign),
                object_id=instance.campaign.id,
                message=f"{instance.user.email} supported your campaign: {instance.campaign.title}"
            )
            logger.debug("CampaignSupport notification created successfully")
    except Exception as e:
        logger.error(f"Error in notify_campaign_support: {str(e)}", exc_info=True)
        raise

@receiver(post_save, sender=CampaignComment)
def notify_campaign_comment(sender, instance, created, **kwargs):
    logger.debug(f"CampaignComment post_save signal triggered: comment_id={instance.id}, created={created}")
    try:
        if created and instance.user != instance.campaign.creator:
            Notification.objects.create(
                sender=instance.user,
                recipient=instance.campaign.creator,
                notification_type='comment',
                content_type=ContentType.objects.get_for_model(instance.campaign),
                object_id=instance.campaign.id,
                message=f"{instance.user.email} commented on your campaign: {instance.text[:50]}"
            )
            logger.debug("CampaignComment notification created successfully")
    except Exception as e:
        logger.error(f"Error in notify_campaign_comment: {str(e)}", exc_info=True)
        raise

@receiver(post_save, sender=Order)
def notify_order(sender, instance, created, **kwargs):
    logger.debug(f"Order post_save signal triggered: order_id={instance.id}, created={created}")
    try:
        if created:
            Notification.objects.create(
                sender=instance.buyer,
                recipient=instance.product.seller,
                notification_type='order',
                content_type=ContentType.objects.get_for_model(instance.product),
                object_id=instance.product.id,
                message=f"{instance.buyer.email} ordered your product: {instance.product.title}"
            )
            logger.debug("Order notification created successfully")
    except Exception as e:
        logger.error(f"Error in notify_order: {str(e)}", exc_info=True)
        raise

@receiver(post_save, sender=Follow)
def notify_follow(sender, instance, created, **kwargs):
    logger.debug(f"Follow post_save signal triggered: follow_id={instance.id}, created={created}")
    try:
        if created:
            Notification.objects.create(
                sender=instance.follower,
                recipient=instance.followed,
                notification_type='follow',
                message=f"{instance.follower.email} followed you"
            )
            logger.debug("Follow notification created successfully")
    except Exception as e:
        logger.error(f"Error in notify_follow: {str(e)}", exc_info=True)
        raise