import re
from pymongo import MongoClient
from pyrogram import filters
from pyrogram.types import Message
from anony import app
import os
from anony import config
from anony.helpers.pastebin import JaiBsdkBin
import asyncio
from pyrogram.errors import FloodWait
import gc
from datetime import datetime


MONGO_DB_URI = os.getenv("MONGO_URL")

SYSTEM_DBS = ["admin", "local", "config","sample_mflix"]

@app.on_message(filters.command("mongochk"))
async def mongo_check_command(client, message: Message):
    if len(message.command) < 2:
        await message.reply("Please provide your MongoDB URL with the command: <code>/mongochk your_mongo_url</code>")
        return
    ok = await message.reply_text("Please wait i am checking your mongo...")
    mongo_url = message.command[1]
    try:
        mongo_client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        databases = mongo_client.list_database_names()
        result = f"MongoDB URL <code>{mongo_url}</code> is valid.\n\nAvailable Databases:\n"
        for db_name in databases:
            if db_name not in ["admin", "local"]:
                result += f"\n<code>{db_name}</code>:\n"
                db = mongo_client[db_name]
                for col_name in db.list_collection_names():
                    result += f"<code>{col_name}</code> (<code>{db[col_name].count_documents({})}</code> documents)\n"
        if len(result) > 4096:
            paste_url = await JaiBsdkBin(result)
            await ok.delete()
            await message.reply(f"The database list is too long to send here. You can view it at: {paste_url}")
        else:
            await ok.delete()
            result += f"\nᴍᴏɴɢᴏᴅʙ ᴅᴀᴛᴀʙᴀꜱᴇ ʙʏ : @AMBOTYT"
            await message.reply(result)
        mongo_client.close()

    except Exception as AbhiModszYT:
        await message.reply(f"Failed to connect to MongoDB\n\nYour Mongodb is dead❌\n\nError:- <code>{AbhiModszYT}</code>")
def delete_collection(client, db_name, col_name):
    db = client[db_name]
    db.drop_collection(col_name)
def delete_database(client, db_name):
    client.drop_database(db_name)
def list_databases_and_collections(client):
    numbered_list = []
    counter = 1
    for db_name in client.list_database_names():
        if db_name not in ["admin", "local"]:  
            numbered_list.append((counter, db_name, None))
            counter += 1
            db = client[db_name]
            for col_name in db.list_collection_names():
                numbered_list.append((counter, db_name, col_name))
                counter += 1
    return numbered_list

