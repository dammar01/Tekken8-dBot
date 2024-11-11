from dotenv import load_dotenv
from discord.ext import commands
from find_moveset import finding_move, draw_find_move
from discord import app_commands
import discord, os, traceback, requests, asyncio

load_dotenv(override=True)
TOKEN = os.getenv("DISCORD_TOKEN")
HOST = os.getenv("HOST")

intents = discord.Intents.default()
intents.message_content = True
active_sessions = {}

bot = commands.Bot(command_prefix="/", intents=intents)


async def check_connection():
    print("Checking connection..")
    try:
        response = requests.get(HOST, timeout=5)
        data = response.json()
        if data["detail"] == "Not Found":
            print(f"Using host {HOST}")
            return True
        else:
            print(f"URL returned status code {response.status_code}: {HOST}")
            return False
    except requests.ConnectionError:
        print(f"Failed to connect to URL: {HOST}")
        return False
    except requests.Timeout:
        print(f"Connection to URL timed out: {HOST}")
        return False
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return False


@bot.event
async def on_ready():
    print("Setting up bot...")
    await bot.tree.sync()
    while not await check_connection():
        print("Retrying connection in 10 seconds...")
        await asyncio.sleep(10)
    print(f"We have logged in as {bot.user}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    user_id = message.author.id
    try:
        if bot.user in message.mentions and message.channel.name == "find-moveset":
            if user_id in active_sessions:
                await message.reply(
                    "Your previous request is still processing. Please wait."
                )
                return
            active_sessions[user_id] = True
            parts = message.content.split(" ")
            if len(parts) != 3:
                await message.channel.send(
                    "Please write correctly: **@tekken8-bot <name_character> <notation>**"
                )
                return
            notation, char_name = parts[2], parts[1]
            async with message.channel.typing():
                data = await finding_move(notation, char_name)
                if isinstance(data, dict):
                    msg_embed = draw_find_move(data, notation, char_name)
                    await message.reply(embeds=msg_embed)
                else:
                    await message.reply("Failed to get data")
    except Exception:
        print(traceback.format_exc())
        await message.reply("Failed to get data")
    finally:
        del active_sessions[user_id]


@bot.tree.command(name="find", description="Find moveset using notation")
@app_commands.describe(char_name="Character name to find", notation="Notation to find")
async def find(interaction: discord.Interaction, char_name: str, notation: str):
    await interaction.response.defer()
    try:
        data = await finding_move(notation, char_name)
        if isinstance(data, dict):
            msg_embed = draw_find_move(data, notation, char_name)
            await interaction.followup.send(embeds=msg_embed, silent=True)
            return
        else:
            await interaction.followup.send(f"Error: {data}", silent=True)
            return
    except Exception:
        print(traceback.format_exc())
        await interaction.followup.send(f"Failed to get data", silent=True)


bot.run(TOKEN)
