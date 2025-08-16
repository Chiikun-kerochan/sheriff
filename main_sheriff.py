import discord
import os
from discord import app_commands
import dotenv
import time
from keep_alive import keep_alive
import asyncio
from typing import Literal
import aiohttp

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
            await asyncio.sleep(600)
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
                    except discord.HTTPException as e:
                        print(f"HTTPエラーが発生しました:{e} ")
        await message.channel.send("任務完了")

#読み上げ機能
async def read_text(text):
        VOICE_DIR = "voice_files"
        if not os.path.exists(VOICE_DIR):
            os.makedirs(VOICE_DIR)
        VOICEVOX_URL = "http://localhost:50021"
        voice_client = discord.utils.get(client.voice_clients, guild=client.get_guild(1076105584329375765))
        file_path = os.path.join(VOICE_DIR, "voicevox_voice.wav")
        try:
            async with aiohttp.ClientSession() as session:
                # 1. 音声合成クエリを取得
                params = {'text': text, 'speaker': 1}
                async with session.post(f'{VOICEVOX_URL}/audio_query', params=params) as response:
                    audio_query = await response.json()
            
                # 2. 音声合成を実行
                async with session.post(f'{VOICEVOX_URL}/synthesis', params={'speaker': 1}, json=audio_query) as response:
                    audio_data = await response.read()
        # 音声データをファイルに保存
            with open(file_path, "wb") as f:
                f.write(audio_data)
        # 再生
            if voice_client:
                ffmpeg_path = r"/usr/bin/ffmpeg"
                source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(file_path, executable=ffmpeg_path))
                voice_client.play(source)
                #voice_client.play(discord.FFmpegPCMAudio(file_path), after=lambda e: os.remove(file_path))　　#この書き方だと上手くいかない
        except Exception as e:
            await print(f'エラーが発生しました: {e}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    guild = message.guild
    zatsudan = client.get_channel(1076482232342020096)
    ph = guild.get_member(1018781055215468624)
    
    # ここで重い処理をバックグラウンドで開始
    if message.author == ph and message.channel == zatsudan and message.content == "はじめます":
        asyncio.create_task(hajime_process(guild, zatsudan, ph,  message))
    #読み上げbotの機能
    if guild.voice_client :
        voice_channel_members = guild.voice_client.channel.members
        # メッセージの投稿者がVCメンバーリストに含まれているかチェック
        if message.author in voice_channel_members:
            # ここにVC参加者からのメッセージを処理するコードを記述
            print(f"VC参加者からメッセージを受信: {message.content}")
            if message.guild.voice_client:
                asyncio.create_task(read_text(str(message.content)  ))

@client.event
async def on_voice_state_update(member, before, after): #自動退出機能
    # BotがVCにいて、メンバーがVCから退出したときにチェック
    if member.id != client.user.id and before.channel and client.user in before.channel.members:
        # 退出後のチャンネルに誰もいなければ退出
        if len(before.channel.members) == 1: # Bot自身しかいなくなった場合
            await before.channel.guild.voice_client.disconnect()


@tree.command(name="ping",description="ping値を測定")
async def pingchi(inter : discord.Interaction):
    raw_ping = client.latency
    ping = round(raw_ping * 1000)
    await inter.response.send_message(f"🏓{ping}ms")
    
@tree.command(name="join", description="vcに接続します")
async def join(interaction: discord.Interaction):
    if not interaction.user.voice:
        return await interaction.response.send_message('vcに入ってからコマンドを実行してください。', ephemeral=True)
    voice_channel = interaction.user.voice.channel
    await voice_channel.connect()
    await interaction.response.send_message(f"{voice_channel.name}に接続しました。")
    
@tree.command(name="leave", description="vcから切断します")
async def bye(interaction: discord.Interaction):
    voice_client = discord.utils.get(client.voice_clients, guild=interaction.guild)
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
        await interaction.response.send_message('vcから切断しました。')
    else:
        await interaction.response.send_message('vcに接続していません。', ephemeral=True)

@tree.command(name="invite_url",description="ふぁれんサーバーへの招待リンクを生成する")
async def invite_ph(inter:discord.Interaction):
    url = "https://discord.gg/mdyRcy8gWt"
    try:
        await inter.response.send_message(f"{url}")
    except discord.Forbidden:
        await inter.response.send_message("権限不足")
    except discord.HTTPException :
        await inter.response.send_message("HTTP error occurred:")

@tree.command(name="introduction_phalen" , description="ふぁれんが活動しているSNSを紹介します")
async def intro_ph(inter:discord.Interaction , mode:Literal["Youtube","X","Twitch","全て"]):
    twi_url = "https://twitter.com/ponko2ninja"
    Youtube_url = "https://youtube.com/channel/UC4BPiLhjSLozx2qWoR6yrhg?si=V62dclJo0PrxeOYZ"
    twitch_url = "https://www.twitch.tv/ponko2ninja"
    if mode == "Youtube":
        await inter.response.send_message(f"{Youtube_url}")
    elif mode =="Twitch":
        await inter.response.send_message(f"{twitch_url}")
    elif mode == "X":
        await inter.response.send_message(f"{twi_url}")
    elif mode =="全て":
        await inter.response.send_message(f"{Youtube_url} \n{twitch_url} \n{twi_url}")

keep_alive()
client.run(TOKEN)





























