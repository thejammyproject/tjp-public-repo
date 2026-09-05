import discord
import os
from discord.ext import commands

DEFAULT_CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])

# This is the dictionary of each role, with its name, custom and emoji and role ID.
roles = [
    ("Eidolon Hunting", "<:EidolonShard:1121097815075070043>", 1121075982594490548),
    ("Archon Hunts", "<:archonhunt:1121079247197454448>", 1121076069093621851),
    ("XP Farm", "<:levelup:1121087946049720320>", 1121076200459223080),
    ("Steel Path", "<:SteelEssence:1121088962602205338>", 1121077081678295171),
    ("Circuits", "<:Circuits:1121099334776266783>", 1121097899888099438),
    ("Parvos", "<:SisterhoodEmblem:1121099274684473394>", 1121097986232037426),
    ("Liches", "<:OldBloodEmblem:1121099271421304932>", 1121098043173908500),
    ("Relic Runs", "<:AxiRelicFlawless:1122349589958238349>", 1122349819718021171),
]

# Start of the button class to build the buttons for each roles.
class WFRoleButton(discord.ui.Button["WFRoleView"]):
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
class WFRoleView(discord.ui.View):
    def __init__(self, message_id: int):
        super().__init__(timeout=None) # set timeout to None to make the view persistent
        self.message_id = message_id

        # Here we use the for loop to iterate through the buttons and apply them to the embed.
        for role in roles:
            self.add_item(WFRoleButton(role))

# Here we create the embed class
class WFRoleEmbed(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.view = None  # initialize the view attribute

    # Build the embed here, and only allow administrators to use the command.
    @commands.command(name="wfroles")
    @commands.has_permissions(administrator=True)
    async def WFRoles(self, ctx):
        # delete the message sent by the user.
        await ctx.message.delete()
        # After deleting message sent for the command, then create embed.

        support_channel = self.bot.get_channel(DEFAULT_CHANNEL_ID)
        game_description = (f"Apply Warframe specific roles so your getting pinged for what your interested in.\n\n"
                            f"Don't forget to be patient for clan members to actually have time to reply, etc. and only apply these if your happy to be pinged regularly.\n\n"
                            f"If you are having any issues selecting a role, you can post in {support_channel.mention}.\n")

        embed = discord.Embed(
            title="Select your Warframe roles!",
            description=game_description,
            color=0x725691
        )
        embed.set_thumbnail(url='https://i.imgur.com/7e8684J.png')
        embed.set_image(url='https://i.imgur.com/kefzkX3.png')

        message = await ctx.send(embed=embed)
        self.view = WFRoleView(message.id)

        await message.edit(embed=embed, view=self.view)

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(WFRoleEmbed(bot))
