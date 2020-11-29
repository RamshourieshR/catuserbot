import io
import json
import math
import os
import re
import time
from userbot import bot as borg
from userbot import CMD_HELP,  client
from userbot.javes_main.heroku_var import Config
from telethon import Button, custom, events

from userbot import CMD_LIST
from userbot import tebot as tgbot

CAT_IMG = None
BTN_URL_REGEX = re.compile(r"(\[([^\[]+?)\]\<buttonurl:(?:/{0,2})(.+?)(:same)?\>)")


if Config.TG_BOT_USER_NAME_BF_HER is not None and tgbot is not None:

    @tgbot.on(events.InlineQuery)
    async def inline_handler(event):
        builder = event.builder
        global me
        me = await client.get_me()
        bot.uid=me.id
        result = None
        query = event.text
        hmm = re.compile("secret (.*) (.*)")
        match = re.findall(hmm, query)
        if event.query.user_id == bot.uid and query.startswith("secrete"):
            markdown_note = query[7:]
            prev = 0
            note_data = ""
            buttons = []
            for match in BTN_URL_REGEX.finditer(markdown_note):
                # Check if btnurl is escaped
                n_escapes = 0
                to_check = match.start(1) - 1
                while to_check > 0 and markdown_note[to_check] == "\\":
                    n_escapes += 1
                    to_check -= 1
                # if even, not escaped -> create button
                if n_escapes % 2 == 0:
                    # create a thruple with button label, url, and newline
                    # status
                    buttons.append(
                        (match.group(2), match.group(3), bool(match.group(4)))
                    )
                    note_data += markdown_note[prev : match.start(1)]
                    prev = match.end(1)
                # if odd, escaped -> move along
                else:
                    note_data += markdown_note[prev:to_check]
                    prev = match.start(1) - 1
            else:
                note_data += markdown_note[prev:]
            message_text = note_data.strip()
            tl_ib_buttons = ibuild_keyboard(buttons)
            result = builder.article(
                title="secrete",
                text=message_text,
                buttons=tl_ib_buttons,
                link_preview=False,
            )
            await event.answer([result] if result else None)
        elif event.query.user_id == bot.uid and match:
            query = query[7:]
            user, txct = query.split(" ", 1)
            builder = event.builder
            secret = os.path.join("./userbot", "secrets.txt")
            try:
                jsondata = json.load(open(secret))
            except:
                jsondata = False
            try:
                # if u is user id
                u = int(user)
                try:
                    u = await event.client.get_entity(u)
                    if u.username:
                        sandy = f"@{u.username}"
                    else:
                        sandy = f"[{u.first_name}](tg://user?id={u.id})"
                except ValueError:
                    # ValueError: Could not find the input entity
                    sandy = f"[user](tg://user?id={u})"
            except ValueError:
                # if u is username
                try:
                    u = await event.client.get_entity(user)
                except ValueError:
                    return
                if u.username:
                    sandy = f"@{u.username}"
                else:
                    sandy = f"[{u.first_name}](tg://user?id={u.id})"
                u = int(u.id)
            except:
                return
            timestamp = int(time.time() * 2)
            newsecret = {str(timestamp): {"userid": u, "text": txct}}

            buttons = [
                custom.Button.inline("show message 🔐", data=f"secret_{timestamp}")
            ]
            result = builder.article(
                title="secret",
                text=f"🔒 A whisper message to {sandy}, Only he/she can open it.",
                buttons=buttons,
            )
            await event.answer([result] if result else None)
            if jsondata:
                jsondata.update(newsecret)
                json.dump(jsondata, open(secret, "w"))
            else:
                json.dump(newsecret, open(secret, "w"))




    @tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"secret_(.*)")))
    async def on_plug_in_callback_query_handler(event):
        timestamp = int(event.pattern_match.group(1).decode("UTF-8"))
        if os.path.exists("./userbot/secrets.txt"):
            jsondata = json.load(open("./userbot/secrets.txt"))
            try:
                message = jsondata[f"{timestamp}"]
                userid = message["userid"]
                ids = [userid, bot.uid]
                if event.query.user_id in ids:
                    encrypted_tcxt = message["text"]
                    reply_pop_up_alert = encrypted_tcxt
                else:
                    reply_pop_up_alert = "why were you looking at this  go away and do your own work"
            except KeyError:
                reply_pop_up_alert = "This message no longer exists in bot server"
        else:
            reply_pop_up_alert = "This message no longer exists "
        await event.answer(reply_pop_up_alert, cache_time=0, alert=True)








def ibuild_keyboard(buttons):
    keyb = []
    for btn in buttons:
        if btn[2] and keyb:
            keyb[-1].append(Button.url(btn[0], btn[1]))
        else:
            keyb.append([Button.url(btn[0], btn[1])])
    return keyb
