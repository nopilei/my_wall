from django.db import models


class State(models.TextChoices):
    SUBSCRIBING = 'subscribing'
    SUBSCRIBED = 'subscribed'
    DEFAULT = 'default'


class UserState(models.Model):
    user_id = models.IntegerField()
    current_state = models.CharField(choices=State.choices, max_length=32)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'current_state'], name='unique_state_per_user'),
        ]
