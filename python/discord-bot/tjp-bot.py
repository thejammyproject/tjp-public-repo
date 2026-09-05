import os
import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_GUILD_ID = int(os.getenv("DISCORD_GUILD_ID", "1489708000640766045"))

class MySlashBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def setup_hook(self) -> None:
        # Dynamically load all cogs from all Python files in the current directory and its subdirectories
        await self.load_all_cogs()

        # Sync the command tree for slash commands
        guild = discord.Object(id=DISCORD_GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

    async def on_ready(self):
        print(f'\n\nLogged in as: {self.user.name} - {self.user.id}\nVersion: {discord.__version__}\n')
        await self.change_presence(activity=discord.Game(name='Jammys Cogs Builder!!', type=1, url='https://discordpy.readthedocs.io/en/stable/ext/commands/cogs.html'))
        print(f'Successfully logged in and booted...!')

    async def load_all_cogs(self):
        # Get the current working directory
        current_directory = os.getcwd()

        # Loop through all files in the current directory and its subdirectories
        for root, dirs, files in os.walk(current_directory):
            dirs[:] = [directory for directory in dirs if not directory.startswith((".", "__"))]
            for filename in files:
                # Check if the file is a Python file and ends with .py
                if filename.endswith('.py') and filename != 'tjp-bot.py':
                    # Build the full path to the cog file
                    relative_path = os.path.relpath(os.path.join(root, filename), current_directory)
                    cog_path = relative_path.replace(os.path.sep, '.')[:-3]
                    # Load the cog
                    try:
                        await self.load_extension(cog_path)
                        print(f'Loaded cog: {cog_path}')
                    except Exception as e:
                        print(f'Error loading cog {cog_path}: {e}')

bot = MySlashBot()
bot.run(DISCORD_TOKEN)
