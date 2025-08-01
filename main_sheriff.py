import discord
import os
from discord import app_commands
import dotenv
import time

dotenv.load_dotenv()



TOKEN = os.getenv("token")

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
    mm = []
    k = []
    x = -1
    y = -1
    # メッセージ送信者がボットの場合は無視する
    
    if message.content.startswith("Ajpam379vcoff"):
        for v in client.get_all_channels():
            #print(v.name)
            if isinstance(v,discord.VoiceChannel):
                ls.append(v.id) #vcチャンネルのチャンネルid

        for i in ls:
            x += 1
            ls_count = len(ls)
            channel = client.get_channel(ls[x])
            print(channel)
            await channel.connect()
            current_vc = discord.utils.get(client.voice_clients,guild=message.guild)
            time.sleep(1)
            vcmember = current_vc.channel.members
            for k in vcmember:
                ml.append(k)
            for member in vcmember:
                mm.append(member.id)
                y += 1
                guild = client.get_guild(1076105584329375765)#guild id
                h = guild.get_member(member.id)
                if h.bot == False:
                    print(h)
                    await h.move_to(channel=None,reason="配信が始まるため")
                    y += 1
                else:
                    y +=1
                    
                if len(ml) == x: #no
                    break
            await current_vc.disconnect()
            if ls_count == x:
                break
        await message.channel.send("任務完了")

client.run(TOKEN)
