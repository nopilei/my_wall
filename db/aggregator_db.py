from db.tables.models import UserSubscribtion


async def add_subscribtion(user_id: int, channel_id: int):
    await UserSubscribtion.objects.aget_or_create(user_id=user_id, channel_id=channel_id)


async def get_all_channels():
    return UserSubscribtion.objects.values_list('channel_id', flat=True).distinct()
