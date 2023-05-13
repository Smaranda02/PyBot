#to do 
#hosting, music, quiz, quote time


import os
import discord
from dotenv import load_dotenv
from nextcord.ext import commands,tasks
from dataclasses import dataclass
import youtube_dl
import aiohttp  #for gpt
import asyncio  #for music
import time
import schedule 
import pyjokes
import random
import datetime
import requests
import json
from gtts import gTTS
import nextcord
import pyowm #wrapper for weather api




intents = nextcord.Intents.all()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
#CHANNEL=os.getenv('CHANNEL_ID')
CHANNEL=1102597234832453816
API_KEY=os.getenv('API_KEY')
api_key_weather=os.getenv('WEATHER_API_KEY')


voice_clients={}

yt_dl_opts={'format':'bestaudio/best'}
ytdl=youtube_dl.YoutubeDL(yt_dl_opts)


ffmpeg_options={'options':"-vn"}


#setting variables 
client = nextcord.Client(intents=intents)
bot=commands.Bot(command_prefix="!",intents=intents)

channel=bot.get_channel(CHANNEL)

utc=datetime.timezone.utc
time=datetime.time(hour=22, minute = 12, tzinfo=utc)



#owm = pyowm.OWM('4b096846dea87214c945bf7a0158fe48')




@bot.command()
async def weather(context, city_name): 
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    city=city_name
    complete_url = base_url + "appid=" + api_key_weather + "&q=" + city
    response=requests.get(complete_url)
    res=response.json()
    info=res["main"]

    if response.status_code!=200:
        await context.send("Invalid city name. Try again!")

    else:
        await context.send(f'''Temperature in Celsius in {city_name} is : { int(info['temp']-273) }
                        How the temperature actually feels like : { int(info['feels_like']-273)}
                        Short description of the weather : { res['weather'][0]['description']}
                        Pressure : { info['pressure']}\nHumidity : { info['humidity']}
                        ''')






@bot.command()
async def tts(context, *args):
    text=" ".join(args)
    user=context.message.author
    if user.voice!= None:
        try:
            vc= await user.voice.channel.connect()
        except: 
            vc=context.voice_client

        sound=gTTS(text=text,lang="en", slow=False)
        sound.save("tts-audio.mp3")

        if vc.is_playing():
            vc.stop()

        source=await nextcord.FFmpegOpusAudio.from_probe("tts-audio.mp3", method="fallback")
        vc.play(source)
    
    else:
        await context.send("You need to be in a vc to run the command")





@bot.event
async def quote_of_the_day():
        @tasks.loop(seconds=2)
        async def quote():
            response = requests.get ("https://zenquotes.io/api/random")
            json_data = json.loads(response.text)
            quote = json_data[0]['q'] + " -" + json_data[0]['a']
            await channel.send(quote)


@bot.event
async def on_member_join(member):
    channel=bot.get_channel(CHANNEL)
    await channel.send(f"{member.mention} has joined the server")
    

@bot.event
async def on_member_remove(member):
    channel=bot.get_channel(CHANNEL)
    await channel.send(f"{member.mention} has left the server")


@bot.event
async def on_member_remove(member):
    channel=bot.get_channel(CHANNEL)
    await channel.send(f"{member.mention} has left the server")
        
        

@bot.command()
async def joke(context):
    await context.send(pyjokes.get_joke())


#to do write time in hours or minutes or minutes
#tip comanda !remind "time" "task"
@bot.command()
async def remind(context, time:int, *, msg):

    channel=bot.get_channel(CHANNEL)

    await context.send(f"Okay, I will remind you in {time} minutes.")
    await asyncio.sleep(time*60)
    author=context.author
    await channel.send(f"Reminder: {msg} {author.mention}")



@bot.command()
async def play(msg):
    
    try :
        url=msg

        voice_client=await msg.author.voice.channel.connect()
        voice_clients[voice_client.guild.id]=voice_client

        loop=asyncio.get_event_loop()
        data= await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

        song=data['url']
        #player=discord.FFmpegPCMAudio(song,**ffmpeg_options, executable="/wsl.localhost/Ubuntu/home/smara/DiscordBot/ffmpeg/bin/ffmpeg.exe")
        player=discord.FFmpegPCMAudio(song,**ffmpeg_options, executable="C:\\Users\\smara\\Desktop\\ffmpeg\\bin\\ffmpeg.exe")
        #player=discord.FFmpegPCMAudio(song,**ffmpeg_options)
        voice_client.play(player)
    except Exception as err:
        print(err)


@bot.command()
async def gpt(context:commands.Context, *, prompt: str):
    
    await context.send("Loading response from ChatGPT...")
    
    async with aiohttp.ClientSession() as session:
        payload ={
            "model": "text-davinci-003",
            "prompt": prompt,
            "temperature" : 0.5,
            "max_tokens" : 200,
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "best_of":1
        } 

        headers={"Authorization": f"Bearer {API_KEY}"}

        async with session.post("https://api.openai.com/v1/completions", json=payload , headers=headers) as resp:
            response = await resp.json()
            embed =nextcord.Embed(title="Chat GPT'S Response ", description=response["choices"][0]["text"])
            await context.reply(embed=embed)


@bot.event
async def on_ready():
    print(f' HELLO TO Discord!')
    channel=bot.get_channel(CHANNEL)
    await channel.send("Hello! Project Bot is ready")


@bot.command()
async def hello(context):
    await context.send("Hello!")


@bot.command()
async def add(context,*arr):
    sum=0
    for i in arr:
        sum+=i
    await context.send(f"Sum: {sum}")


bot.run(TOKEN)

print(client.guilds)

