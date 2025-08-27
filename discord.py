import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import asyncio
import aiohttp
from flask import Flask


TOKEN = 'DISCORD TOKEN'
CHANNEL_ID = 'CHANNEL_ID'  # Channel where leaderboard will be posted
DATABASE_NAME = 'leaderboard.db'

# Initialize bot with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Database setup
def setup_database():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, problems_solved INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS monthly_stats
                 (username TEXT, problems_solved INTEGER, month TEXT,
                  UNIQUE(username, month))''')
    conn.commit()
    conn.close()

async def fetch_codechef_stats(username):
    """Fetch problem solving statistics from CodeChef profile"""
    async with aiohttp.ClientSession() as session:
        url = f'https://www.codechef.com/users/{username}'
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    problems_div = soup.find('div', {'class': 'problems-solved'})
                    if problems_div:
                        return int(problems_div.text.strip())
                return 0
        except Exception as e:
            print(f"Error fetching stats for {username}: {e}")
            return 0

async def update_user_stats():
    """Update statistics for all users"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()

    # Get all users
    c.execute('SELECT username FROM users')
    users = c.fetchall()

    current_month = datetime.now().strftime('%Y-%m')

    for username in users:
        username = username[0]
        problems_solved = await fetch_codechef_stats(username)

        # Update current stats
        c.execute('UPDATE users SET problems_solved = ? WHERE username = ?',
                 (problems_solved, username))

        # Add monthly record
        c.execute('''INSERT OR REPLACE INTO monthly_stats
                     (username, problems_solved, month)
                     VALUES (?, ?, ?)''',
                 (username, problems_solved, current_month))

    conn.commit()
    conn.close()
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    setup_database()
    update_leaderboard.start()

@bot.command(name='adduser')
async def add_user(ctx, username: str):
    """Add a new user to track"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    try:
        problems_solved = await fetch_codechef_stats(username)
        c.execute('INSERT INTO users (username, problems_solved) VALUES (?, ?)',
                 (username, problems_solved))
        conn.commit()
        await ctx.send(f'Added user {username} to leaderboard tracking')
    except sqlite3.IntegrityError:
        await ctx.send(f'User {username} is already being tracked')
    finally:
        conn.close()

@bot.command(name='removeuser')
async def remove_user(ctx, username: str):
    """Remove a user from tracking"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE username = ?', (username,))
    conn.commit()
    conn.close()
    await ctx.send(f'Removed user {username} from leaderboard tracking')

@bot.command(name='leaderboard')
async def show_leaderboard(ctx):
    """Display current leaderboard"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''SELECT username, problems_solved FROM users
                 ORDER BY problems_solved DESC''')
    users = c.fetchall()
    conn.close()

    if not users:
        await ctx.send("No users are currently being tracked!")
        return

    leaderboard = "🏆 **CodeChef Leaderboards** 🏆\n\n"
    for i, (username, solved) in enumerate(users, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "👤"
        leaderboard += f"{medal} {i}. {username}: {solved} problems\n"

    await ctx.send(leaderboard)

@tasks.loop(hours=24)
async def update_leaderboard():
    """Update leaderboard daily and post monthly summary"""
    await update_user_stats()
 # If it's the first day of the month, post monthly summary
    if datetime.now().day == 1:
        channel = bot.get_channel(int(CHANNEL_ID))
        if channel:
            conn = sqlite3.connect(DATABASE_NAME)
            c = conn.cursor()

            last_month = (datetime.now().replace(day=1) -
                         datetime.timedelta(days=1)).strftime('%Y-%m')

            c.execute('''SELECT username, problems_solved FROM monthly_stats
                        WHERE month = ? ORDER BY problems_solved DESC''',
                     (last_month,))
            monthly_stats = c.fetchall()
            conn.close()

            if monthly_stats:
                summary = f"📊 **Monthly Leaderboard - {last_month}** 📊\n\n"
                for i, (username, solved) in enumerate(monthly_stats, 1):
                    medal = ("🥇" if i == 1 else "🥈" if i == 2
                            else "🥉" if i == 3 else "👤")
                    summary += f"{medal} {i}. {username}: {solved} problems\n"

                await channel.send(summary)

# Run the bot
bot.run(TOKEN)
