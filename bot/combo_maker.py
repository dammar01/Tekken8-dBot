from dotenv import load_dotenv
import os, httpx, traceback
from io import BytesIO

load_dotenv(override=True)
HOST = os.getenv("HOST")


async def get_img_combo(
    char_name: str, notation: str, draw_starter_frame: bool | None = True
):
    url = HOST + "/notation"
    print(f"Trying to drawing combo {url}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={
                    "character_name": char_name,
                    "notation": notation,
                    "draw_starter_frame": draw_starter_frame,
                },
                timeout=60,
            )
            # Check if response is an image (status code 200 with image/png)
            if (
                response.status_code == 200
                and response.headers["content-type"] == "image/png"
            ):
                print("Image receiving..")
                # Load image from the response and send it as an attachment
                image_bytes = BytesIO(response.content)
                return image_bytes
            else:
                # Handle JSON error response
                print(traceback.format_exc())
                print("JSON receiving..")
                error_data = response.json()
                return error_data
    except httpx.RequestError as e:
        print(traceback.format_exc())
        return {"error": f"Failed to fetch data, {str(e)}"}
    except httpx.TimeoutException:
        return {"error": "The request timed out. Please try again later."}
