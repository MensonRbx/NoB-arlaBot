# INFORMATION:
# Name: No Béarla
# Date of creation: 09/06/2024

# Music for bot: "Towards The Horizon" by Alexander Nakarada
# https://www.youtube.com/watch?v=nFovhPQ_M_k

# This software is released into the public domain under CC0 1.0 Universal (CC0 1.0) Public Domain Dedication.
# You may use this software freely without any conditions or restrictions.
# For more information, see https://creativecommons.org/publicdomain/zero/1.0/

# Tír gan teanga, tír gan anam.

from datetime import datetime
import random
import asyncio
import discord

from discord import FFmpegPCMAudio, PCMVolumeTransformer
from discord.ext import tasks
from discord.ext.commands import Bot

from tokens import bot_token as TOKEN

background_music_path = 'Music\\background_music.mp3'

TARGET_USERNAMES = ['cacamilis', '__menson', 'mr.jones4954', 'staunchy2.0', 'goodoleagle', '_mrapples_', 'l0chlainn']
TARGET_NUMBER_FOR_VC_JOIN = 1 # for random number part
MINIMUM_MEMBERS_IN_VC = 2

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = Bot(command_prefix='!', intents=intents)

active_channels_map = {}

# ServerBotHandler
# Handler for actions for bot to perform in a server
# 
# bot: Bot - the bot object
# guild_id: int - the id of the guild

# start(self): None - concurrent method

class ServerVoiceChannelBotHandler:
    def __init__(self, bot, channel, guild):
        self.bot = bot
        self.channel = channel
        self.guild = guild
        self.started = False
        
        self._lastDayTime = datetime.now().day
        self._hasJoinedToday = False

        asyncio.create_task(self._set_has_joined_today_async())

    async def _set_has_joined_today_async(self):
        while True:
            if self._lastDayTime != datetime.now().day and self._hasJoinedToday:
                self._hasJoinedToday = False
                self._lastDayTime = datetime.now().day
                asyncio.create_task(self.start())
            await asyncio.sleep(10)

    async def start(self):
        self.started = True
        print(f'Checking {self.channel.name} in {self.guild.name}')
        while not self._hasJoinedToday:
            await asyncio.sleep(5)
            no_of_whitelisted_members = len(await self.get_members_in_vc())
            print(f'No of whitelisted members: {no_of_whitelisted_members}')
            while no_of_whitelisted_members >= MINIMUM_MEMBERS_IN_VC:
                random_number = random.randint(1, 100)                  
                print(f'Random number: {random_number}, Target number: {TARGET_NUMBER_FOR_VC_JOIN}')
                if random_number == TARGET_NUMBER_FOR_VC_JOIN:
                    self._hasJoinedToday = True
                    await self.joinVC()
                    break
                else:
                    await asyncio.sleep(5)

    async def get_members_in_vc(self):
        members = self.channel.members
        arrayOfWhitelistedMembers = [member for member in members if member.name in TARGET_USERNAMES]
        return arrayOfWhitelistedMembers

    async def joinVC(self):
        self._hasJoinedToday = True

        vc = await self.channel.connect()
        print(f'Joined {self.channel.name} in {self.guild.name}')

        background_music = FFmpegPCMAudio(background_music_path)
        background_music = PCMVolumeTransformer(background_music, volume=0.1)
        vc.play(background_music)
        
        await asyncio.sleep(60) 
        await vc.disconnect()
        print(f'Left {self.channel.name} in {self.guild.name}')

@tasks.loop(hours=24)
async def daily_join():
    for guild in bot.guilds:
        for channel in guild.channels:
            if not isinstance(channel, discord.VoiceChannel):
                continue
            if not active_channels_map.get(channel.id):
                voice_channel_handler = ServerVoiceChannelBotHandler(bot, channel, guild)
                active_channels_map[channel.id] = voice_channel_handler
                asyncio.create_task(voice_channel_handler.start())
            # await handleVoiceChannel(guild, channel)

@daily_join.before_loop
async def before_daily_join():
    await bot.wait_until_ready()

@bot.command(name='anois')
async def now(ctx):
    author_name = ctx.author.name
    if author_name != "__menson":
        return
    print(f'Command received from {ctx.author.name} in {ctx.guild.name}')
    channel_id = ctx.author.voice.channel.id
    voice_channel_handler = active_channels_map.get(channel_id)
    if not voice_channel_handler:
        voice_channel_handler = ServerVoiceChannelBotHandler(bot, ctx.author.voice.channel, ctx.guild)
        active_channels_map[channel_id] = voice_channel_handler
        asyncio.create_task(voice_channel_handler.start())    
    await voice_channel_handler.joinVC()

@bot.event
async def on_ready():
    daily_join.start()

bot.run(TOKEN)
