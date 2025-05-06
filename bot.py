import discord
from discord.ext import commands
import json
import os

TOKEN = ''  # Replace this with the regenerated token
GUILD_ID = 1343989764403105892
CHANNEL_ID = 1344652461989953639
MESSAGE_ID = 1369418549596000366
LEADERBOARD_CHANNEL_ID = 1348640863491723366 # Leaderboard channel ID
LEADERBOARD_MESSAGE_ID = 1369435661089898547 # Leaderboard message ID

DATA_FILE = 'kills.json'

# Load or create data
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
else:
    data = {"total_kills": 0, "players": {}}

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

async def update_kill_message():
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        try:
            message = await channel.fetch_message(MESSAGE_ID)
            await message.edit(content=f"💀 Dice Sect and Breadskate users killed: **{data['total_kills']}**")
        except discord.NotFound:
            print("Kill count message not found.")

async def update_leaderboard_message():
    sorted_players = sorted(data["players"].items(), key=lambda x: x[1]["kills"], reverse=True)
    leaderboard_text = "**🏆 Kill Leaderboard**\n"
    for user_id, info in sorted_players:
        leaderboard_text += f"{info['name']}: {info['kills']} kills\n"

    channel = bot.get_channel(LEADERBOARD_CHANNEL_ID)
    if channel:
        try:
            message = await channel.fetch_message(LEADERBOARD_MESSAGE_ID)
            await message.edit(content=leaderboard_text)
        except discord.NotFound:
            print("Leaderboard message not found.")

@bot.event
async def on_ready():
    print(f"{bot.user} is online and ready.")
    guild = bot.get_guild(GUILD_ID)
    if guild:
        async for member in guild.fetch_members(limit=None):
            user_id = str(member.id)
            if user_id not in data["players"]:
                data["players"][user_id] = {"name": member.display_name, "kills": 0}
        save_data()
        await update_leaderboard_message()

@bot.event
async def on_member_join(member):
    if str(member.id) not in data["players"]:
        data["players"][str(member.id)] = {"name": member.display_name, "kills": 0}
        save_data()

@bot.slash_command(name="enemydowned", description="Log a kill for yourself", guild_ids=[GUILD_ID])
async def enemydowned(ctx: discord.ApplicationContext):
    await ctx.defer(ephemeral=True)
    user_id = str(ctx.author.id)

    if user_id not in data["players"]:
        data["players"][user_id] = {"name": ctx.author.display_name, "kills": 0}

    data["players"][user_id]["kills"] += 1
    data["total_kills"] += 1
    save_data()

    await update_kill_message()
    await update_leaderboard_message()
    await ctx.send_followup(f"{ctx.author.display_name} scored a kill! Total: {data['total_kills']}", ephemeral=True)

@bot.slash_command(name="undo", description="Remove your most recent kill", guild_ids=[GUILD_ID])
async def undo(ctx: discord.ApplicationContext):
    await ctx.defer(ephemeral=True)
    user_id = str(ctx.author.id)
    if data["players"].get(user_id, {}).get("kills", 0) > 0:
        data["players"][user_id]["kills"] -= 1
        data["total_kills"] -= 1
        save_data()
        await update_kill_message()
        await update_leaderboard_message()
        await ctx.send_followup(f"{ctx.author.display_name}'s kill undone. Total: {data['total_kills']}", ephemeral=True)
    else:
        await ctx.send_followup("You have no kills to undo.", ephemeral=True)

@bot.slash_command(name="leaderboard", description="Show the top 5 on the leaderboard", guild_ids=[GUILD_ID])
async def leaderboard(ctx: discord.ApplicationContext):
    await ctx.defer()
    sorted_players = sorted(data["players"].items(), key=lambda x: x[1]["kills"], reverse=True)
    leaderboard_text = "**🏆 Kill Leaderboard - Top 5**\n"
    for user_id, info in sorted_players[:5]:
        leaderboard_text += f"{info['name']}: {info['kills']} kills\n"
    await ctx.send_followup(leaderboard_text)

bot.run(TOKEN)
