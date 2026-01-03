import discord
import os
from discord import app_commands
import dotenv
import time
from keep_alive import keep_alive
import asyncio
from typing import Literal
import aiohttp
from google import genai
from apiclient import discovery
from httplib2 import Http
from oauth2client import service_account
from googleapiclient.errors import HttpError
import datetime
import schedule
import threading

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
async def on_member_join(member):
    welcome_channel_id = 1076105585428267101  
    channel = client.get_channel(welcome_channel_id)
    if channel:
        await channel.send(f'{member.mention}さん、{member.guild.name}へようこそ！\nサーバー規約を読んでからゆっくりしていってね')

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

@tree.command(name= "mokkori_ai" ,description="もっこりすが質問をgeminiに丸投げします")
async def m_ai(interaction:discord.Interaction, text : str):
    await interaction.response.defer()
    clie = genai.Client(api_key=os.environ["API_KEY"])
    responce = clie.models.generate_content(model="gemini-2.0-flash",contents=text)
    # APIを利用
    await interaction.followup.send(f"あなたの質問 : {text}\n回答 : {responce.text}")

def get_poll_gf(form_ID:str):
    SCOPES = "https://www.googleapis.com/auth/forms.responses.readonly"
    DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

# JSONキーファイルの名前
    SERVICE_ACCOUNT_FILE = 'phalen-discord-bot-29a372261478.json' 
# 💡 認証情報をファイルから直接ロード（ブラウザ不要）
    creds = service_account.ServiceAccountCredentials.from_json_keyfile_name(
        SERVICE_ACCOUNT_FILE, 
        scopes=SCOPES
    )
    service = discovery.build(
        "forms",
        "v1",
        # ロードした認証情報をhttpオブジェクトに適用
        http=creds.authorize(Http()),
        discoveryServiceUrl=DISCOVERY_DOC,
        static_discovery=False,
    )
    # Prints the responses:
    
    form_id =  form_ID   #"1g0HaDgmvyABvrYFYVGSdUmUMPWPRWq9MEijXGSxzcAE"
    # フォームの回答一覧を取得
    result = service.forms().responses().list(formId=form_id).execute()


    ordict = {}
    ordict.update(result)
    res_opt = []
    for i in range(len(ordict['responses'])):  #解答者数を長さとして指定
        new_dict = ordict['responses'][i]["answers"]
        key_view = list(new_dict.keys()) #質問IDをリスト化
        #print(f"{i+1}人目の解答")
        for k in range(len(key_view)):   #質問数を指定
            c = new_dict[f"{key_view[k]}"]["textAnswers"]["answers"]
            len_opt = len(c)
            for j in range(len(c)):
                res_opt.append(c[j]["value"])

    return res_opt

