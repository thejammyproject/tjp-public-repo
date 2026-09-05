import discord
import os
from discord.ext import commands

DEFAULT_CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = discord.utils.get(member.guild.channels, id=DEFAULT_CHANNEL_ID)
        if channel is not None:
                embed = discord.Embed(title="A NEW SOUL",description=f"Welcome to The {member.guild.name} Society {member.mention}, we have been expecting you.")
                embed.set_thumbnail(url='https://i.imgur.com/mu7cgXs.png')
                await channel.send(embed=embed)
        else:
            print("id channel wrong")

async def setup(bot):
    await bot.add_cog(Welcome(bot))