@app.on_message(filters.command(["deletedb", "deletedatabase", "deldb", "deldatabase"]) & app.sudoers)
async def delete_db_command(client, message: Message):
    try:
        mongo_client = MongoClient(MONGO_DB_URI, serverSelectionTimeoutMS=5000)
        databases_and_collections = list_databases_and_collections(mongo_client)
        if len(message.command) == 1:
            if len(databases_and_collections) > 0:
                result = "MongoDB Databases and Collections given below you can delete by /deldb 1,2,7,5 (your choice you can delete multiple databse in one command with multiple count value seperated by comma:\n\n"
                for num, db_name, col_name in databases_and_collections:
                    if col_name:
                        result += f"<code>{num}</code>.) <code>{col_name}</code>\n"
                    else:
                        result += f"\n<code>{num}</code>.) <code>{db_name}</code> (Database)\n"
                result += f"\nᴍᴏɴɢᴏᴅʙ ᴅᴀᴛᴀʙᴀꜱᴇ ʙʏ : @AMBOTYT"
                ok = await message.reply(result)
            else:
                await message.reply("No user databases found. ❌")
        elif "," in message.command[1]:
            numbers = message.command[1].split(",")
            failed = []
            for num_str in numbers:
                num_str = num_str.strip()  
                if num_str.isdigit():
                    number = int(num_str)
                    if number > 0 and number <= len(databases_and_collections):
                        num, db_name, col_name = databases_and_collections[number - 1]
                        try:
                            if col_name:
                                delete_collection(mongo_client, db_name, col_name)
                                await message.reply(f"Collection <code>{col_name}</code> in database <code>{db_name}</code> has been deleted successfully. 🧹\n\nCheck Rest databse by: /checkdb, /deldb")
                                await ok.delete()
                            else:
                                delete_database(mongo_client, db_name)
                                await message.reply(f"Database <code>{db_name}</code> has been deleted successfully. 🧹\n\nCheck Rest databse by: /checkdb, /deldb")
                                await ok.delete()
                        except Exception as AbhiModszYT:
                            failed.append(num_str)
                    else:
                        failed.append(num_str)
                else:
                    failed.append(num_str)
            if failed:
                await message.reply(f"Some entries could not be deleted or were invalid: {', '.join(failed)} ❌\n\nCheck Rest databse by: /checkdb, /deldb")
        elif message.command[1].isdigit():
            number = int(message.command[1])
            if number > 0 and number <= len(databases_and_collections):
                num, db_name, col_name = databases_and_collections[number - 1]
                if col_name:
                    delete_collection(mongo_client, db_name, col_name)
                    await message.reply(f"Collection <code>{col_name}</code> in database <code>{db_name}</code> has been deleted successfully. 🧹\n\nCheck Rest databse by: /checkdb, /deldb")
                else:
                    delete_database(mongo_client, db_name)
                    await message.reply(f"Database <code>{db_name}</code> has been deleted successfully. 🧹\n\nCheck Rest databse by: /checkdb, /deldb")
            else:
                await message.reply("Invalid number. Please check the list again.")
        else:
            db_name = message.command[1]
            if len(message.command) == 3:
                col_name = message.command[2]
                if db_name in [db[1] for db in databases_and_collections if not db[2]]:
                    delete_collection(mongo_client, db_name, col_name)
                    await message.reply(f"Collection <code>{col_name}</code> in database <code>{db_name}</code> has been deleted successfully. 🧹\n\nCheck Rest databse by: /checkdb, /deldb")
                else:
                    await message.reply(f"Database <code>{db_name}</code> does not exist. ❌")
            else:
                if db_name in [db[1] for db in databases_and_collections if not db[2]]:
                    delete_database(mongo_client, db_name)
                    await message.reply(f"Database <code>{db_name}</code> has been deleted successfully. 🧹\n\nCheck Rest databse by: /checkdb, /deldb")
                else:
                    await message.reply(f"Database <code>{db_name}</code> does not exist. ❌")
        mongo_client.close()
    except Exception as AbhiModszYT:
        await message.reply(f"Failed to delete databases Try to delete by count")

MONGO_DB_URI = os.getenv("MONGO_URL")

@app.on_message(filters.command(["checkdb", "checkdatabase"]) & app.sudoers)
async def check_db_command(client, message: Message):
    try:
        ok = await message.reply_text("Please wait while checking your bot mongodb database...")
        mongo_client = MongoClient(MONGO_DB_URI, serverSelectionTimeoutMS=5000)
        databases = mongo_client.list_database_names()
        if len(databases) > 2:
            result = "MongoDB Databases:\n"
            for db_name in databases:
                if db_name not in ["admin", "local"]:
                    result += f"\n<code>{db_name}</code>:\n"
                    db = mongo_client[db_name]
                    for col_name in db.list_collection_names():
                        collection = db[col_name]
                        result += f"<code>{col_name}</code> (<code>{collection.count_documents({})}</code> documents)\n"
                        
            
            if len(result) > 4096: 
                paste_url = await JaiBsdkBin(result)
                await message.reply(f"The database list is too long to send here. You can view it at: {paste_url}")
                await ok.delete()
            else:
                await ok.delete()
                result += f"\nᴍᴏɴɢᴏᴅʙ ᴅᴀᴛᴀʙᴀꜱᴇ ʙʏ : @AMBOTYT"
                await message.reply(result)
        else:
            await ok.delete()
            await message.reply("No user databases found. ❌")
        mongo_client.close()

    except Exception as AbhiModszYT:
        await ok.delete()
        await message.reply(f"Failed to check databases: code>{AbhiModszYT}</code>")
mongo_url_pattern = re.compile(r"mongodb(?:\+srv)?:\/\/[^\s]+")

def backup_old_mongo_data(old_client):
    backup_data = {}
    AbhiModsz = ['local', 'admin', 'config','sample_mflix']  
    for db_name in old_client.list_database_names():
        if db_name in AbhiModsz:
            continue
        db = old_client[db_name]
        backup_data[db_name] = {}
        for col_name in db.list_collection_names():
            collection = db[col_name]
            backup_data[db_name][col_name] = list(collection.find())  
    return backup_data


def restore_data_to_new_mongo(new_client, backup_data):
    for db_name, collections in backup_data.items():
        db = new_client[db_name]
        for col_name, documents in collections.items():
            collection = db[col_name]
            if documents:
                try:
                    collection.insert_many(documents, ordered=False)
                except Exception as e:
                    print(f"Error while inserting data into {db_name}.{col_name}: {str(e)}")


