import io
import json
import datetime
import collections
import pickle

import matplotlib.pyplot as plt
import discord
from discord.ext import commands, tasks

class PieConfig():
    def __init__(self):
        self.age_restriction = None
        self.close = None
        self.choices = list()

class PieCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            with open('votes.json', 'r') as f:
                self.votes = json.load(f)
        except FileNotFoundError:
            self.votes = dict()
        try:
            with open('pie.bin', 'rb') as f:
                self.config = pickle.load(f)
        except FileNotFoundError:
            self.config = PieConfig()

    async def send_pie(self, ctx):
        def labels(pct, total):
            absolute = int(round(pct/100*total))
            return f'{pct:.2f}%\n({absolute} votes)' if absolute else None
        cmap = plt.get_cmap("tab10")
        colors = cmap(range(len(self.config.choices)))
        freqs = collections.Counter(self.votes.values())
        freqs = [freqs.get(x, 0) for x in self.config.choices]
        total = sum(freqs)
        wedges, texts, autotexts = plt.pie(freqs, colors=colors, autopct=lambda pct: labels(pct, total))
        plt.legend(wedges, self.config.choices, loc='best')
        plt.axis('equal')
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, transparent=True)
        plt.clf()
        buf.seek(0)
        await ctx.send('Vote with `.vote <entry>`\nAll entries: <https://imgur.com/a/dYiJ8tc>',
                        file=discord.File(buf, filename='pie.png'))

    @commands.command()
    async def pie(self, ctx):
        await self.send_pie(ctx)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def choices(self, ctx, choices):
        self.config.choices = choices.split(',')
        with open('pie.bin', 'wb') as f:
            pickle.dump(self.config, f)
        await ctx.message.add_reaction('\u2705')

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def restrict(self, ctx, date):
        if date == 'clear':
            self.config.age_restriction = None
        else:
            self.config.age_restriction = datetime.datetime.fromisoformat(date)
        with open('pie.bin', 'wb') as f:
            pickle.dump(self.config, f)
        await ctx.message.add_reaction('\u2705')

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def close(self, ctx, date):
        if date == 'clear':
            self.config.close = None
        else:
            self.config.close = datetime.datetime.fromisoformat(date)
        with open('pie.bin', 'wb') as f:
            pickle.dump(self.config, f)
        await ctx.message.add_reaction('\u2705')

    @commands.command()
    async def vote(self, ctx, option):
        if self.config.close and datetime.datetime.now() > self.config.close:
            return
        if self.config.age_restriction and ctx.author.created_at > self.config.age_restriction:
            await ctx.send(f'Sorry {ctx.author.mention}, your Discord account is too recent.')
            return
        if option not in self.config.choices:
            await ctx.message.add_reaction('\u2753')
            return

        self.votes[str(ctx.author.id)] = option
        with open('votes.json', 'w') as f:
            json.dump(self.votes, f)
        await self.send_pie(ctx)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def whovoted(self, ctx):
        message = f'{len(self.votes)} total votes'
        for user_id, vote in self.votes.items():
            user = await self.bot.fetch_user(user_id)
            message += f'\n{user.name}: {vote}'
        await ctx.send(message)
