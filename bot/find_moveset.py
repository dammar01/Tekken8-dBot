import discord, os, traceback, httpx
from dotenv import load_dotenv

load_dotenv(override=True)
HOST = os.getenv("HOST")


async def finding_move(notation: str, char_name: str):
    """Fetches move data from the specified host."""
    url = f"{HOST}/findmove"
    print(f"Trying to find move at {url}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={"character_name": char_name, "notation": notation},
                timeout=60,
            )
        if response.status_code == 200:
            return response.json()
        return {"error": "Failed to fetch data"}
    except httpx.RequestError as e:
        print(traceback.format_exc())
        return {"error": f"Request failed: {str(e)}"}
    except httpx.TimeoutException:
        return {"error": "Request timed out, please try again."}


def draw_find_move(data: dict, notation: str, char_name: str):
    """Creates Discord embeds for the main and similar movesets."""

    def add_move_fields(embed: discord.Embed, move_data: dict):
        """Adds fields for move details to the provided embed."""
        details = (
            f"**Moveset**: {move_data['moveset']}\n"
            f"**Name move**: {move_data['name_move']}\n"
            f"**Startup**: {move_data['startup']}\n"
            f"**Hit Properties**: {move_data['hit_properties']}\n"
            f"**Damage**: {move_data['damage']}\n"
            f"**On Block**: {move_data['on_block']}\n"
            f"**On Hit**: {move_data['on_hit']}\n"
            f"**Notes**: {move_data['notes']}\n"
        )
        embed.add_field(name="", value=details, inline=False)

    # Check for errors in data
    if "error" in data:
        return [
            discord.Embed(
                title="Error", color=discord.Color.red(), description=data["error"]
            )
        ]

    # Primary moveset embed
    main_move_data = data["data"][0] if isinstance(data["data"], list) else data["data"]
    main_embed = discord.Embed(
        title=f"Moveset for {main_move_data['moveset'].split('-')[0]}",
        color=discord.Color.blue(),
    )
    if "error" not in data["data"]:
        add_move_fields(main_embed, main_move_data)
    else:
        main_embed.add_field(
            name="Not found", value="No matching moveset found.", inline=False
        )

    # Similar movesets embed
    similar_embed = discord.Embed(
        title=f"Similar movesets for {char_name}-{notation}",
        color=discord.Color.green(),
    )
    if "error" not in data["similiar"]:
        for move in data["similiar"]:
            add_move_fields(similar_embed, move)
    else:
        similar_embed.add_field(
            name="Not found", value="No similar movesets found.", inline=False
        )

    return [main_embed, similar_embed]
