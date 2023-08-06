from db.tables.models import UserSubscribtion


def get_user_subscribtions(channel_id: str):
    return UserSubscribtion.objects.filter(channel_id=channel_id)
