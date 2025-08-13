import discord
import os
from discord import app_commands
import dotenv
import time
from keep_alive import keep_alive
import asyncio
dotenv.load_dotenv()



TOKEN = os.getenv("token")
aikotoba = os.getenv("aikotoba")

intents = discord.Intents.all()#適当に。
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
@client.event
async def on_message(message):
    guild = message.guild
    zatsudan = client.get_channel(1076482232342020096)
    ph = guild.get_member(951411435370582016) #ふぁれんのユーザーid=1018781055215468624
    pr_ch = client.get_channel(1292500305992224869)
    t = 0
    members_in_vc = []
    if message.author == ph and message.channel == zatsudan:
        if  message.content == "はじめます":
            print("スタート")
            for i in range(1):
                await asyncio.sleep(60)
                t += 1
                await pr_ch.send(f"{t}分経過")
            for channel in client.get_all_channels():
                if isinstance(channel,discord.VoiceChannel) and channel.members: #vcか確認
                    members_in_vc.extend(channel.members)
            for w in members_in_vc:
                if w.bot == False:
                    try:
                        await w.move_to(channel=None,reason="配信が始まるため")
                    except discord.Forbidden:
                        print(f"権限が不足しているため移動できませんでした。")
                    except discord.HTTPException as e:
                        print(f"HTTPエラーが発生しました: {e}")
        await message.channel.send("任務完了")

keep_alive()
client.run(TOKEN)










