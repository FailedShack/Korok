import string
from discord.ext import commands

def to_emoji(text):
    other = {
        '!!': '\u203C', '!?': '\u2049', '?': '\u2753', '!': '\u2757', 'tm': '\u2122',
        'cool': '\U0001F192', 'free': '\U0001F193', 'new': '\U0001F195', 'ok': '\U0001F197',
        'ab': '\U0001F18E', 'cl': '\U0001F191', 'id': '\U0001F194'
    }
    alternate = {
        'a': '\U0001F170', 'b': '\U0001F171', 'o': ['\U0001F17E', '\u2B55'], 'i': '\u2139',
        'm': '\u24C2', 'p': '\U0001F17F', 's': '\U0001F4B2', 'u': '\u26CE', 't': '\u271D'
    }
    chars = list(text.lower())
    emojis = list()
    while chars:
        i = 0
        while i < len(other):
            seq, emoji = list(other.items())[i]
            l = len(seq)
            if emoji not in emojis and ''.join(chars[:l]) == seq:
                emojis.append(emoji)
                chars = chars[l:]
                i = 0
                continue
            i += 1

        if not chars:
            break
        char = chars[0]
        if char in string.ascii_lowercase:
            emoji = chr(ord(char) - ord('a') + 0x1F1E6)
            if char in alternate:
                alt = iter(alternate[char])
                while emoji in emojis:
                    try:
                        emoji = next(alt)
                    except StopIteration:
                        break
            emojis.append(emoji)
        elif char in '0123456789':
            emojis.append(char + '\u20E3')
        chars.pop(0)

    return emojis

class ReactionCog(commands.Cog):
    @commands.command()
    async def reaction(self, ctx, *, text):
        message = await ctx.history(limit=1, before=ctx.message).next()
        i = 0
        for emoji in list(dict.fromkeys(to_emoji(text))):
            if i != 0 and i % 20 == 0:
                message = await ctx.send('\u2800')
            await message.add_reaction(emoji)
            i += 1
