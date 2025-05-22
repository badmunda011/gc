from telethon import events
from telethon.tl.functions.channels import GetParticipantsRequest, EditBannedRequest
from telethon.tl.types import ChannelParticipantsSearch, ChatBannedRights

from SUKH import Bad  # Your custom client

ban_rights = ChatBannedRights(
    until_date=None,
    view_messages=True
)

@Bad.on(events.NewMessage(pattern=r"^/clean$"))
async def clean_deleted_users(event):
    if not event.is_group:
        return await event.reply("This command only works in groups.")

    sender = await event.get_sender()
    chat = await event.get_chat()
    me = await Bad.get_permissions(chat.id, 'me')

    if not me.is_admin:
        return await event.reply("I need to be an admin with ban permissions to perform this action.")

    await event.reply("Cleaning up deleted accounts...")

    offset = 0
    limit = 100
    total_banned = 0

    while True:
        participants = await Bad(GetParticipantsRequest(
            channel=chat,
            filter=ChannelParticipantsSearch(''),
            offset=offset,
            limit=limit,
            hash=0
        ))

        if not participants.users:
            break

        for user in participants.users:
            if user.deleted:
                try:
                    await Bad(EditBannedRequest(
                        channel=chat,
                        participant=user.id,
                        banned_rights=ban_rights
                    ))
                    total_banned += 1
                except Exception:
                    continue

        offset += len(participants.users)

    await event.reply(f"Cleanup complete.\nTotal deleted accounts banned: {total_banned}")
