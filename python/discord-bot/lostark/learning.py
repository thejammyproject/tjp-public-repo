import discord
import asyncio
import os
from discord.ext import commands, tasks
from datetime import datetime
from pytz import timezone

DEFAULT_CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])
DISCORD_GUILD_ID = int(os.environ["DISCORD_GUILD_ID"])

class LearningRaids(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tag_role.start()

    def cog_unload(self):
        self.tag_role.cancel()

    @tasks.loop(hours=24)
    async def tag_role(self):
        now = datetime.now(timezone('Europe/Berlin'))
        if now.weekday() == 2 and now.hour == 12 and now.minute >= 00:  # start it at 1200hrs 1100hrs UK time
            guild = self.bot.get_guild(DISCORD_GUILD_ID)
            if guild is None:
                return
            role = discord.utils.get(guild.roles, id=1036402466973044887)  # replace with role id
            channel = self.bot.get_channel(DEFAULT_CHANNEL_ID)
            if channel is None or role is None:
                return
            embed = discord.Embed(
                title="Learning Raids",
                description=f"Select the raid you need to learn and we will try our best to set up a group to run through, no promises can be made for everyone.\n\n"
                            f"0️⃣ Valtan Normal\n"
                            f"1️⃣ Valtan Hard\n"
                            f"2️⃣ Vykas Normal\n"
                            f"3️⃣ Vykas Hard\n"
                            f"4️⃣ Kakul Normal\n"
                            f"5️⃣ Brel NM G1-2\n"
                            f"6️⃣ Brel NM G3-4\n"
                            f"7️⃣ Brel NM G5-6\n"
                            f"8️⃣ Brel HM G1-2\n"
                            f"9️⃣ Brel HM G3-4\n"
                            f"🔟 Brel HM G5-6\n\n",
                            # f"If you can't find a learning group here, you can join the [LostArkLFG Discord](https://discord.gg/lostarklfg).",
                color=0x725691
    )

            # Send the mention and the embed in the same message
            message = await channel.send(content=f'{role.mention}', embed=embed)
            await message.add_reaction('0️⃣')
            await message.add_reaction('1️⃣')
            await message.add_reaction('2️⃣')
            await message.add_reaction('3️⃣')
            await message.add_reaction('4️⃣')
            await message.add_reaction('5️⃣')
            await message.add_reaction('6️⃣')
            await message.add_reaction('7️⃣')
            await message.add_reaction('8️⃣')
            await message.add_reaction('9️⃣')
            await message.add_reaction('🔟')
        else:
            return

    @tag_role.before_loop
    async def before_tag_role(self):
        for _ in range(60*60*24):  # loop the whole day
            now = datetime.now(timezone('Europe/Berlin'))
            if now.hour == 12 and now.minute >= 00:  # wait until the hour before starting tag_role
                break
            await asyncio.sleep(1)  # wait a second before looping again

async def setup(bot):
    await bot.add_cog(LearningRaids(bot))
