import asyncio
import discord
import os
from discord.ext import commands
import aiohttp

DEFAULT_CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])

class LAUpdateNotifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url = "https://example.com/update_notes"
        self.interval = 300 # seconds
        self.notifications = {}

    async def check_updates(self):
        channel = self.bot.get_channel(DEFAULT_CHANNEL_ID)
        if channel is None:
            return
        async with aiohttp.ClientSession() as session:
            async with session.get("https://patchbot.io/lostark/api/patchnotes?lang=en") as response:
                if response.status == 200:
                    patch_notes = await response.json()
                    # Format and send patch note posts to target channel
                    message = "New patch notes:\n\n"
                    for note in patch_notes:
                        message += f"Title: {note['title']}\n"
                        message += f"Link: {note['url']}\n\n"
                    await channel.send(message)

    @commands.Cog.listener()
    async def on_ready(self):
        while True:
            await self.check_updates()
            await asyncio.sleep(self.interval)

async def setup(bot):
    await bot.add_cog(LAUpdateNotifier(bot))
