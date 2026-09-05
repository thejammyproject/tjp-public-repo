import discord
import os
from discord.ext import commands

DEFAULT_CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])

# This is the dictionary of each role, with its name, custom and emoji and role ID.
roles = [
    ("Valtan NM", "<:valtanscissors:1118254586499715203>", 1118288232849883199),
    ("Valtan HM", "<:valtanpaper:1118254590664658964>", 1118288460902563930),
    ("Helltan", "<:valtanrock:1118254587850264627>", 1118288590120701952),
    ("Vykas NM", "<:illeatyou:1118254596570239080>", 1118288698086277180),
    ("Vykas HM", "<:justthetwo:1118254593021853696>", 1118288801496846458),
    ("Kakul Saydon NM", "<:floorpov:1118254663721046087>", 1118288903921745971),
    ("Brel NM", "<:commanduh:1118255888210346084>", 1118289104896012308),
    ("Brel HM", "<:teatime:1118255890320072766>", 1118289232650317875),
    ("Kayangel NM", "<:lfg:1046433969291403285>", 1118289366041755668),
    ("Kayangel HM", "<:lfg:1046433969291403285>", 1118289468395356301),
    ("Akkan NM", "<:decayhunt:1118254610977652856>", 1118289602973810738),
    ("Akkan HM", "<:decaydespair:1118254605223075970>", 1118289688214650921),
]

# Start of the button class to build the buttons for each roles.
class RaidRoleButton(discord.ui.Button["RaidRoleView"]):
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
class RaidRoleView(discord.ui.View):
    def __init__(self, message_id: int):
        super().__init__(timeout=None) # set timeout to None to make the view persistent
        self.message_id = message_id

        # Here we use the for loop to iterate through the buttons and apply them to the embed.
        for role in roles:
            self.add_item(RaidRoleButton(role))

# Here we create the embed class
class RaidRoleEmbed(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.view = None  # initialize the view attribute

    # Build the embed here, and only allow administrators to use the command.
    @commands.command(name="raidroles")
    @commands.has_permissions(administrator=True)
    async def RaidRoles(self, ctx):
        # delete the message sent by the user.
        await ctx.message.delete()
        # After deleting message sent for the command, then create embed.

        support_channel = self.bot.get_channel(DEFAULT_CHANNEL_ID)
        game_description = (f"Apply raid specific roles so your getting pinged for what your interested in.\n\n"
                            f"Don't forget to be patient for guildmates to actually have time to reply, etc. and only apply these if your happy to be pinged regularly.\n\n"
                            f"If you are having any issues selecting a role, you can post in {support_channel.mention}.\n")

        embed = discord.Embed(
            title="Select your Raiding roles!",
            description=game_description,
            color=0x725691
        )
        embed.set_thumbnail(url='https://i.imgur.com/7e8684J.png')
        embed.set_image(url='https://i.imgur.com/kefzkX3.png')

        message = await ctx.send(embed=embed)
        self.view = RaidRoleView(message.id)

        await message.edit(embed=embed, view=self.view)

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(RaidRoleEmbed(bot))
