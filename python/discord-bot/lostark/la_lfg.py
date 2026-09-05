import asyncio
import discord
import os
import psycopg
import uuid
from discord.ext import commands
from discord import app_commands
import logging

# Configure logging
logging.basicConfig(
    filename='lostark/logs/error.log',
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

modes = {
    "Valtan": ["Normal Mode, 1415", "Hard Mode, 1445", "Inferno Mode, 1445"],
    "Vykas": ["Normal Mode, 1430", "Hard Mode, 1460", "Inferno Mode, 1460"],
    "Kakul-Saydon": ["Training mode, 1385", "Normal Mode, 1475", "Inferno Mode, 1475"],
    "Brelshaza": ["Training mode, 1430", "Gate 1&2, 1490", "Gate 3&4, 1500", "Gate 5&6, 1520",  "Gate 1&2, 1540", "Gate 3&4, 1560", "Gate 5&6, 1580"],
    "Kayangel": ["Normal Mode, 1540", "Hard Mode, 1580"],
    "Akkan": ["Normal Mode, 1580", "Hard Mode, 1620"],
}

raids = {
    "Valtan": ("Valtan Legion Raid. Max 8 players", 8, 6, 2, "https://i.imgur.com/R63CtZ9.jpg"),
    "Vykas": ("Vykas Legion Raid. Max 8 players", 8, 6, 2, "https://i.imgur.com/u7KB3Rz.png"),
    "Kakul-Saydon": ("Kakul Legion Raid. Max 4 players", 4, 3, 1, "https://i.imgur.com/ICc9VY1.jpg"),
    "Brelshaza": ("Brelshaza Legion Raid. Max 8 players", 8, 6, 2, "https://i.imgur.com/NyDK7dO.jpg"),
    "Kayangel": ("Kayangel Abyss Raid. Max 4 players", 4, 3, 1, "https://i.imgur.com/hfm6iSp.jpg"),
    "Akkan": ("Akkan Legion Raid. Max 8 players", 8, 6, 2, "https://i.imgur.com/0SkBpg0.jpg"),
}

connection = psycopg.connect(
    host=os.environ["DB_HOST"],
    dbname=os.environ["DB_NAME"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    sslmode=os.getenv("DB_SSLMODE", "require"),
    connect_timeout=10,
)
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS raids (
        id TEXT PRIMARY KEY,
        creator TEXT,
        raid TEXT,
        mode TEXT,
        max_players INTEGER,
        max_dps INTEGER,
        max_support INTEGER,
        dps TEXT,
        support TEXT,
        message_id TEXT,
        thread_id TEXT,
        channel_id TEXT,
        title TEXT,
        owner_id TEXT
    )
''')
connection.commit()

cursor.execute("SELECT * FROM raids")
active_raids = cursor.fetchall()

def channel_embed(raid_id, user=None, role=None):
    cursor.execute("SELECT * FROM raids WHERE id=%s", (raid_id,))
    raid_data = cursor.fetchone()

    if raid_data:
        raid_title = raid_data[12]  # Adjust this index if needed. This assumes title is the 13th column (index 12)
        raid_name = raid_data[2]  # Adjust this index if needed
        dps = raid_data[7].split(',') if raid_data[7] else []
        support = raid_data[8].split(',') if raid_data[8] else []
        thumbnail_url = raids[raid_name][4]  # Get the thumbnail URL for the selected raid

        # Create the embed
        channel_embed = discord.Embed(
            title=raid_title,
            description=f"{raid_name} {raid_data[3]}\n\nIf this is your first time in the raid, make sure to watch guides and videos and be sure to let your teammates know.\n\n",
            color=0x725691
        )
        channel_embed.set_image(url=thumbnail_url)

        # Add fields for the user and their role, if provided
        if user and role:
            channel_embed.add_field(name="Player", value=user, inline=True)
            channel_embed.add_field(name="Role", value=role, inline=True)

        # Add Raid ID in the footer
        channel_embed.set_footer(text=f"Raid ID: {raid_id}")

        return channel_embed

class DPSButton(discord.ui.Button):
    def __init__(self, raid_id):
        super().__init__(style=discord.ButtonStyle.green, label="⚔️ DPS")
        self.raid_id = raid_id

    async def callback(self, interaction: discord.Interaction):
        # Defer the interaction immediately to stop interaction failed.
        await interaction.response.defer()

        # Add delay to button call back to prevent rate limiting.
        await asyncio.sleep(3)

        cursor.execute("SELECT * FROM raids WHERE id=%s", (self.raid_id,))
        raid_data = cursor.fetchone()

        if raid_data:
            user_id = str(interaction.user.id)  # Get the user ID
            user = interaction.user.name

            max_players = raid_data[4]
            max_dps = raid_data[5]
            max_support = raid_data[6]
            dps_column = raid_data[7]
            support_column = raid_data[8]

            dps = dps_column.split(',') if dps_column else []
            support = support_column.split(',') if support_column else []

            if len(dps) >= max_dps:
                await interaction.followup.send("Maximum DPS roles reached.", ephemeral=True)
                return

            if user_id not in dps:  # Add the user ID to DPS only if it's not already present
                dps.append(user_id)

            if user_id in support:  # Remove the user ID from the support list
                support.remove(user_id)

            # Update the respective columns based on the selected role
            dps_column = ",".join(dps)
            support_column = ",".join(support)

            cursor.execute("UPDATE raids SET dps=%s, support=%s WHERE id=%s", (dps_column, support_column, self.raid_id))  # Update the columns with the updated lists of DPS and support user IDs
            connection.commit()

            msg = await interaction.channel.fetch_message(interaction.message.id)
            embed = msg.embeds[0]

            players_field = embed.fields[0]
            roles_field = embed.fields[1]

            players_value = players_field.value.split("\n")
            roles_value = roles_field.value.split("\n")

            try:
                index = players_value.index(user)
                roles_value[index] = "DPS"
            except ValueError:
                players_value.append(user)
                roles_value.append("DPS")

            embed.set_field_at(0, name="Player", value="\n".join(players_value), inline=True)
            embed.set_field_at(1, name="Role", value="\n".join(roles_value), inline=True)

            await msg.edit(embed=embed)

            thread_id = raid_data[10]
            thread = await interaction.guild.fetch_channel(thread_id)
            if thread:
                await thread.add_user(interaction.user)

            # Log the DPS role selection
            logging.info(f"User {user} selected DPS role for raid {self.raid_id}")

class SupportButton(discord.ui.Button):
    def __init__(self, raid_id):
        super().__init__(style=discord.ButtonStyle.blurple, label="🛡️ Support")
        self.raid_id = raid_id

    async def callback(self, interaction: discord.Interaction):
        # Defer the interaction immediately
        await interaction.response.defer()

        # Add delay to button call back to prevent rate limiting
        await asyncio.sleep(3)

        cursor.execute("SELECT * FROM raids WHERE id=%s", (self.raid_id,))
        raid_data = cursor.fetchone()

        if raid_data:
            user_id = str(interaction.user.id)  # Get the user ID
            user = interaction.user.name

            max_players = raid_data[4]
            max_dps = raid_data[5]
            max_support = raid_data[6]
            dps_column = raid_data[7]
            support_column = raid_data[8]

            dps = dps_column.split(',') if dps_column else []
            support = support_column.split(',') if support_column else []

            if len(support) >= max_support:
                await interaction.followup.send("Maximum Support roles reached.", ephemeral=True)
                return

            if user_id not in support:  # Add the user ID to support only if it's not already present
                support.append(user_id)

            if user_id in dps:  # Remove the user ID from the DPS list
                dps.remove(user_id)

            # Update the respective columns based on the selected role
            dps_column = ",".join(dps)
            support_column = ",".join(support)

            cursor.execute("UPDATE raids SET dps=%s, support=%s WHERE id=%s", (dps_column, support_column, self.raid_id))  # Update the columns with the updated lists of DPS and support user IDs
            connection.commit()

            msg = await interaction.channel.fetch_message(interaction.message.id)
            embed = msg.embeds[0]

            players_field = embed.fields[0]
            roles_field = embed.fields[1]

            players_value = players_field.value.split("\n")
            roles_value = roles_field.value.split("\n")

            try:
                index = players_value.index(user)
                roles_value[index] = "Support"
            except ValueError:
                players_value.append(user)
                roles_value.append("Support")

            embed.set_field_at(0, name="Player", value="\n".join(players_value), inline=True)
            embed.set_field_at(1, name="Role", value="\n".join(roles_value), inline=True)

            await msg.edit(embed=embed)

            thread_id = raid_data[10]
            thread = await interaction.guild.fetch_channel(thread_id)
            if thread:
                await thread.add_user(interaction.user)

            # Log the Support role selection
            logging.info(f"User {user} selected Support role for raid {self.raid_id}")

class CreateButton(discord.ui.Button):
    def __init__(self, raid_id, title):
        super().__init__(style=discord.ButtonStyle.green, label="✅ Create")
        self.raid_id = raid_id
        self.title = title

    async def callback(self, interaction: discord.Interaction):
        self.view.create_button.disabled = True
        await self.view.refresh()

        selected_raid = self.view.raid_select.values[0] if self.view.raid_select and self.view.raid_select.values else None
        selected_mode = self.view.mode_select.values[0] if self.view.mode_select and self.view.mode_select.values else None
        selected_role = self.view.role_select.values[0] if self.view.role_select and self.view.role_select.values else None
        user_id = str(interaction.user.id)  # Get the user ID

        if selected_raid and selected_mode:
            channel = interaction.channel

            # Create the thread and store the thread channel ID
            thread = await channel.create_thread(
                name=self.title,  # Use the title from the button (self.title) instead of self.view.title
                auto_archive_duration=10080,
                invitable=False  # Make the thread private
            )
            thread_id = thread.id
            # Add user to the thread
            await thread.add_user(interaction.user)

            # Get the raid information from the dictionaries
            raid_info = raids[selected_raid]
            max_players = raid_info[1]
            max_dps = raid_info[2]
            max_support = raid_info[3]

            dps_column = ""  # Initialize the DPS column value
            support_column = ""  # Initialize the Support column value

            # Determine the role column based on the selected_role
            if selected_role.lower() == "dps":
                dps_column = user_id
                selected_role = "DPS"
            elif selected_role.lower() == "support":
                support_column = user_id
                selected_role = "Support"

            # Store the thread channel ID, user ID, and role in the respective columns in the database
            cursor.execute("INSERT INTO raids (id, creator, raid, mode, max_players, max_dps, max_support, dps, support, message_id, thread_id, channel_id, title, owner_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (self.raid_id, interaction.user.name, selected_raid, selected_mode, max_players, max_dps, max_support, dps_column, support_column, "", thread_id, channel.id, self.title, user_id))
            connection.commit()

            # Create the embed using the raid_id, user, and selected_role variables
            embed = channel_embed(self.raid_id, interaction.user.name, selected_role)

            dps_button = DPSButton(self.raid_id)
            support_button = SupportButton(self.raid_id)
            leave_button = LeaveButton(self.raid_id)

            view = discord.ui.View(timeout=None)
            view.add_item(dps_button)
            view.add_item(support_button)
            view.add_item(leave_button)

            # Send a new message to the channel with your embed and view
            new_message = await interaction.channel.send(embed=embed, view=view)

            # Store the message ID in the database
            cursor.execute("UPDATE raids SET message_id=%s WHERE id=%s", (str(new_message.id), self.raid_id))
            connection.commit()

        self.view.create_button.disabled = False
        await self.view.refresh()

        self.view.clear_items()
        group_chat_button = GroupChatButton(thread)
        self.view.add_item(group_chat_button)

        await interaction.response.send_message(content="The raid group has been created", ephemeral=True, view=self.view)

class LeaveButton(discord.ui.Button):
    def __init__(self, raid_id):
        super().__init__(style=discord.ButtonStyle.red, label="⛔ Leave")
        self.raid_id = raid_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        # Add delay to button call back to prevent rate limiting
        await asyncio.sleep(3)

        cursor.execute("SELECT * FROM raids WHERE id=%s", (self.raid_id,))
        raid_data = cursor.fetchone()

        if raid_data:
            dps = raid_data[7].split(',') if raid_data[7] else []
            support = raid_data[8].split(',') if raid_data[8] else []
            user = interaction.user.name  # Replace 'user' with 'interaction.user.name'

            if user in dps:
                dps.remove(user)

            if user in support:
                support.remove(user)

            cursor.execute("UPDATE raids SET dps=%s, support=%s WHERE id=%s", (",".join(dps), ",".join(support), self.raid_id))
            connection.commit()

            msg = await interaction.channel.fetch_message(interaction.message.id)
            embed = msg.embeds[0]

            players_field = embed.fields[0]
            roles_field = embed.fields[1]

            players_value = players_field.value.split("\n")
            roles_value = roles_field.value.split("\n")

            try:
                index = players_value.index(user)
                players_value.pop(index)
                roles_value.pop(index)
            except ValueError:
                return  # User not found, nothing to do

            embed.set_field_at(0, name="Player", value="\n".join(players_value), inline=True)
            embed.set_field_at(1, name="Role", value="\n".join(roles_value), inline=True)

            await msg.edit(embed=embed)

            thread_id = raid_data[10]
            thread = await interaction.guild.fetch_channel(thread_id)
            if thread:
                await thread.remove_user(interaction.user)


class GroupChatButton(discord.ui.Button):
    def __init__(self, thread):
        super().__init__(style=discord.ButtonStyle.green, label="Group Chat", url=thread.jump_url)

class RoleRaidModeSelection(discord.ui.View):
    def __init__(self, raid_id, title):  # include title here
        super().__init__(timeout=None)  # Set the timeout to None here
        self.raid_id = raid_id
        self.title = title  # Set title attribute here
        self.raid_select = None
        self.mode_select = None
        self.role_select = RoleSelect(self)  # This was missing
        self.create_button = CreateButton(raid_id, title)
        self.add_item(self.role_select)  # Add the RoleSelect to the view
        self.add_item(self.create_button)

    async def refresh(self):
        self.clear_items()
        self.add_item(self.create_button)

    async def on_role_select(self, interaction, selected_role):
        self.clear_items()
        self.add_item(self.raid_select)
        self.add_item(self.mode_select)
        self.add_item(self.create_button)
        await interaction.response.edit_message(view=self)

    async def on_raid_select(self, interaction, selected_raid):
        if selected_raid is None:
            await interaction.response.send_message("Please select a raid.")
        else:
            self.mode_select = ModeSelect(self, selected_raid, modes)
            self.clear_items()
            self.add_item(self.raid_select)
            self.add_item(self.mode_select)
            self.add_item(self.create_button)
            await interaction.response.edit_message(view=self)

    async def on_mode_select(self, interaction, selected_mode):
        if self.raid_select and self.raid_select.values:
            selected_raid = self.raid_select.values[0]
            self.clear_items()
            self.add_item(self.raid_select)
            self.add_item(self.mode_select)
            self.add_item(self.create_button)
            await interaction.response.edit_message(view=self)

class RoleSelect(discord.ui.Select):
    def __init__(self, parent_view):
        options = [
            discord.SelectOption(
                label='DPS',
                value='dps',
                description="Choose this role if you're a damage dealer.",
                emoji=discord.PartialEmoji(animated=False, name='⚔️', id=None),
                default=False
            ),
            discord.SelectOption(
                label='Support',
                value='support',
                description="Choose this role if you're a support.",
                emoji=discord.PartialEmoji(animated=False, name='🛡️', id=None),
                default=False
            )
        ]
        super().__init__(
            custom_id='role_select',
            options=options,
            placeholder="Choose your role",
            min_values=1,
            max_values=1
        )
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        if not self.values:  # Check if role is selected
            await interaction.response.send_message("Please select a role.", ephemeral=True)
            return

        selected_role = self.values[0].lower()
        if selected_role == 'dps':
            self.placeholder = selected_role.upper()
        elif selected_role == 'support':
            self.placeholder = selected_role.capitalize()
        else:
            self.placeholder = selected_role
        self.value = selected_role

        # After role selection, add raid selection to the view
        self.parent_view.raid_select = LegionRaidSelect(self.parent_view)

        self.parent_view.clear_items()
        self.parent_view.add_item(self)
        self.parent_view.add_item(self.parent_view.raid_select)
        self.parent_view.add_item(self.parent_view.create_button)
        await interaction.response.edit_message(view=self.parent_view)

class LegionRaidSelect(discord.ui.Select):
    def __init__(self, parent_view):
        options = [discord.SelectOption(label=raid, value=raid, description=f"{raids[raid][0]}, players: {raids[raid][1]}") for raid in raids]
        super().__init__(
            placeholder='Choose a raid',
            min_values=1,
            max_values=1,
            options=options,
            custom_id='raid_select',
            disabled=False
        )
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        selected_raid = interaction.data['values'][0]
        self.placeholder = selected_raid
        self.value = selected_raid
        if selected_raid not in modes:
            await interaction.response.send_message("Invalid raid selection. Please try again.")
            return
        self.parent_view.clear_items()
        self.parent_view.add_item(self.parent_view.role_select)
        self.parent_view.add_item(self)
        self.parent_view.mode_select = ModeSelect(self.parent_view, selected_raid, modes)
        self.parent_view.add_item(self.parent_view.mode_select)
        self.parent_view.add_item(self.parent_view.create_button)
        await interaction.response.edit_message(view=self.parent_view)

class ModeSelect(discord.ui.Select):
    def __init__(self, parent_view, selected_raid, raid_modes):
        if selected_raid not in raid_modes:
            raise ValueError(f"Invalid raid: {selected_raid}")
        self.parent_view = parent_view
        self.selected_raid = selected_raid
        self.raid_modes = raid_modes
        options = [discord.SelectOption(label=mode, value=mode) for mode in raid_modes[selected_raid]]
        super().__init__(
            custom_id='mode_select',
            options=options,
            placeholder="Choose a mode",
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: discord.Interaction):
        selected_mode = self.values[0]
        self.placeholder = selected_mode
        self.value = selected_mode
        self.parent_view.clear_items()
        self.parent_view.add_item(self.parent_view.role_select)
        self.parent_view.add_item(self.parent_view.raid_select)
        self.parent_view.add_item(self)
        self.parent_view.add_item(self.parent_view.create_button)
        await interaction.response.edit_message(view=self.parent_view)

class LegionRaidCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="create", description="Create a new raid")
    @app_commands.describe(title='Your cool title here..')
    async def create_raid(self, ctx, title: str):
        raid_id = str(ctx.id)
        role_raid_mode_view = RoleRaidModeSelection(raid_id, title)  # pass raid_id here
        await ctx.response.send_message(view=role_raid_mode_view, ephemeral=True)

        # Add title to database.
        cursor.execute("UPDATE raids SET title = %s WHERE id = %s", (title, raid_id))

    @commands.Cog.listener()
    async def on_ready(self):
        cursor.execute("SELECT * FROM raids")
        active_raids = cursor.fetchall()

        for raid in active_raids:
            raid_id = raid[0]
            dps = raid[7].split(',') if raid[7] else []
            support = raid[8].split(',') if raid[8] else []

            message_id = raid[9]
            channel_id = raid[11]  # Fetch the channel ID from the database

            # Fetch the channel using the channel ID
            channel = self.bot.get_channel(int(channel_id))
            if channel is None:
                logger = logging.getLogger(__name__)
                logger.error(f"Channel not found for raid ID {raid_id}")

                # Optionally, you can remove the entry from the database since the channel is not found.
                cursor.execute("DELETE FROM raids WHERE id=%s", (raid_id,))
                connection.commit()

                continue

            try:
                # Fetch the message using the message ID within the channel
                message = await channel.fetch_message(int(message_id))
            except discord.NotFound:
                logger = logging.getLogger(__name__)
                logger.error(f"Raid message not found for ID {message_id}")

                # Optionally, you can remove the entry from the database since the message is not found.
                cursor.execute("DELETE FROM raids WHERE id=%s", (raid_id,))
                connection.commit()

                continue

            dps_button = DPSButton(raid_id)  # use raid_id
            support_button = SupportButton(raid_id)  # use raid_id
            leave_button = LeaveButton(raid_id)  # use raid_id

            view = discord.ui.View(timeout=None)
            view.add_item(dps_button)
            view.add_item(support_button)
            view.add_item(leave_button)

            await message.edit(view=view)

    @commands.Cog.listener()
    async def on_thread_member_remove(self, thread_member):
        # Fetch the User associated with the ThreadMember
        member = await self.bot.fetch_user(thread_member.id)
        cursor.execute("SELECT * FROM raids WHERE dps LIKE %s OR support LIKE %s", ('%'+str(member.id)+'%', '%'+str(member.id)+'%'))
        raid_data = cursor.fetchall()

        for raid in raid_data:
            raid_id = raid[0]  # Get the raid ID

            dps_column = raid[7]  # Get the DPS column
            support_column = raid[8]  # Get the Support column

            dps = dps_column.split(',') if dps_column else []
            support = support_column.split(',') if support_column else []

            if str(member.id) in dps:  # If the user is in DPS, remove them
                dps.remove(str(member.id))

            if str(member.id) in support:  # If the user is in support, remove them
                support.remove(str(member.id))

            dps_column = ",".join(dps)  # Update the DPS column
            support_column = ",".join(support)  # Update the Support column

            cursor.execute("UPDATE raids SET dps=%s, support=%s WHERE id=%s", (dps_column, support_column, raid_id))  # Update the columns with the updated lists of DPS and support user IDs
            connection.commit()

            # Fetch the embed message
            channel_id = raid[11]
            message_id = raid[9]
            channel = self.bot.get_channel(int(channel_id))
            msg = await channel.fetch_message(int(message_id))
            embed = msg.embeds[0]

            # Update the embed
            players_field = embed.fields[0]
            roles_field = embed.fields[1]

            players_value = players_field.value.split("\n")
            roles_value = roles_field.value.split("\n")

            if member.name in players_value:
                index = players_value.index(member.name)
                players_value.pop(index)
                roles_value.pop(index)

            embed.set_field_at(0, name="Player", value="\n".join(players_value), inline=True)
            embed.set_field_at(1, name="Role", value="\n".join(roles_value), inline=True)

            await msg.edit(embed=embed)

async def setup(bot):
    await bot.add_cog(LegionRaidCommand(bot))
