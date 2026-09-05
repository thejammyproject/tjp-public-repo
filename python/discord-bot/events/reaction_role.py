# Import modules here
import discord
import os
from discord.ext import commands

DEFAULT_CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])

# This is the dictionary of each role, with its name, custom and emoji and role ID.
roles = [
    ("Warframe", "<:warframe2:1128048718424317962>", 1018295778537644094),
]

class ReactionRoleButton(discord.ui.Button["ReactionRoleView"]):
    def __init__(self, role: tuple):
        self.role = role
        custom_id = f"reaction_role_{role[2]}" # use role ID as custom_id
        super().__init__(style=discord.ButtonStyle.gray, label=role[0], custom_id=custom_id)
        self.emoji = role[1]


    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        guild = interaction.guild
        role = discord.utils.get(guild.roles, name=self.role[0])

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

class ReactionRoleView(discord.ui.View):
    def __init__(self, message_id: int):
        super().__init__(timeout=None) # set timeout to None to make the view persistent
        self.message_id = message_id

        for role in roles:
            self.add_item(ReactionRoleButton(role))

# Create embed here.
class ReactionRoleEmbed(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.view = None  # initialize the view attribute

    @commands.command(name="embed")
    @commands.has_permissions(administrator=True)
    async def ReactionRoles(self, ctx):
        # delete the message sent by the user.
        await ctx.message.delete()
        # After deleting message sent for the command, then create embed.
        support_channel = self.bot.get_channel(DEFAULT_CHANNEL_ID)
        wfroles_channel = self.bot.get_channel(DEFAULT_CHANNEL_ID)
        game_description = (f"Welcome to the Take My Sword discord server, here you can select any role for the games you play or if you want just want to chill out in the non-gaming area.\n\n"
                            f"Don't for get to check out the different roles for each game!\n"
                            f"{wfroles_channel.mention}\n\n"
                            f"And if you need help with the roles as the bot may not always respond, ping a message into {support_channel.mention}\n\n")

        embed = discord.Embed(
            title="Create Your Profile",
            description=game_description,
            color=0x725691
        )
        embed.set_thumbnail(url='https://i.imgur.com/7e8684J.png')
        embed.set_image(url='https://i.imgur.com/kefzkX3.png')

        message = await ctx.send(embed=embed)
        self.view = ReactionRoleView(message.id)

        await message.edit(embed=embed, view=self.view)

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(ReactionRoleEmbed(bot))
