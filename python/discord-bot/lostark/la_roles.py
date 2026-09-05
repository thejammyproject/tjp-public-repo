import discord
import os
from discord.ext import commands

DEFAULT_CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])

# This is the dictionary of each role, with its name, custom and emoji and role ID.
roles = [
    ("Guardian Raids", "<:lostark:1015390919614267483>", 1122357794432098354),
    ("Ch. Guardian Raids", "<:lostark:1015390919614267483>", 1122357967275175946),
    ("Abyss Dungeons", "<:lostark:1015390919614267483>", 1122358109726310421),
    ("Ch. Abyss Dungeons", "<:lostark:1015390919614267483>", 1122358259228082186),
    ("Argos", "<:argosbitch:1122356628998598850>", 1122357677272617030),
    ("Card Runs", "<:legendarycards:1122353744709959690>", 1122357540630564944),
]

# Start of the button class to build the buttons for each roles.
class LOARoleButton(discord.ui.Button["LOARoleView"]):
    def __init__(self, role: tuple):
        self.role = role
        custom_id = f"role_{role[2]}" # use role ID as custom_id
        super().__init__(style=discord.ButtonStyle.blurple, label=role[0], custom_id=custom_id)
        self.emoji = role[1]

# Here we define a call back function so when a user interacts (clicks a button) they either get the role or remove
    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        guild = interaction.guild
        role = discord.utils.get(guild.roles, id=self.role[2])

    # Here we use the if and else statements to check for roles, and either remove it or give them it.
        if role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"{member.mention}, You've lost the {role.name} role.",
                ephemeral=True
            )
        else:
            await member.add_roles(role)
            await interaction.response.send_message(
                f"{member.mention}, You've been given the {role.name} role.",
                ephemeral=True
            )

# Next we create the view class
class LOARoleView(discord.ui.View):
    def __init__(self, message_id: int):
        super().__init__(timeout=None) # set timeout to None to make the view persistent
        self.message_id = message_id

        # Here we use the for loop to iterate through the buttons and apply them to the embed.
        for role in roles:
            self.add_item(LOARoleButton(role))

# Here we create the embed class
class LOARoleEmbed(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.view = None  # initialize the view attribute

    # Build the embed here, and only allow administrators to use the command.
    @commands.command(name="laoroles")
    @commands.has_permissions(administrator=True)
    async def RaidRoles(self, ctx):
        # delete the message sent by the user.
        await ctx.message.delete()
        # After deleting message sent for the command, then create embed.

        support_channel = self.bot.get_channel(DEFAULT_CHANNEL_ID)
        game_description = (f"When selecting for example, Guardian Raids, be clear which GR you are going to do to make it easier for people to help.\n\n"
                            f"And as always, be patient wait for guildies to reply and get the ones your interested in.\n")

        embed = discord.Embed(
            title="Select your daily/weekly roles!",
            description=game_description,
            color=0x725691
        )
        embed.set_thumbnail(url='https://i.imgur.com/7e8684J.png')
        embed.set_image(url='https://i.imgur.com/kefzkX3.png')

        message = await ctx.send(embed=embed)
        self.view = LOARoleView(message.id)

        await message.edit(embed=embed, view=self.view)

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(LOARoleEmbed(bot))
