import re
import random

from discord.ext import commands

def build_regex(script):
    lines = script.splitlines()
    regex = lines[-1]
    for assignment in lines[:-1]:
        k, v = assignment.split('=', 2)
        regex = regex.replace('${{{var}}}'.format(var=k), v)
    return re.compile(regex)

class HelpfulCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_event = dict()
        with open('keys.txt', 'r') as f:
            self.script = f.read()
        self.keys = build_regex(self.script)
        self.good_bot = [
            'Thank you! Buh-bye!',
            'Buh-thank you! :blush:',
            '*happy robotic noises*'
        ]
        self.thank_you = [
            'No worries. Now go, traveler. For you must defeat Calamity Ganon.',
            'My pleasure. Now go, traveler. Hyrule\'s fate rests upon you.',
            'No problem. Buh-bye!',
            'No worries. Buh-bye!',
            'You are welcome. Buh-bye!',
            'It is my pleasure.'
        ]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        before = await message.channel.history(limit=1, before=message).next()
        if not 'titlekeys.ovh' in message.content.lower() and re.search(self.keys, message.content):
            msg = await message.channel.send('Yahaha! You found me!\nUse this: **titlekeys.ovh**')
            self.last_event[message.channel.id] = msg.id
        elif before.id == self.last_event.get(message.channel.id, None):
            if re.search(r'(?i)g[uo0]+d\s+b[o0]t', message.content):
                await message.channel.send(random.choice(self.good_bot))
            elif re.search(r'(?i)(?:thanks|thank\s+you)', message.content):
                await message.channel.send(random.choice(self.thank_you))
            elif re.search(r'(?i)l[uo0]+ve?\s+y[o0]+u', message.content):
                await message.channel.send(':flushed:')

    @commands.group()
    async def triggers(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send(f'{ctx.prefix}triggers options: view, update, save')

    @triggers.command()
    @commands.has_permissions(manage_messages=True)
    async def view(self, ctx):
        await ctx.send(f'```{self.script}```')

    @triggers.command()
    @commands.has_permissions(manage_messages=True)
    async def update(self, ctx, *, script):
        self.script = script
        self.keys = build_regex(self.script)
        await ctx.message.add_reaction('\u2705')

    @triggers.command()
    @commands.has_permissions(manage_messages=True)
    async def save(self, ctx):
        with open('keys.txt', 'w') as f:
            f.write(self.script)
        await ctx.message.add_reaction('\u2705')
