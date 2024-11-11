# Tekken 8 Discord Bot

This is a Discord bot designed to help Tekken 8 players quickly find movesets and notations for their characters using the [Tekken8-API](https://github.com/dammar01/Tekken8-API). The bot provides features to search for moves based on notation and character names, and it retrieves detailed information about moves such as startup frames, damage, properties, and more.

## Features

- **Find Moveset**: Allows users to search for Tekken 8 movesets using a character's name and move notation.
- **Get Detailed Information**: For each move, the bot provides detailed information such as damage, startup frames, hit properties, on-block properties, and more.
- **Error Handling**: If the bot can't find a matching move or the user inputs incorrect data, it will provide error messages with helpful instructions.
- **Similar Movesets**: Suggests similar movesets in case the exact move is not found.

## Setup and Installation

### Prerequisites

Before running the bot, you need to set up and run the [Tekken8-API](https://github.com/dammar01/Tekken8-API) in your local.

### Installation Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/tekken8-discord-bot.git
   cd tekken8-discord-bot
   ```

2. Setup venv and activate:

   ```bash
   py -m venv venv
   venv\Scripts\activate
   ```

3. Setup venv:

   ```bash
   py -m venv venv
   ```

4. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Create a .env file in the project root and add the following:

   ```bash
   DISCORD_TOKEN=your-discord-bot-token
   HOST=tekken8-api-host-url
   ```

6. Running locally:
   ```bash
   py bot/main.py
   ```

## Contributing

Contributions are always welcome!

Feel free to customize any section to better fit your project structure!

## Feedback

If you have any feedback, please reach out to me at dammar.s011@gmail.com or DM me at instagram [@dmmrs_a](https://www.instagram.com/dmmrs_a/)

## Acknowledgements

- [WavuWiki](https://wavu.wiki/t/Main_Page)

## License

This project is licensed under the Mozilla Public License 2.0 (MPL-2.0). For more details, see the [LICENSE](LICENSE) file