@tree.command(name="poll_viewer",description="formはGoogleFormのid、pollにそのメッセージIDを")
async def povw(interaction: discord.Interaction,form_id : str, poll1 : str, poll2 : str = None ): #tetで日時
    await interaction.response.defer(thinking=True)
    channel = interaction.channel
    mess = await channel.fetch_message(int(poll1))
    mess_counter = len(mess.poll.answers)
    
    
    if mess.poll:
        pl_opt = []
        pl_count = []
        for i in range(1,mess_counter + 1):
            pl_opt.append(mess.poll.get_answer(id=i).text) #選択肢の名前
            pl_count.append(mess.poll.get_answer(id=i).vote_count) #その選択肢に投票された数
        
        desc = "DiscordアンケートとGoogle Formを合わせた集計"
        emb = discord.Embed(title="アンケート集計結果",description=desc,type="rich",color=0xff9300)

        discord.PollAnswer.text
        if mess.poll.is_finalized  :
            vict_ans_count = max(pl_count) #discordの最多票
            vict_ans_index = pl_count.index(max(pl_count))
            vict_ans_opt = pl_opt[vict_ans_index] #discord最多票の選択肢
            emb.add_field(name="質問1の結果",value="以下のようになりました",inline=False)

            for k in range(len(pl_opt)):
                gf_count = get_poll_gf(form_ID=form_id)
                gfl = gf_count.count(f"{pl_opt[k]}") #その項目のGoogle Formでの選択数
                rtco = gfl + pl_count[k]
                emb.add_field(name=pl_opt[k],value= f"{rtco}票 ({pl_count[k]}+{gfl})",inline=False)
            await interaction.followup.send(embed=emb)
        else:
            await interaction.response.send_message("poll has not been finalized")

    else:
        await interaction.response.send_message("this is not a poll")

    if poll2 is not None:
        channel = interaction.channel
        mess = await channel.fetch_message(int(poll2))
        mess_counter = len(mess.poll.answers)
    
    
        if mess.poll:
            pl_opt = []
            pl_count = []
            for i in range(1,mess_counter + 1):
                pl_opt.append(mess.poll.get_answer(id=i).text) #選択肢の名前
                pl_count.append(mess.poll.get_answer(id=i).vote_count) #その選択肢に投票された数
        
            desc = "DiscordアンケートとGoogle Formを合わせた集計"
            emb = discord.Embed(title="アンケート集計結果",description=desc,type="rich",color=0xFF0000)

            discord.PollAnswer.text
            if mess.poll.is_finalized :
                vict_ans_count = max(pl_count) #discordの最多票
                vict_ans_index = pl_count.index(max(pl_count))
                vict_ans_opt = pl_opt[vict_ans_index] #discord最多票の選択肢

                emb.add_field(name="質問2の結果",value="以下のようになりました",inline=False)
                for k in range(len(pl_opt)):
                    gf_count = get_poll_gf(form_ID=form_id)
                    o2o = gf_count.count(f"{pl_opt[k]}") #その項目のGoogle Formでの選択数
                    gfl2 = pl_count[k] + o2o
                    emb.add_field(name=pl_opt[k],value= f"{gfl2}票 ({pl_count[k]}+{o2o})",inline=False)
                await interaction.followup.send(embed=emb)

def makegf(cont:list ,itemID,formIDs,ind,checkbox:str):
    SCOPES = "https://www.googleapis.com/auth/forms.body"
    DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"
    SERVICE_ACCOUNT_FILE = 'phalen-discord-bot-29a372261478.json'
    #store = file.Storage("token.json")
    creds = service_account.ServiceAccountCredentials.from_json_keyfile_name(
            SERVICE_ACCOUNT_FILE, 
            scopes=SCOPES)

    form_service = discovery.build(
        "forms",
        "v1",
        http=creds.authorize(Http()),
        discoveryServiceUrl=DISCOVERY_DOC,
        static_discovery=False,
    )


# Request body to add a multiple-choice question
    item_id = itemID #checkboxは便宜上そうした。RADIOなどを入れられる。
    NEW_QUESTION = {
        "requests": [
            {
                "updateItem": {
                    "item": {
                        "itemId": item_id,
                        "questionItem": {
                            "question": {
                                "required": True,
                                "choiceQuestion": {
                                    "type": checkbox,
                                    "options": [

                                    ]
                                    ,
                                    "shuffle": False,
                                },
                            }
                        },
                    },
                    "location": {"index": ind},
                    "updateMask": "questionItem"
                }
            
            }
        ]
    }
    NEW_QUESTION["requests"][0]["updateItem"]["item"]["questionItem"]["question"]["choiceQuestion"]["options"].append(cont)

    form_id = formIDs
    try:
        form_service.forms().batchUpdate(formId=form_id, body=NEW_QUESTION).execute()
        print(f"\n✅ 成功: アイテムID '{item_id}' の選択肢を変更しました。")
        
    except HttpError as e:
            print(f"❌ 更新エラー: {e}")



