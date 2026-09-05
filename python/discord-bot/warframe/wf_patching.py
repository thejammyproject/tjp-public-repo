import asyncio
import discord
import os
from discord.ext import commands
import aiohttp

DEFAULT_CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])

class WFUpdateNotifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url = "https://api.warframestat.us/pc/news"
        self.interval = 300 # seconds
        self.notifications = {}
        # Initialize self.notifications with the IDs of patch notes that have already been posted
        asyncio.ensure_future(self.get_initial_notifications())

    async def get_initial_notifications(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                if response.status == 200:
                    patch_notes = await response.json()
                    for note in patch_notes:
                        self.notifications[note['id']] = True

    async def check_updates(self):
        channel = self.bot.get_channel(DEFAULT_CHANNEL_ID)
        if channel is None:
            return
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                if response.status == 200:
                    patch_notes = await response.json()
                    # Sort the patch notes in reverse chronological order based on the date field
                    sorted_patch_notes = sorted(patch_notes, key=lambda x: x['date'], reverse=True)
                    # Get the latest patch note
                    latest_patch_note = sorted_patch_notes[0]
                    # Check if the latest patch note has already been posted
                    if latest_patch_note['id'] not in self.notifications:
                        # Mark the latest patch note as posted
                        self.notifications[latest_patch_note['id']] = True
                        # Format and send the latest patch note to target channel
                        embed = discord.Embed(title="New patch notes", description=latest_patch_note['message'], color=discord.Color.blue())
                        embed.add_field(name="Link", value=f"[Click here]({latest_patch_note['link']})", inline=False)
                        if 'imageLink' in latest_patch_note:  # Check if 'image' key exists
                            embed.set_image(url=latest_patch_note['imageLink'])  # Add image here
                        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        while True:
            await self.check_updates()
            await asyncio.sleep(self.interval)

async def setup(bot):
    await bot.add_cog(WFUpdateNotifier(bot))
