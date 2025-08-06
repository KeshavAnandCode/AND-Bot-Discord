import os
import logging
import threading
from flask import Flask
from discord.ext import commands
import discord
from dotenv import load_dotenv

# Load .env and get token
load_dotenv()
TOKEN = os.getenv('TOKEN')
if not TOKEN:
    print('❌ TOKEN missing in .env')
    exit(1)

# Enable debug logging
logging.basicConfig(level=logging.INFO)

# Flask app for uptime pings
app = Flask(__name__)

@app.route('/')
def home():
    return '✅ Bot is alive!'

def run_keep_alive():
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_keep_alive, daemon=True).start()

# Setup Discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user} (ID: {bot.user.id})')

@bot.command(name='and')
async def and_command(ctx, *role_names):
    if len(role_names) < 2:
        await ctx.reply('❌ Usage: `!and Role1 Role2 [Role3 ...]` (at least 2 roles)')
        return

    guild = ctx.guild
    members = [member async for member in guild.fetch_members(limit=None)]

    # Find all roles
    roles = []
    for role_name in role_names:
        role = discord.utils.find(lambda r: r.name.lower() == role_name.lower(), guild.roles)
        if not role:
            await ctx.reply(f'❌ Role not found: `{role_name}`')
            return
        roles.append(role)

    # Filter members who have ALL the roles
    members_with_all = [
        member for member in members if all(role in member.roles for role in roles)
    ]

    if not members_with_all:
        await ctx.reply('⚠️ No members have all specified roles.')
        return

    mentions = ' '.join(member.mention for member in members_with_all)
    await ctx.send(f'{mentions}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.strip()

    # Check for spoilered !and command: ||!and role1 role2 ...||
    if content.startswith('||!and') and content.endswith('||'):
        command_text = content.strip('|')
        parts = command_text.split()

        if len(parts) < 3:
            await message.channel.send('||❌ Usage: `||!and Role1 Role2 [Role3 ...]||` (at least 2 roles)||')
            return

        _, *role_names = parts
        guild = message.guild
        members = [member async for member in guild.fetch_members(limit=None)]

        roles = []
        for role_name in role_names:
            role = discord.utils.find(lambda r: r.name.lower() == role_name.lower(), guild.roles)
            if not role:
                await message.channel.send(f'||❌ Role not found: `{role_name}`||')
                return
            roles.append(role)

        members_with_all = [
            member for member in members if all(role in member.roles for role in roles)
        ]

        if not members_with_all:
            await message.channel.send('||⚠️ No members have all specified roles.||')
            return

        mentions = ' '.join(member.mention for member in members_with_all)
        await message.channel.send(
            f'||{mentions}||'
        )

    await bot.process_commands(message)

# Run bot
try:
    print("🚀 Starting bot...")
    bot.run(TOKEN)
except Exception as e:
    print(f"❌ Failed to start bot: {e}")