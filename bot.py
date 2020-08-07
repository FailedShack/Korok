#!/usr/bin/env python3
import discord
from discord.ext import commands

import secret
from cogs import core, crowdin, debug, fun, helpful, pie, reaction

client = commands.Bot(command_prefix='.')
client.add_cog(core.CoreCog())
client.add_cog(crowdin.CrowdinCog(client))
client.add_cog(debug.DebugCog(client))
client.add_cog(fun.FunCog(client))
client.add_cog(helpful.HelpfulCog(client))
client.add_cog(pie.PieCog(client))
client.add_cog(reaction.ReactionCog())

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name='hide and seek'))
    guild = discord.utils.get(client.guilds, name='Wii U USB Helper Launcher')
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

client.run(secret.TOKEN)
