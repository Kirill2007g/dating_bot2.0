from src.db.db_queries import UserQueries, get_all_seen_ids, get_profiles_limit
from src.validation.validation import build_media_group, media_list
from src.db.db_queries import ActionQueries, add_to_seen_ids_table

async def get_ten_profiles(tg_id) -> tuple[list, list]:
    user_profile = await UserQueries.get_profile(tg_id=tg_id)
    if user_profile is None:
        return [], []
    user_aclt = await UserQueries.get_profile_aclt(user_profile.tg_id)
    if user_aclt is None:
        return [], []
    fields = {key: value for key, value in user_aclt.items()}
    seen_ids = await get_all_seen_ids(user_tg_id=tg_id)
    profiles = await get_profiles_limit(**fields, seen_ids=seen_ids)
    if not profiles:
        return [], []
    ten_users = []
    for user in profiles:
        if user is None:
            continue
        ten_users.append({user.id: {'name': user.name, 'age': user.age, 'city': user.city,
                                                'description': user.description}})
    valid_profiles = [user for user in profiles if user is not None]
    return ten_users, valid_profiles

async def add_reaction(from_user_id, to_user_id, reaction, message=None):
    if message is None:
        await ActionQueries.add_action(from_user_id=from_user_id, to_user_id=to_user_id, reaction_type=reaction)
    if message is not None:
        await ActionQueries.add_action(from_user_id=from_user_id, to_user_id=to_user_id, reaction_type=reaction, message=message)
    await add_to_seen_ids_table(user_tg_id=from_user_id, viewed_profile_id=to_user_id)


async def get_next_profile(tg_id, ten_users_list):
    if ten_users_list != []:
        users, profiles = await get_ten_profiles(tg_id=tg_id)
        if not profiles:
            return [], [], [], None
        user = profiles[0]
        user_media = user.media if hasattr(user, 'media') else None
        if user_media:
            _media_list = await media_list(user_media)
            media_group = build_media_group(_media_list)
            if media_group:
                users.pop(0)
                profiles.pop(0)
                return users, profiles, media_group, user
        users.pop(0)
        profiles.pop(0)
        return users, profiles, [], user


    return ten_users_list, [], [], None