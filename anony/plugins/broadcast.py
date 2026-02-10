# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import os
import asyncio

from pyrogram import errors, filters, types

from anony import app, db, lang


@app.on_message(filters.command(["broadcast"]) & app.sudoers)
@lang.language()
async def _broadcast(_, message: types.Message):
    if not message.reply_to_message:
        return await message.reply_text(message.lang["gcast_usage"])

    msg = message.reply_to_message
    count, ucount = 0, 0
    groups, users = [], []
    sent = await message.reply_text(message.lang["gcast_start"])

    if "-nochat" not in message.command:
        groups.extend(await db.get_chats())
    if "-user" in message.command:
        users.extend(await db.get_users())
    await asyncio.sleep(5)

    failed = ""
    for chat in groups:
        try:
            (
                await msg.copy(chat, reply_markup=msg.reply_markup)
                if "-copy" in message.text
                else await msg.forward(chat)
            )
            count += 1
            await asyncio.sleep(0.1)
        except errors.FloodWait as fw:
            await asyncio.sleep(fw.value + 60)
        except Exception as ex:
            failed += f"{chat} - {ex}\n"
            continue
    await message.reply_text(f"Broadcated to {count} chats.")

    for chat in users:
        try:
            (
                await msg.copy(chat, reply_markup=msg.reply_markup)
                if "-copy" in message.text
                else await msg.forward(chat)
            )
            ucount += 1
            await asyncio.sleep(0.1)
        except errors.FloodWait as fw:
            await asyncio.sleep(fw.value + 60)
        except Exception as ex:
            failed += f"{chat} - {ex}\n"
            continue

    text = message.lang["gcast_end"].format(count, ucount)
    if failed:
        with open("errors.txt", "w") as f:
            f.write(failed)
        await message.reply_document(
            document="errors.txt",
            caption=text,
        )
        os.remove("errors.txt")
    try: await sent.delete()
    except: pass
    await message.reply_text(text)