MONGO_DB_URI = os.getenv("MONGO_URL")
@app.on_message(filters.command(["transferdb", "copydb", "paste", "copydatabase", "transferdatabase"]) & app.sudoers)
async def transfer_db_command(client, message: Message):
    try:
        if len(message.command) == 2:
            main_mongo_url = MONGO_DB_URI
            target_mongo_url = message.command[1]
        elif len(message.command) == 3:
            main_mongo_url = message.command[1]
            target_mongo_url = message.command[2]
        else:
            await message.reply("Please provide one or two MongoDB URLs as required.")
            return

        if not re.match(mongo_url_pattern, target_mongo_url):
            await message.reply("The target MongoDB URL format is invalid! ❌")
            return
        main_client = MongoClient(main_mongo_url, serverSelectionTimeoutMS=5000)
        backup_data = backup_old_mongo_data(main_client)
        main_client.close()
        target_client = MongoClient(target_mongo_url, serverSelectionTimeoutMS=5000)
        restore_data_to_new_mongo(target_client, backup_data)
        target_client.close()
        await message.reply("Data transfer to the new MongoDB is successful! 🎉")
    except Exception as AbhiModszYT:
        await message.reply(f"Data transfer failed: code>{AbhiModszYT}</code>")
        
import json
import io

MONGO_DB_URI = os.getenv("MONGO_URL")

@app.on_message(filters.command("downloaddata"))
async def download_data_command(client, message: Message):
    try:
        mongo_url = message.command[1]
        mongo_client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        data = {}
        for db_name in mongo_client.list_database_names():
            if db_name not in ["local", "admin", "config","sample_mflix"] :
                data[db_name] = {}
                db = mongo_client[db_name]
                for col_name in db.list_collection_names():
                    data[db_name][col_name] = list(db[col_name].find())
        mongo_client.close()
        json_data = json.dumps(data, default=str, indent=2)
        file = io.BytesIO(json_data.encode('utf-8'))
        file.name = "ambot.json"
        AMBOTFIRE = f"ᴍᴏɴɢᴏᴅʙ ᴅᴀᴛᴀʙᴀꜱᴇ ʙᴀᴄᴋᴜᴘ ʙʏ : @AMBOTYT"
        await client.send_document(chat_id=message.chat.id, document=file, caption=AMBOTFIRE)
    except Exception as AbhiModszYT:
        await message.reply(f"Failed to download data: <code>{AbhiModszYT}</code>")

