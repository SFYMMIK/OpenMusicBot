
# Discord Music Bot with GUI

This is a Discord music bot built using `discord.py`, `yt-dlp`, and `PyQt5`. The bot allows users to play music in a Discord voice channel, manage a playlist, and control the bot through a graphical user interface (GUI).

## Features

- **Join/Leave Voice Channel**: The bot can join and leave a voice channel on command.
- **Play Music**: Add songs to a playlist via URL or by uploading `.mp3` or `.wav` files.
- **Skip, Stop, and Remove Songs**: Control playback with commands to skip, stop, or remove songs from the playlist.
- **Announcements**: Set a specific channel where the bot will announce the currently playing song.
- **Graphical User Interface (GUI)**: Start, stop, and monitor the bot through a simple GUI application.

## Requirements

- Python 3.8+
- The following Python packages:
  - `discord.py`
  - `yt-dlp`
  - `PyQt5`

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/discord-music-bot.git
   cd discord-music-bot
   ```

2. **Install Dependencies:**
   ```bash
   pip install discord.py yt-dlp PyQt5
   ```

3. **Set Up Bot Token:**
   - Go to the [Discord Developer Portal](https://discord.com/developers/applications).
   - Create a new application and bot.
   - Copy the bot token.
   - Create a file named `TOKEN.DISCORD.BOT.txt` in the root directory.
   - Paste your Discord bot token into this file.

## Usage

### Running the Bot

To run the bot with the GUI, execute the following command:

```bash
python bot.py
```

The GUI will allow you to boot or stop the bot, and view or export logs.

### Bot Commands

- **`!join`**: Makes the bot join the voice channel you're currently in.
- **`!leave`**: Makes the bot leave the voice channel.
- **`!play <url or attach file>`**: Adds a song to the playlist. The bot joins the voice channel if it's not already in one.
- **`!stop`**: Stops the playlist and disconnects the bot from the voice channel.
- **`!skip`**: Skips the current song in the playlist.
- **`!rem <index>`**: Removes the song at the specified index from the playlist.
- **`!channel <#channel>`**: Sets the channel where the bot will announce the currently playing song.
- **`!commands`**: Displays a list of available commands and supported links.
- **`!creds`**: Shows credits for the bot's creation.

### Supported Links

- **YouTube**
- **SoundCloud**
- **Spotify** (will attempt to find a YouTube equivalent)
- **Bandcamp**
- **Attachments**: `.mp3`, `.wav` files

### GUI Features

- **Boot/Stop Bot**: Start and stop the bot from the GUI.
- **Log Viewer**: View real-time logs of the bot's activity.
- **Export Log**: Save the bot's logs to a file.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss your ideas.

## License

This project is licensed under the GPL-3.0 License. See the [LICENSE](LICENSE) file for details.
