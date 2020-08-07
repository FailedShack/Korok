import sqlite3
import time

import bs4
import requests
import discord
from discord.ext import commands, tasks
from urllib.parse import urljoin

import marker

class CrowdinCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = {'project_id': '380351'}
        self.headers = {
            'Cookie': 'csrf_token=pjbguha48j',
            'X-Csrf-Token': 'pjbguha48j'
        }
        self.db = sqlite3.connect('crowdin.db')
        self.db.execute('CREATE TABLE IF NOT EXISTS history (activity INTEGER PRIMARY KEY, message INTEGER, timestamp INTEGER)')

    async def update(self, force=False):
        r = requests.get('https://crowdin.com/backend/project_actions/activity_stream', params=self.data, headers=self.headers, timeout=5)
        activities = r.json()['activity']
        for activity in activities[::-1]:
            activity_id = int(activity['id'])
            timestamp = activity['timestamp']
            message = activity['message']
            event = activity['type']

            # Process only new activities
            if timestamp < self.start and not force:
                continue

            # Create the embed
            date = activity['datetime']
            soup = bs4.BeautifulSoup(message, features='lxml')
            profile = soup.select_one('a.user-link')
            embed = discord.Embed(description=marker.read(message, href='https://crowdin.com/', rules={'span': lambda node, text: f'**{text}**'}))
            embed.set_author(name=profile.text, url=urljoin('https://crowdin.com/', profile['href']), icon_url=activity['avatar'])
            embed.set_footer(text=f'Published on {date}')
            if event == 'build_project':
                embed.colour = 0xd4ebf5

            # Check if we should update an existing message
            cur = self.db.cursor()
            cur.execute('SELECT message, timestamp FROM history WHERE activity = ? LIMIT 1', (activity_id,))
            rows = cur.fetchone()
            if rows:
                if force:
                    continue
                prev_message, prev_timestamp = rows
                if timestamp != prev_timestamp:
                    if event == 'build_project':
                        message = await self.channel.send(embed=embed)
                        self.db.execute('UPDATE history SET message = ?, timestamp = ? WHERE activity = ?', (message.id, timestamp, activity_id))
                    else:
                        embed.set_footer(text=f'Updated on {date}')
                        message = await self.channel.fetch_message(prev_message)
                        await message.edit(embed=embed)
                        self.db.execute('UPDATE history SET timestamp = ? WHERE activity = ?', (timestamp, activity_id))
                    self.db.commit()
                continue

            # Send a new meessage
            message = await self.channel.send(embed=embed)
            self.db.execute('INSERT INTO history VALUES (?, ?, ?)', (activity_id, message.id, timestamp))
            self.db.commit()

    @commands.Cog.listener()
    async def on_ready(self):
        guild = discord.utils.get(self.bot.guilds, name='Wii U USB Helper Launcher')
        self.channel = discord.utils.find(lambda c: c.name == 'crowdin', guild.text_channels)
        self.update_task.start()
        self.start = int(time.time())

    @commands.command(name='forcecrowdin')
    @commands.has_permissions(manage_messages=True)
    async def force_update(self, ctx):
        await self.update(force=True)
        await ctx.message.add_reaction('\u2705')

    @tasks.loop(seconds=20.0)
    async def update_task(self):
        await self.update()
