import discord
import os
from discord import app_commands
import dotenv
import time
from keep_alive import keep_alive
import asyncio
dotenv.load_dotenv()



TOKEN = os.getenv("token")

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
intents.message_content = True
intents.messages = True
intents.members = True
intents.voice_states = True
intents.guilds = True


# ボットの起動時の処理
@client.event
async def on_ready():
    print('ログインしました')

# メッセージ受信時の処理
async def hajime_process(guild, zatsudan, ph, message):
    members_in_vc = []
    if message.author == ph and message.channel == zatsudan:
        if  message.content == "はじめます":
            print("スタート")
            await asyncio.sleep(60)
            #await pr_ch.send(f"{t}分経過")
            for channel in client.get_all_channels():
                if isinstance(channel,discord.VoiceChannel) and channel.members: #vcか確認
                    members_in_vc.extend(channel.members)
            for w in members_in_vc:
                if w.bot == False:
                    try:
                        await w.move_to(channel=None,reason="配信が始まるため")
                        await asyncio.sleep(0.5)
                    except discord.Forbidden:
                        print(f"権限が不足しているため移動できませんでした。")
                    except discord.HTTPException:
                        print(f"HTTPエラーが発生しました: ")
        await message.channel.send("任務完了")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    guild = message.guild
    zatsudan = client.get_channel(1076482232342020096)
    ph = guild.get_member(951411435370582016)
    #pr_ch = client.get_channel(1292500305992224869)
    
    # ここで重い処理をバックグラウンドで開始
    if message.author == ph and message.channel == zatsudan and message.content == "はじめます":
        asyncio.create_task(heavy_process(guild, zatsudan, ph,  message))

keep_alive()
client.run(TOKEN)





















