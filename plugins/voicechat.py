
from pyrogram import filters
from pyrogram.enums import ChatType
from strings import get_string
from VIPMUSIC import app
from VIPMUSIC.utils import VIPbin

from VIPMUSIC.utils.database import get_assistant, get_lang
import asyncio
from os import getenv
from dotenv import load_dotenv
from pyrogram import Client
from dotenv import load_dotenv
import config

from VIPMUSIC.logging import LOGGER
from VIPMUSIC.utils.database import (
    delete_filter,
    get_cmode,
    get_lang,
    is_active_chat,
    is_commanddelete_on,
    is_maintenance,
    is_nonadmin_chat,
    set_loop,
)
from VIPMUSIC.core.call import VIP

from pyrogram import filters
from pyrogram.enums import ChatType
from strings import get_string
from VIPMUSIC import app
from VIPMUSIC.utils import VIPbin
from VIPMUSIC.utils.database import get_assistant, get_lang
from VIPMUSIC.core.mongo import mongodb
import asyncio

# Database collection for active VC monitoring
vc_monitoring = mongodb.vc_monitoring

# Function to store or check if a group has monitoring active
async def is_vc_monitoring_active(chat_id):
    return await vc_monitoring.find_one({"chat_id": chat_id})

async def set_vc_monitoring(chat_id, status):
    if status:
        await vc_monitoring.update_one(
            {"chat_id": chat_id}, {"$set": {"chat_id": chat_id}}, upsert=True
        )
    else:
        await vc_monitoring.delete_one({"chat_id": chat_id})

# Command to start monitoring
@app.on_message(filters.command("checkvcon") & filters.admin)
async def start_vc_monitoring(client, message):
    chat_id = message.chat.id
    language = await get_lang(chat_id)
    _ = get_string(language)
    
    # Check if monitoring is already active
    if await is_vc_monitoring_active(chat_id):
        await message.reply_text(_["V_C_MONITOR_ACTIVE"])
        return
    
    await set_vc_monitoring(chat_id, True)
    await message.reply_text(_["V_C_MONITOR_START"])
    await monitor_vc_members(client, chat_id)

# Function to stop monitoring
@app.on_message(filters.command("stopvcon") & filters.admin)
async def stop_vc_monitoring(client, message):
    chat_id = message.chat.id
    language = await get_lang(chat_id)
    _ = get_string(language)
    
    # Check if monitoring is active
    if not await is_vc_monitoring_active(chat_id):
        await message.reply_text(_["V_C_MONITOR_NOT_ACTIVE"])
        return
    
    await set_vc_monitoring(chat_id, False)
    await message.reply_text(_["V_C_MONITOR_STOP"])

# Main monitoring function
async def monitor_vc_members(client, chat_id):
    prev_members = set()

    while await is_vc_monitoring_active(chat_id):
        userbot = await get_assistant(chat_id)
        current_members = set()
        
        async for m in userbot.get_call_members(chat_id):
            if not m.is_left:  # Only consider active participants
                current_members.add(m.user.id)

        # Determine new joiners and leavers
        new_joiners = current_members - prev_members
        leavers = prev_members - current_members

        # Notify for new joiners
        for user_id in new_joiners:
            user = await client.get_users(user_id)
            await client.send_message(chat_id, f"{user.mention} has joined the voice chat.")

        # Notify for leavers
        for user_id in leavers:
            user = await client.get_users(user_id)
            await client.send_message(chat_id, f"{user.mention} has left the voice chat.")

        # Update the previous member list
        prev_members = current_members

        # Delay for 1 second before the next check
        await asyncio.sleep(1)














@app.on_message(
    filters.command(["vcuser", "vcusers", "vcmember", "vcmembers"]) & filters.admin
)
async def vc_members(client, message):
    try:
        language = await get_lang(message.chat.id)
        _ = get_string(language)
    except:
        _ = get_string("en")
    msg = await message.reply_text(_["V_C_1"])
    userbot = await get_assistant(message.chat.id)
    TEXT = ""
    try:
        async for m in userbot.get_call_members(message.chat.id):
            chat_id = m.chat.id
            username = m.chat.username
            is_hand_raised = m.is_hand_raised
            is_video_enabled = m.is_video_enabled
            is_left = m.is_left
            is_screen_sharing_enabled = m.is_screen_sharing_enabled
            is_muted = bool(m.is_muted and not m.can_self_unmute)
            is_speaking = not m.is_muted

            if m.chat.type != ChatType.PRIVATE:
                title = m.chat.title
            else:
                try:
                    title = (await client.get_users(chat_id)).mention
                except:
                    title = m.chat.first_name

            TEXT += _["V_C_2"].format(
                title,
                chat_id,
                username,
                is_video_enabled,
                is_screen_sharing_enabled,
                is_hand_raised,
                is_muted,
                is_speaking,
                is_left,
            )
            TEXT += "\n\n"
        if len(TEXT) < 4000:
            await msg.edit(TEXT or _["V_C_3"])
        else:
            link = await VIPbin(TEXT)
            await msg.edit(
                _["V_C_4"].format(link),
                disable_web_page_preview=True,
            )
    except ValueError as e:
        await msg.edit(_["V_C_5"])
from pyrogram import *
from pyrogram import filters
from pyrogram.types import *
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from VIPMUSIC import app



