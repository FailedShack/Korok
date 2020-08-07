import re
import io
import json
import textwrap
import time

import requests
import discord
from discord.ext import commands

class DebugCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_check = 0
        with open('ntstatus.json', 'r') as f:
            self.ntstatus = json.load(f)
        self.latest = None
        self.channel = None

    def ensure_ready(self):
        if (time.time() - self.last_check) > 3600:
            r = requests.get('https://api.github.com/repos/FailedShack/USBHelperLauncher/releases/latest')
            self.latest = r.json()['tag_name']

    async def process_message(self, message, filename, log):
        self.ensure_ready()
        arch = 32 if '32-bit' in log else 64
        version = re.findall('^Version: (.*)$', log, re.MULTILINE)[0].rstrip()
        v_cmp = version
        if len(v_cmp) == 3:
            v_cmp = '0.0' + v_cmp[2:]
 
        lines = iter(log.splitlines())
        try:
            while True:
                line = next(lines)
                exit_code = re.findall('code (0x[a-f0-9]{8}):$', line)
                if exit_code:
                    exit_code = exit_code[0]
                    break
        except StopIteration:
            exit_code = '0x00000000'

        more = ''
        exit_status = None
        if exit_code in self.ntstatus:
            nt = self.ntstatus[exit_code]
            exit_status = nt['code']
            more = f'''\n>>> **MSDN says:**\n{nt['description']}'''
        elif exit_code == '0xe0434352': # CLR Exception
            exit_status = 'CLR_EXCEPTION'
            exception = next(lines).split(': ', 1)[1]
            exception = exception.split(' ---> ')[-1] # Most inner exception
            more = f'\n>>> **Unhandled Exception:**\n{exception}'

        if exit_status:
            more = f' ({exit_status}){more}'

        if 'wiiu.titlekeys.gq ->' in log:
            await message.channel.send(f'Remove `hosts.json` from your installation folder.')

        if v_cmp < '0.14':
            notlikethis = discord.utils.find(lambda e: e.name == 'notlikethis', message.guild.emojis)
            await message.channel.send(textwrap.dedent(f'''
            Wow! It looks like that belongs in a museum, {message.author.mention}! {notlikethis}
            Your USBHelperLauncher is really out of date.
            Please update to the latest version ({self.latest}). You can get it from:
            https://github.com/FailedShack/USBHelperLauncher/releases/latest'''))
        elif v_cmp < self.latest:
            await message.channel.send(textwrap.dedent(f'''
            It looks like your USBHelperLauncher version is out of date.
            Please update to the latest version ({self.latest}). You can get it from:
            https://github.com/FailedShack/USBHelperLauncher/releases/latest'''))

        fp = io.BytesIO(log.encode('utf-8'))
        file = discord.File(fp, filename=filename)
        embed = discord.Embed(description=textwrap.dedent(f'''
        Version: {version}
        Architecture: {arch}-bit
        Exit Code: {exit_code}''') + more)
        embed.set_author(name=f'{message.author.name}', url=message.jump_url)
        embed.set_thumbnail(url=f'https://cdn.discordapp.com/avatars/{message.author.id}/{message.author.avatar}.png?size=1024')
        embed.set_footer(text=f'Debug message in #{message.channel.name}')
        embed.colour = ~int(exit_code, 16) % 0xffffff
        await self.channel.send(embed=embed, file=file)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        haste = re.findall(r'hastebin\.com\/([a-z]{10})', message.content.lower())
        for hid in haste:
            url = f'https://hastebin.com/raw/{hid}'
            r = requests.get(url)
            r.raise_for_status()
            await self.process_message(message, f'usbhelperlauncher_{hid}.log', r.text)

        logs = re.findall(r'api\.nul\.sh\/logs\/(.{12})', message.content)
        for log in logs:
            url = f'https://api.nul.sh/logs/{log}'
            r = requests.get(url)
            r.raise_for_status()
            await self.process_message(message, f'usbhelperlauncher_{log}.log', r.text)

        for attach in message.attachments:
            if attach.filename.endswith('.log'):
                debug = (await attach.read()).decode('utf-8')
                if 'Made by FailedShack' in debug:
                    await self.process_message(message, attach.filename, debug)

    @commands.Cog.listener()
    async def on_ready(self):
        guild = discord.utils.get(self.bot.guilds, name='Wii U USB Helper Launcher')
        self.channel = discord.utils.find(lambda c: c.name == 'bot-spam', guild.text_channels)
