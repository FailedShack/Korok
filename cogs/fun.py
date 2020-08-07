import random
import time
import re

import asyncio
import discord
from discord.ext import commands

import lyrics

class FunCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.engaged = dict()
        self.opinions = [
            'Reply hazy, try again',
            'Not very good',
            'Somewhat decent',
            'Really think I got one?',
        ]
        self.last_song = None

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.mention_everyone and self.bot.user.mentioned_in(message):
            pingthink = discord.utils.find(lambda e: e.name == 'pingthink', message.guild.emojis)
            await message.add_reaction(pingthink)
            return

        def message_contains(*words):
            return all(re.search(f'\\b{w}\\b', message.content.lower()) for w in words)

        author = message.author.id
        if 'korok' in message.content.lower():
            self.engaged[author] = time.time()
        if author in self.engaged:
            if time.time() - self.engaged[author] > 10:
                del self.engaged[author]

            if message_contains('what', 'gender'):
                await message.channel.send(':flushed:')
            elif message_contains('what', 'opinion'):
                await message.channel.send(random.choice(self.opinions))
            elif message_contains('fuck', 'you'):
                await message.channel.send(':heart:')
            elif message_contains('love', 'you'):
                await message.channel.send(':blush:')
            elif (message_contains('more') or message_contains('go', 'on')) and self.last_song:
                await self.sing(message.channel, self.last_song)
                self.engaged[author] = time.time()
            elif re.findall('(?:who|what|where|when|why).+you', message.content.lower()):
                await message.channel.send('Shut up')

    @commands.command()
    async def bruh(self, ctx):
        await ctx.send('Bruhhh :angry: :angry: :angry:')

    @commands.command()
    async def bully(self, ctx):
        await ctx.send('https://i.imgur.com/lLqxbaR.jpg')

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def say(self, ctx, channel: discord.TextChannel, *, text):
        await channel.send(text)

    async def sing(self, channel, song):
        energy = 3
        while song and energy:
            verse = song.pop(0)
            if len(verse) > 5:
                verse = f':musical_note: {verse} :musical_note:'
                energy -= 1
            await channel.send(verse)
            async with channel.typing():
                await asyncio.sleep(1)
        self.last_song = song

    @commands.command()
    async def lyrics(self, ctx, *, query=None):
        if not query:
            await ctx.channel.send(f'{ctx.prefix}lyrics [<source>:] <keywords>')
            await ctx.channel.send('Available sources: ' + ', '.join(lyrics.SOURCES))
            return
        source = re.findall('^(.+?):', query.lower())
        if source:
            song = lyrics.find(query.split(':')[1], source=source[0])
        else:
            song = lyrics.find(query)
        if not song:
            await ctx.message.add_reaction('\u2753')
            return
        await self.sing(ctx.channel, song)
        self.engaged[ctx.message.author.id] = time.time()
