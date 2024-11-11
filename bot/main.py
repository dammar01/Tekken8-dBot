import discord, os, traceback, requests, asyncio, io
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from find_moveset import finding_move, draw_find_move
from combo_maker import get_img_combo

# Load environment variables
load_dotenv(override=True)
TOKEN = os.getenv("DISCORD_TOKEN")
HOST = os.getenv("HOST")

# Setup bot and intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

# Active sessions for user requests
active_sessions = {}


async def check_connection():
    """Checks if the host connection is available."""
    try:
        response = requests.get(HOST, timeout=5)
        if response.ok and "detail" in response.json():
            print(f"Connected to host: {HOST}")
            return True
    except requests.RequestException as e:
        print(f"Error connecting to {HOST}: {e}")
    return False


@bot.event
async def on_ready():
    """Bot initialization on login."""
    await bot.tree.sync()
    while not await check_connection():
        print("Retrying connection in 10 seconds...")
        await asyncio.sleep(10)
    print(f"Logged in as {bot.user}")


async def handle_request_error(interaction, msg):
    """Handles and logs errors for interactions."""
    print(traceback.format_exc())
    await interaction.followup.send(msg, silent=True)


async def validate_message(message, channel_name, min_parts):
    """Validates if a message is correctly structured for a request."""
    if message.channel.name != channel_name or bot.user not in message.mentions:
        return False
    if len(message.content.split(" ")) < min_parts:
        await message.reply(
            f"Incorrect format. Check usage instructions for {channel_name}."
        )
        return False
    return True


async def get_response_embed(title, color, description=None, image=None):
    """Creates an embed with optional image attachment."""
    embed = discord.Embed(title=title, color=color)
    if description:
        embed.add_field(name="", value=description, inline=False)
    if image:
        embed.set_image(url=image)
    return embed


async def command_on_message(message, parts):
    if await validate_message(message, "find-moveset", 3):
        notation, char_name = parts[2], parts[1]
        async with message.channel.typing():
            data = await finding_move(notation, char_name)
            if isinstance(data, dict):
                await message.reply(embed=draw_find_move(data, notation, char_name))
            else:
                await message.reply("Failed to get data")
    elif await validate_message(message, "combo-maker", 4):
        notation, char_name, starter_frame = (
            parts[2],
            parts[1],
            parts[3].lower() in ["true", "1", "yes", "y"],
        )
        async with message.channel.typing():
            img = await get_img_combo(char_name, notation, starter_frame)
            if isinstance(img, dict):
                embed = await get_response_embed(
                    "Error when drawing notation", discord.Color.red(), img["error"]
                )
                await message.reply(embed=embed)
            else:
                file = discord.File(fp=img, filename="notation.png")
                embed = await get_response_embed(
                    "Your combo notation image",
                    discord.Color.blue(),
                    image="attachment://notation.png",
                )
                await message.reply(embed=embed, file=file)


@bot.event
async def on_message(message):
    """Processes user messages and executes find or combo commands."""
    if message.author == bot.user:
        return

    user_id = message.author.id
    if user_id in active_sessions:
        await message.reply("Your previous request is still processing. Please wait.")
        return

    try:
        active_sessions[user_id] = True
        parts = message.content.split(" ")
        await command_on_message(message, parts)
    except Exception:
        print(traceback.format_exc())
        await message.reply("Failed to get data")
    finally:
        active_sessions.pop(user_id, None)


@bot.tree.command(
    name="find", description="Find moveset using name character and notation"
)
@app_commands.describe(char_name="Character name to find", notation="Notation to find")
async def find(interaction: discord.Interaction, char_name: str, notation: str):
    """Handles the find command to retrieve move data."""
    if interaction.channel.name != "find-moveset":
        error_embed = discord.Embed(
            title="Command Error",
            description="Use find-moveset channel to use this command!",
            color=discord.Color.red(),
        )
        await interaction.response.send_message(embed=error_embed, ephemeral=True)
        return
    await interaction.response.defer()
    try:
        data = await finding_move(notation, char_name)
        if isinstance(data, dict):
            await interaction.followup.send(
                embeds=draw_find_move(data, notation, char_name), silent=True
            )
        else:
            await interaction.followup.send("Failed to get data", silent=True)
    except Exception:
        await handle_request_error(interaction, "Failed to retrieve data")


@bot.tree.command(
    name="make-combo", description="Making combo using name character and notation"
)
@app_commands.describe(
    char_name="Character name to find",
    notation="Notation to find",
    draw_starter_frame="Drawing starter frame (default True)",
)
async def make_combo(
    interaction: discord.Interaction,
    char_name: str,
    notation: str,
    draw_starter_frame: bool = True,
):
    """Handles the make-combo command to generate combo images."""
    if interaction.channel.name != "combo-maker":
        error_embed = discord.Embed(
            title="Command Error",
            description="Use combo-maker channel to use this command!",
            color=discord.Color.red(),
        )
        await interaction.response.send_message(embed=error_embed, ephemeral=True)
        return
    await interaction.response.defer()
    try:
        img = await get_img_combo(char_name, notation, draw_starter_frame)
        if isinstance(img, dict):
            embed = await get_response_embed(
                "Error when drawing notation", discord.Color.red(), img["error"]
            )
            await interaction.followup.send(embed=embed, silent=True)
        else:
            file = discord.File(fp=img, filename="notation.png")
            embed = await get_response_embed(
                "Your combo notation image",
                discord.Color.blue(),
                image="attachment://notation.png",
            )
            await interaction.followup.send(embed=embed, file=file)
    except Exception:
        await handle_request_error(interaction, "Failed to generate combo image")


# Run bot
bot.run(TOKEN)