@tree.command(name="make_google_form",description="質問に対応したGoogleフォームを作成。when:日時,what：内容に対応したメッセージのidを入力してください")
async def mkgf(inter:discord.Interaction, password:str, when:str, what:str ):
    await inter.response.defer(thinking=True)
    channel = inter.channel
    mess = await channel.fetch_message(int(when))
    mess_counter = len(mess.poll.answers)
    
    channelB = inter.channel
    messB = await channelB.fetch_message(int(what))
    mess_counterB = len(messB.poll.answers)
    pl_opt = []
    value1 = []
    pl_optB = []
    value1B = []
    if mess.poll and password == "abi": #日時だけのとき
        for i in range(1,mess_counter+1 ):
            pl_opt.append(mess.poll.get_answer(id=i).text) #選択肢の名前 
            value = {}    
            value["value"] = pl_opt[i-1]
            value1.append(value)
        try:
            print(value1)
            makegf(cont=value1,itemID="4e7a81f9",formIDs="1g0HaDgmvyABvrYFYVGSdUmUMPWPRWq9MEijXGSxzcAE",ind=1,checkbox="CHECKBOX")#両方あるフォーム
        except HttpError as e :
            await inter.followup.send(content= f"{e}")
    if  messB.poll and password == "a" :
        for k in range(1,mess_counterB+1 ):
            pl_optB.append(messB.poll.get_answer(id=k).text) #選択肢の名前 
            valueB = {}    
            valueB["value"] = pl_optB[k-1]
            value1B.append(valueB)  
        try:    
            print(value1B)
            makegf(cont=value1B,itemID="38bef855",formIDs="1g0HaDgmvyABvrYFYVGSdUmUMPWPRWq9MEijXGSxzcAE",ind=2,checkbox="CHECKBOX")#下の段の質問
            await inter.followup.send(content= "https://docs.google.com/forms/d/e/1FAIpQLScPeI6gnYC3_1I8lwQkzuNbdCHuVuAyL7iz6YuMjNkA4vljsw/viewform?usp=header")
        except HttpError as e:
            print(f"{e}")

@tree.command(name="make_gf_date",description="質問に対応したGoogleフォームを作成。when:日時に対応したメッセージのidを入力してください")
async def mkgf_date(inter:discord.Interaction, password:str, when:str):
    await inter.response.defer(thinking=True)
    channel = inter.channel
    mess = await channel.fetch_message(int(when))
    mess_counter = len(mess.poll.answers)
    pl_opt = []
    value1 = []
    if mess.poll and password == "a": #日時だけのとき
        for i in range(1,mess_counter+1 ):
            pl_opt.append(mess.poll.get_answer(id=i).text) #選択肢の名前 
            value = {}    
            value["value"] = pl_opt[i-1]
            value1.append(value)
        try:
            print(value1)
            makegf(cont=value1,itemID="71923339",formIDs="1VnRjoBxYO85j_Kp1D_Ck71qumGMgJRKwk8nIlp-vSM0",ind=1,checkbox="RADIO")
            await inter.followup.send(content= "https://forms.gle/8K1Vf4RFwmVqQHb37")
        except HttpError as e :
            await inter.followup.send(content= f"{e}")




async def send_msg(mes,channel_id:int): # メッセージを送れる汎用関数
    try:
        channel = client.get_channel(channel_id)
        if channel :
            await channel.send(content=f"{mes}")
            print("メッセージを送信しました")
        else:
            print("channel is not found.")
    except Exception as e:
        print(f"exception error : {e}")

async def job(msg, channel_id):
    now = datetime.datetime.now()
    print(str(now) + " 通知した")
    await send_msg(msg, channel_id)

def schedule_job(msg, weekdays, channel_id):
    now = datetime.datetime.now()
    if now.weekday() in weekdays:
        client.loop.call_soon_threadsafe(asyncio.create_task,job(msg,channel_id))

# スケジュール設定 ここの部分で個別に設定していく
channel_id = 1456890395970768951
cont = "https://media.discordapp.net/attachments/1160135713480785921/1181510300034400339/140_20231205171931.png?ex=695979f6&is=69582876&hm=8b9f8c771b598fc1abde8c89f036e629633bacc69cb13e80a169b5b7a659095f&=&format=webp&quality=lossless"
Use = client.get_channel(channel_id)

schedule.every().day.at("21:30").do(lambda: schedule_job(f"{cont}\n 21:30です。配信の調子はいかがでしょうか。 <@1018781055215468624>", [1,2,4,5,6], channel_id))  
schedule.every().day.at("21:45").do(lambda: schedule_job(f"{cont}\n 21:45です。そろそろ10時です。 <@1018781055215468624>", [1,2,4,5,6], channel_id))
schedule.every().day.at("22:00").do(lambda: schedule_job(f"{cont}\n 22:00です。配信の時刻としては理想的でしょう。 <@1018781055215468624>", [1,2,4,5,6], channel_id))  # 

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(60) # 60秒に一度判定を行う

schedule_thread = threading.Thread(target=run_schedule)
schedule_thread.start()


keep_alive()
client.run(TOKEN)