@app.on_message(filters.command("reupload") & app.sudoers)
async def download_data_command(client, message: Message):
    am = await message.reply("Hmmmm............") 
    try:
        mongo_url = message.command[1]
        mongo_url2 = message.command[2]
        await am.edit("ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴏɴ ʏᴏᴜʀ ᴍᴀɪɴ ᴍᴏɴɢᴏᴅʙ...")
        mongo_client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        await am.edit("ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴏɴ ʏᴏᴜʀ ᴍᴀɪɴ ᴍᴏɴɢᴏᴅʙ ✅\nᴄᴏᴍᴘʟᴇᴛᴇ ᴍᴏɴɢᴏᴅʙ ᴅᴀᴛᴀʙᴀꜱᴇ ʙʏ : @AMBOTYT")
        await asyncio.sleep(3)
        await am.edit("ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴏɴ ʏᴏᴜʀ ɴᴇᴡ ᴍᴏɴɢᴏᴅʙ....")
        mongo_client2 = MongoClient(mongo_url2, serverSelectionTimeoutMS=5000)
        await am.edit("ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴏɴ ʏᴏᴜʀ ɴᴇᴡ ᴍᴏɴɢᴏᴅʙ ✅\nᴄᴏᴍᴘʟᴇᴛᴇ ᴍᴏɴɢᴏᴅʙ ᴅᴀᴛᴀʙᴀꜱᴇ ʙʏ : @AMBOTYT")
        await asyncio.sleep(3)
        await am.edit("ꜱᴛᴀʀᴛᴇᴅ ᴛᴏ ʙᴀᴄᴋ-ᴜᴘ ᴍᴀɪɴ ᴍᴏɴɢᴏ....\nɪᴛ'ꜱ ᴛᴀᴋᴇ ᴛɪᴍᴇ ʙᴀꜱᴇ ᴏɴ ʏᴏᴜʀ ᴅᴀᴛᴀ ꜱᴛᴏʀᴀɢᴇ ꜱɪᴢᴇ\n\nᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ.....")
        data = {}
        for db_name in mongo_client.list_database_names():
            if db_name not in ["local", "admin", "config","sample_mflix"]:
                data[db_name] = {}
                db = mongo_client[db_name]
                for col_name in db.list_collection_names():
                    data[db_name][col_name] = list(db[col_name].find())
        mongo_client.close()
        await am.edit("ʙᴀᴄᴋ-ᴜᴘ ᴄᴏᴍᴘʟᴇᴛᴇ ᴏɴ ᴍᴀɪɴ ᴍᴏɴɢᴏ ✅\nᴄᴏᴍᴘʟᴇᴛᴇ ᴍᴏɴɢᴏᴅʙ ᴅᴀᴛᴀʙᴀꜱᴇ ʙʏ : @AMBOTYT")
        json_data = json.dumps(data, default=str, indent=2)
        backup_data = io.BytesIO(json_data.encode('utf-8'))
        backup_data.name = "ambot.json"
        await am.edit("ʙᴀᴄᴋ-ᴜᴘ ꜰɪʟᴇ ʀᴇᴜᴘʟᴏᴀᴅɪɴɢ ᴏɴ ɴᴇᴡ ᴍᴏɴɢᴏ...\nɪᴛ'ꜱ ᴛᴀᴋᴇ ᴛɪᴍᴇ ʙᴀꜱᴇ ᴏɴ ʏᴏᴜʀ ᴅᴀᴛᴀ ꜱᴛᴏʀᴀɢᴇ ꜱɪᴢᴇ\n\nᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ.....")
        backup_data.seek(0)
        data_to_restore = json.load(backup_data)
        await restore_data_to_new_mongo(mongo_client2, data_to_restore)
        mongo_client2.close()
        backup_data.close()
        del backup_data
        gc.collect()
        await am.edit("ʙᴀᴄᴋ-ᴜᴘ ꜰɪʟᴇ ʀᴇᴜᴘʟᴏᴀᴅɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇ ᴏɴ ɴᴇᴡ ᴍᴏɴɢᴏ ᴡᴀɪᴛ ᴄʜᴇᴄᴋᴋɪɴɢ ᴅʙ ʟᴏᴀᴅ ꜱᴜᴘᴘᴏʀᴛ ✅\nᴄᴏᴍᴘʟᴇᴛᴇ ᴍᴏɴɢᴏᴅʙ ᴅᴀᴛᴀʙᴀꜱᴇ ʙʏ : @AMBOTYT")
    except Exception as AbhiModszYT:
        pass
    await am.edit("ᴡɪᴛʜᴏᴜᴛ ᴀɴʏ ᴘʀᴏʙʟᴇᴍ ʀᴇᴜᴘʟᴏᴀᴅ ᴛᴀꜱᴋ ᴄᴏᴍᴘʟᴇᴛᴇ ✅\nᴄᴏᴍᴘʟᴇᴛᴇ ᴍᴏɴɢᴏᴅʙ ᴅᴀᴛᴀʙᴀꜱᴇ ʙʏ : @AMBOTYT")


MONGO_DB_URI = os.getenv("MONGO_URL")

@app.on_message(filters.command("upload"))
async def download_data_command(client, message: Message):
    am = await message.reply("Hmmmm............") 
    try:
        if not message.reply_to_message or not message.reply_to_message.document:
            await am.edit("ᴘʟꜱ ʀᴇᴘʟʏ ᴛᴏ ᴊꜱᴏɴ ꜰɪʟᴇ ꜰᴏʀ ᴜᴘʟᴏᴀᴅ ᴅᴀᴛᴀʙᴀꜱᴇ ᴜꜱᴇ ʟɪᴋᴇ : /ᴜᴘʟᴏᴀᴅ ʀᴇᴘʟʏ_ᴊꜱᴏɴ_ꜰɪʟᴇ ᴍᴏɴɢᴏ_ᴅʙ...")
            return
        mongo_url = message.command[1] 
        replyfile = message.reply_to_message.document
        file_name = replyfile.file_name
        file_id = replyfile.file_id
        if not file_name.endswith(".json"):
            await am.edit("ᴏɴʟʏ .ᴊꜱᴏɴ ꜰɪʟᴇꜱ ᴀʀᴇ ꜱᴜᴘᴘᴏʀᴛᴇᴅ.")
            return
        download_path = os.path.join("mongodb", file_name)
        await am.edit("ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴛʜᴇ ꜰɪʟᴇ ᴡᴀɪᴛ....\nɪᴛ'ꜱ ᴛᴀᴋᴇ ᴛɪᴍᴇ ʙᴀꜱᴇ ᴏɴ ʏᴏᴜʀ ᴅᴀᴛᴀ ꜱᴛᴏʀᴀɢᴇ ꜱɪᴢᴇ\n\nᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ.....") 
        backup_data = await client.download_media(file_id, download_path)
        await am.edit("ꜰɪʟᴇ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ. ᴡᴀɪᴛ ꜰᴏʀ ᴜᴘʟᴏᴀᴅ ᴅᴀᴛᴀ...") 
        target_client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        with open(backup_data, 'r') as file:
            data = json.load(file)
        restore_data_to_new_mongo(target_client, data)
        target_client.close()
        await am.edit("ꜰɪʟᴇ ᴅᴀᴛᴀ ʜᴀꜱ ʙᴇᴇɴ ᴘʀᴏᴄᴇꜱꜱᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ✅.\nᴛᴀꜱᴋ ᴄᴏᴍᴘʟᴇᴛᴇ ᴍᴏɴɢᴏᴅʙ ᴅᴀᴛᴀʙᴀꜱᴇ ʙʏ : @AMBOTYT")
    except Exception as AbhiModszYT:
        await am.edit(f"ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ: {str(AbhiModszYT)}")


