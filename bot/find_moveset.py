from dotenv import load_dotenv
import os, httpx, discord, traceback

load_dotenv(override=True)
HOST = os.getenv("HOST")


async def finding_move(notation: str, char_name: str):
    url = HOST + "/findmove"
    print(f"Trying to find move in {url}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={"character_name": char_name, "notation": notation},
                timeout=60,
            )
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {"error": "Failed to fetch data"}
    except httpx.RequestError as e:
        print(traceback.format_exc())
        return {"error": f"Failed to fetch data, {str(e)}"}
    except httpx.TimeoutException:
        return {"error": "The request timed out. Please try again later."}


def draw_find_move(data: dict, notation: str, char_name: str):
    def field(embed: discord.Embed, move_data: dict):
        msg = f"**Moveset**: {move_data["moveset"]} \n"
        msg += f"**Name move**: {move_data["name_move"]} \n"
        msg += f"**Startup**: {move_data["startup"]} \n"
        msg += f"**Hit Properties**: {move_data["hit_properties"]} \n"
        msg += f"**Damage**: {move_data["damage"]} \n"
        msg += f"**On Block**: {move_data["on_block"]} \n"
        msg += f"**On Hit**: {move_data["on_hit"]} \n"
        msg += f"**Notes**: {move_data["notes"]} \n\n\n"
        embed.add_field(name="", value=msg, inline=False)

    if "error" in data:
        err = discord.Embed(
            title=f"**Error**",
            color=discord.Color.red(),
        )
        err.add_field(
            name="Not found",
            value=f"{data['error']}",
            inline=False,
        )
        return [err]

    move_data = data["data"][0] if isinstance(data["data"], list) else data["data"]
    similiar_data = data["similiar"]

    # Create matching embed
    if "error" not in data["data"]:
        matching_embed = discord.Embed(
            title=f"**Moveset for {move_data['moveset'].split("-")[0]}**",
            color=discord.Color.blue(),
        )
        field(matching_embed, move_data)
    else:
        matching_embed = discord.Embed(
            title=f"**Moveset for {move_data['param']['character_name']}-{move_data['param']['notation']}**",
            color=discord.Color.blue(),
        )
        matching_embed.add_field(
            name="Not found",
            value="No matching moveset found.",
            inline=False,
        )

    if "error" not in data["similiar"]:
        # Create similar embed
        similar_embed = discord.Embed(
            title=f"**Similar movesets for {similiar_data[0]['moveset'].split("-")[0]}-{notation}**",
            color=discord.Color.green(),
        )
        for similiar in similiar_data:
            field(similar_embed, similiar)
    else:
        similar_embed = discord.Embed(
            title=f"**Similar movesets for {move_data['param']['character_name']}-{notation}**",
            color=discord.Color.green(),
        )
        similar_embed.add_field(
            name="Not found",
            value="No similar movesets found.",
            inline=False,
        )

    return [matching_embed, similar_embed]
