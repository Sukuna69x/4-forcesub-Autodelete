import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserNotParticipant

from bot import Bot
from config import CHANNEL_ID, DISABLE_CHANNEL_BUTTON, FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2
from helper_func import encode

async def check_membership(client: Client, user_id: int):
    try:
        # Check membership in the first channel
        member1 = await client.get_chat_member(FORCE_SUB_CHANNEL_1, user_id)
        # Check membership in the second channel
        member2 = await client.get_chat_member(FORCE_SUB_CHANNEL_2, user_id)
        return member1.status in ["member", "administrator", "creator"] and member2.status in ["member", "administrator", "creator"]
    except UserNotParticipant:
        return False
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False

@Bot.on_message(filters.private & ~filters.command(['start', 'users', 'broadcast', 'batch', 'genlink', 'stats']))
async def channel_post(client: Client, message: Message):
    reply_text = await message.reply_text("Please Wait...!", quote=True)

    # Check if the user is a member of the required channels
    is_member = await check_membership(client, message.from_user.id)
    if not is_member:
        buttons = [
            [
                InlineKeyboardButton(text="⚡Join Channel 1⚡", url=client.invitelink),
            ],
            [
                InlineKeyboardButton(text="⚡Join Channel 2⚡", url=client.invitelink2),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)

        await reply_text.edit_text(
            "You need to join the following channels to generate a link:\n"
            "Please join them using the buttons below and try again.",
            reply_markup=reply_markup
        )
        return

    try:
        post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)
    except Exception as e:
        print(e)
        await reply_text.edit_text("Something went Wrong..!")
        return

    converted_id = post_message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])

    await reply_text.edit(f"<b>Here is your link</b>\n\n{link}", reply_markup=reply_markup, disable_web_page_preview=True)

    if not DISABLE_CHANNEL_BUTTON:
        await post_message.edit_reply_markup(reply_markup)
    try:
        await message.edit_reply_markup(reply_markup)
    except Exception as e:
        print(e)
        pass