@app.on_message(filters.command(["rm", "rmdb"]) & app.sudoers)
async def delete_db_command(client, message: Message):
    try:
        if len(message.command) < 2:
            return await message.reply(
                "Usage:\n"
                "<code>/rm MONGO_URL</code>\n"
                "<code>/rmdb MONGO_URL 1,2</code>\n"
                "<code>/rm MONGO_URL all</code>"
            )
        mongo_url = message.command[1]
        mongo_client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        db_list = [db for db in mongo_client.list_database_names() if db not in SYSTEM_DBS]
        if not db_list:
            mongo_client.close()
            return await message.reply("No databases found ❌")
        if len(message.command) >= 3 and message.command[2].lower() in ["all", "force"]:
            for db_name in db_list:
                mongo_client.drop_database(db_name)

            mongo_client.close()
            return await message.reply("🔥 All databases deleted successfully.")
        if len(message.command) == 2:
            text = "MongoDB Databases:\n\n"
            for i, db_name in enumerate(db_list, start=1):
                text += f"<code>{i}</code>.) <code>{db_name}</code>\n"

            text += "\nDelete using:\n<code>/deldb MONGO_URL 1,2</code>\n"
            text += "Force delete all:\n<code>/deldb MONGO_URL all</code>"

            mongo_client.close()
            return await message.reply(text)
        numbers = message.command[2].split(",")
        failed = []

        for num_str in numbers:
            num_str = num_str.strip()

            if not num_str.isdigit():
                failed.append(num_str)
                continue

            index = int(num_str) - 1

            if index < 0 or index >= len(db_list):
                failed.append(num_str)
                continue

            try:
                mongo_client.drop_database(db_list[index])
            except:
                failed.append(num_str)

        mongo_client.close()

        if failed:
            await message.reply(f"Some entries failed: {', '.join(failed)} ❌")
        else:
            await message.reply("🧹 Selected databases deleted successfully.")

    except Exception as e:
        await message.reply(f"Mongo Connection Failed ❌\n\nError: <code>{e}</code>")
        
        
        
@app.on_message(filters.command(["mongo", "mongodb"], prefixes=["/", "!"]))
async def rulses(client, message: Message):
    RULSE = f"""ʜᴇʏ,
MongoDB Management  ᴄᴏᴍᴍᴀɴᴅ :

• /deletedb : You can delete by /deletedb 1,2,7,5.

• /deletedb [database_name] [collection_name]: Deletes the specified collection within the database.

• /deletedb all: Deletes all user databases.

• /checkdb: Lists all databases and collections with the number of documents in the MongoDB.

• MongoDB Transfer Commands:

• /transferdb [new_mongo_url]: - Transfers all databases from the old MongoDB (from environment) to the new MongoDB URL.

• /downloaddata - Download your all data from database in a document file.

• /mongochk [MongoDB_URL]: Verifies the given MongoDB URL and lists all databases and collections in it.

• /upload : Upload json file in new database use like : /upload reply_to_json_file MONGODB_URL

• /reupload : rebackup mongo direct mongo to mongo data back-up use like : /reupload Main_MONGO NEW_MONGO

• Users Cmds : /reupload  /upload /mongochk /downloaddata
"""
    await message.delete()
    await message.reply(RULSE)
