import time
import humanize
import discord
from discord.ext import commands

class CoreCog(commands.Cog):
    def __init__(self):
        self.start = time.time()

    @commands.Cog.listener()
    async def on_message(self, message):
        timeout = discord.utils.find(lambda r: r.name == 'Timeout', message.guild.roles)
        if timeout in message.author.roles:
            if message.mentions:
                await message.channel.send(f'Sorry {message.author.mention}, you may not ping that user at this time.')
                await message.delete()

    @commands.command()
    async def hello(self, ctx):
        await ctx.send('I have initialized therefore I am.')

    @commands.command()
    async def uptime(self, ctx):
        elapsed = humanize.naturaldelta(time.time() - self.start)
        await ctx.send(f'My systems have been operative for {elapsed}')

    @commands.command()
    async def time(self, ctx):
        date = time.strftime('%A,%e %B %Y %H:%M:%S')
        await ctx.send(f'Current server time: {date}')
