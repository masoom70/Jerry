# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import os

from pyrogram import filters, types

from anony import app, db, lang, queue


@app.on_message(filters.command(["ac", "activevc"]) & app.sudoers)
@lang.language()
async def _activevc(_, m: types.Message):
    if not db.active_calls:
        return await m.reply_text(m.lang["vc_empty"])

    if m.command[0] == "ac":
        return await m.reply_text(m.lang["vc_count"].format(len(db.active_calls)))

    sent = await m.reply_text(m.lang["vc_fetching"])
    text = ""

    for i, chat in enumerate(db.active_calls):
        playing = queue.get_current(chat)
        text += f"\n{i+1}. <code>{chat}</code>\n    ➜ {playing.title[:25]}"

    if len(text) < 4000:
        return await sent.edit_text(m.lang["vc_list"] + text)

    with open("activevc.txt", "w") as f:
        f.write(text)
    f.close()
    await sent.edit_media(
        media=types.InputMediaDocument(
            media="activevc.txt",
            caption=m.lang["vc_list"],
        )
    )
    os.remove("activevc.txt")


@app.on_message(filters.command(["autoleave"]) & app.sudoers)
async def _autoleave(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text("What?")
    
    mode = m.command[1]
    if mode not in ("enable", "disable"):
        return await m.reply_text("What?\n\nOnly <code>on</code> and <code>off</code> is accepted.")

    status = mode == "enable"
    await db.set_auto_leave(status)
    await m.reply_text(f"Auto leave status updated.\n\n<b>Auto Leave:</b> <code>{status}</code>")
