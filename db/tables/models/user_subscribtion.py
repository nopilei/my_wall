from django.db import models


class UserSubscribtion(models.Model):
    user_id = models.IntegerField()
    channel_id = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'channel_id'], name='unique_subscribtion_per_user'),
        ]
