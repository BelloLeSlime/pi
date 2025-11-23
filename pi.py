import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from keep_alive import keep_alive
keep_alive()

load_dotenv()

# Intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

# State
state = {
    "channel_id": None,
    "enabled": False,
    "difficulty": "easy",  # easy, medium, hard
    "react_enabled": False,
    "last_user": None,
    "count": 0
}

@bot.command()
async def attribuer_salon(ctx, salon: discord.TextChannel):
    state["channel_id"] = salon.id
    await ctx.send(f"OK bebou, je vais dans {salon.mention}")

@bot.command()
async def enabled(ctx, enabled: bool):
    state["enabled"] = enabled
    await ctx.send(f"OK, {'go compter' if enabled else 'c nul enfait de compter'}")

@bot.command()
async def difficulty(ctx, difficulty: str):
    if difficulty not in ["easy", "medium", "hard"]:
        await ctx.send("bro shut up et dis easy medium ou hard")
        return
    state["difficulty"] = difficulty
    await ctx.send(f"ok, je suis en {difficulty}")

@bot.command()
async def react(ctx, enabled: bool):
    state["react_enabled"] = enabled
    await ctx.send(f"ok, je vais {'jou... heu réagir aux msg' if enabled else 'areter de réagir'}")

@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if message.author.bot:
        return
    if not state["enabled"]:
        return
    if message.channel.id != state["channel_id"]:
        return

    content = message.content.strip()
    if not content.isdigit():
        return

    num = int(content)
    expected = state["count"] + 1

    # HARD: same person twice -> reset
    if state["difficulty"] == "hard" and message.author.id == state["last_user"]:
        state["count"] = 0
        state["last_user"] = None
        await message.reply(f"{message.author.mention} a tout foiré le noob, il a parlé 2 fois on repart à 0 :p")
        return

    # WRONG NUMBER
    if num != expected:
        if state["difficulty"] == "easy":
            await message.reply(f"{message.author.mention} attention c'est pas ça :/")
            return
        elif state["difficulty"] == "medium":
            state["count"] = 0
            state["last_user"] = None
            await message.reply(f"désolé {message.author.mention} mais {state['count']} +1 != {num} on repart à 0 Xp")
            return

    # CORRECT NUMBER
    state["count"] += 1
    state["last_user"] = message.author.id

    if state["react_enabled"]:
        await message.add_reaction("✅")

bot.run(os.getenv("DISCORD_TOKEN"))
