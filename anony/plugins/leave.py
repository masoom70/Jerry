# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import asyncio
from pyrogram import enums, filters, types

from anony import app, db, userbot


@app.on_message(filters.command(["leaveall"]) & filters.user(app.owner))
async def _leaveall(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text("Which assistant?")
    
    try:
        num = int(m.command[1])
    except ValueError:
        return await m.reply_text("Invalid number")

    left, failed = 0, 0
    sent = await m.reply_text("Leaving all chats...")
    asses = {
        1: userbot.one,
        2: userbot.two,
        3: userbot.three,
    }

    for dialog in await asses[num].get_dialogs():
        chat = dialog.chat
        if chat.type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            continue
        if chat.id in [app.logger, -1001686672798, -1001549206010]:
            continue
        if chat.id in db.active_calls:
            continue

        try:
            await asses[num].leave_chat(chat.id)
            await asyncio.sleep(3)
            left += 1
        except:
            failed += 1
            continue

    await sent.edit_text(f"Left {left} chats.\nFailed to leave {failed} chats.")
