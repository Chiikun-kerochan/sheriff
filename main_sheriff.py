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
    ls = []
    ml = []
    if message.content == aikotoba:
        current_vc = discord.utils.get(client.voice_clients,guild=message.guild)
        for v in client.get_all_channels():
            if isinstance(v,discord.VoiceChannel): #vcか確認
                ls.append(v.id) #vcチャンネルのチャンネルid
        for i in range(0,len(ls)):
            channel = client.get_channel(ls[i])
            print(channel)
            await channel.connect()
            for k in channel.members:
                if k is not None:
                    ml.append(k)  ##20250806追加
            await current_vc.disconnect()
        for w in range(0,len(ml)):
            guild = client.get_guild(1076105584329375765)#guild id
            h = guild.get_member(ml[w].id)
            if h.bot == False:
                print(h)
                await h.move_to(channel=None,reason="配信が始まるため")
        await message.channel.send("任務完了")

@client.event
async def on_message(message):
    guild = client.get_guild(1076105584329375765) 
    zatsudan = client.get_channel(1076482232342020096)
    ph = guild.get_member(1018781055215468624) #ふぁれんのユーザーid
    pr_ch = client.get_channel(1292500305992224869)
    t = 0
    if message.author == ph and message.channel == zatsudan:
        if  message.content == "はじめます":
            channel = client.get_channel(1324766308062986280) #botチャンネル
            
            print("スタート")
            for i in range(10):
                await asyncio.sleep(60)
                t += 1
                await pr_ch.send(f"ふぁれんが開始を宣言してから{t}分経過")
            await channel.send(aikotoba)

keep_alive()
client.run(TOKEN)