@app.on_message(filters.video_chat_members_invited)
async def brah3(app: app, message: Message):
    text = f"➻ {message.from_user.mention}\n\n**๏ ɪɴᴠɪᴛɪɴɢ ɪɴ ᴠᴄ ᴛᴏ :**\n\n**➻ **"
    x = 0
    for user in message.video_chat_members_invited.users:
        try:
            text += f"[{user.first_name}](tg://user?id={user.id}) "
            x += 1
        except Exception:
            pass

    try:
        add_link = f"https://t.me/{app.username}?startgroup=true"
        reply_text = f"{text} 🤭🤭"
        userbot = await get_assistant(message.chat.id)
        await message.reply(reply_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="๏ ᴊᴏɪɴ ᴠᴄ ๏", url=add_link)]]))
        
    except Exception as e:
        print(f"Error: {e}")


####


@app.on_message(filters.command("math", prefixes="/"))
def calculate_math(client, message):
    expression = message.text.split("/math ", 1)[1]
    try:
        result = eval(expression)
        response = f"ᴛʜᴇ ʀᴇsᴜʟᴛ ɪs : {result}"
    except:
        response = "ɪɴᴠᴀʟɪᴅ ᴇxᴘʀᴇssɪᴏɴ"
    message.reply(response)


@app.on_message(filters.command(["spg"], ["/", "!", "."]))
async def search(event):
    msg = await event.respond("Searching...")
    async with aiohttp.ClientSession() as session:
        start = 1
        async with session.get(
            f"https://content-customsearch.googleapis.com/customsearch/v1?cx=ec8db9e1f9e41e65e&q={event.text.split()[1]}&key=AIzaSyAa8yy0GdcGPHdtD083HiGGx_S0vMPScDM&start={start}",
            headers={"x-referer": "https://explorer.apis.google.com"},
        ) as r:
            response = await r.json()
            result = ""

            if not response.get("items"):
                return await msg.edit("No results found!")
            for item in response["items"]:
                title = item["title"]
                link = item["link"]
                if "/s" in item["link"]:
                    link = item["link"].replace("/s", "")
                elif re.search(r"\/\d", item["link"]):
                    link = re.sub(r"\/\d", "", item["link"])
                if "?" in link:
                    link = link.split("?")[0]
                if link in result:
                    # remove duplicates
                    continue
                result += f"{title}\n{link}\n\n"
            prev_and_next_btns = [
                Button.inline("▶️Next▶️", data=f"next {start+10} {event.text.split()[1]}")
            ]
            await msg.edit(result, link_preview=False, buttons=prev_and_next_btns)
            await session.close()




__MODULE__ = "Mᴀᴛʜ"
__HELP__ = """

## Mᴀᴛʜ Cᴏᴍᴍᴀɴᴅ Hᴇᴘ

### 1. /ᴍᴀᴛʜ [ᴇxᴘʀᴇssɪᴏɴ]
**Dᴇsᴄʀɪᴘᴛɪᴏɴ:**
Cᴀᴄᴜᴀᴛᴇs ᴛʜᴇ ʀᴇsᴜᴛ ᴏғ ᴀ ᴍᴀᴛʜᴇᴍᴀᴛɪᴄᴀ ᴇxᴘʀᴇssɪᴏɴ.

**Usᴀɢᴇ:**
/ᴍᴀᴛʜ [ᴇxᴘʀᴇssɪᴏɴ]

**Dᴇᴛᴀɪs:**
- Sᴜᴘᴘᴏʀᴛs ʙᴀsɪᴄ ᴀʀɪᴛʜᴍᴇᴛɪᴄ ᴏᴘᴇʀᴀᴛɪᴏɴs: ᴀᴅᴅɪᴛɪᴏɴ (+), sᴜʙᴛʀᴀᴄᴛɪᴏɴ (-), ᴍᴜᴛɪᴘɪᴄᴀᴛɪᴏɴ (*), ᴀɴᴅ ᴅɪᴠɪsɪᴏɴ (/).
- Rᴇᴛᴜʀɴs ᴛʜᴇ ʀᴇsᴜᴛ ᴏғ ᴛʜᴇ ᴇxᴘʀᴇssɪᴏɴ.
- Dɪsᴘᴀʏs "Iɴᴠᴀɪᴅ ᴇxᴘʀᴇssɪᴏɴ" ɪғ ᴛʜᴇ ᴇxᴘʀᴇssɪᴏɴ ɪs ɴᴏᴛ ᴠᴀɪᴅ.

## Gᴏᴏɢᴇ Sᴇᴀʀᴄʜ Cᴏᴍᴍᴀɴᴅ Hᴇᴘ

### 1. /sᴘɢ [ǫᴜᴇʀʏ]
**Dᴇsᴄʀɪᴘᴛɪᴏɴ:**
Sᴇᴀʀᴄʜᴇs Gᴏᴏɢᴇ ᴀɴᴅ ᴅɪsᴘᴀʏs sᴇᴀʀᴄʜ ʀᴇsᴜᴛs.

**Usᴀɢᴇ:**
/sᴘɢ [ǫᴜᴇʀʏ]

**Dᴇᴛᴀɪs:**
- Sᴇᴀʀᴄʜᴇs Gᴏᴏɢᴇ ғᴏʀ ᴛʜᴇ sᴘᴇᴄɪғɪᴇᴅ ǫᴜᴇʀʏ.
- Dɪsᴘᴀʏs sᴇᴀʀᴄʜ ʀᴇsᴜᴛs ᴡɪᴛʜ ᴛɪᴛᴇs ᴀɴᴅ ɪɴᴋs.
- Sᴜᴘᴘᴏʀᴛs ᴘᴀɢɪɴᴀᴛɪᴏɴ ᴡɪᴛʜ ɴᴇxᴛ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴠɪᴇᴡ ᴍᴏʀᴇ ʀᴇsᴜᴛs.
"""
