import sys
import os
import discord
import yt_dlp as youtube_dl
from discord.ext import commands
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTextEdit,
    QFileDialog,
)
from PyQt5.QtCore import QThread, pyqtSignal

# Function to load the bot token from a file
def load_token():
    try:
        with open('TOKEN.DISCORD.BOT.txt', 'r') as file:
            token = file.read().strip()
            return token
    except FileNotFoundError:
        print("ERROR: TOKEN.DISCORD.BOT.txt file not found.")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

queue = []
announcement_channel_id = None  # Store the announcement channel ID

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


async def play_next(ctx):
    if queue:
        next_song = queue.pop(0)
        player = await YTDLSource.from_url(next_song, loop=bot.loop)
        ctx.voice_client.play(player, after=lambda e: bot.loop.create_task(play_next(ctx)))
        await ctx.send(f"**Now playing:** {player.title}")

        # Announce in the set channel
        if announcement_channel_id:
            channel = bot.get_channel(announcement_channel_id)
            if channel:
                await channel.send(f"**Now playing in {ctx.guild.name}:** {player.title}")
    else:
        await ctx.send("The playlist is empty.")


@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send(f"{ctx.message.author.name} is not connected to a voice channel")
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
        await ctx.send("Bot has left the voice channel.")
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='play', help='To add a song to the playlist')
async def play(ctx, url: str = None):
    voice_channel = ctx.message.author.voice.channel if ctx.message.author.voice else None
    if voice_channel:
        if ctx.voice_client is None:
            await voice_channel.connect()
        elif ctx.voice_client.channel != voice_channel:
            await ctx.voice_client.move_to(voice_channel)

    if url:
        queue.append(url)
        await ctx.send(f"**Added to queue:** {url}")
        if not ctx.voice_client.is_playing():
            await play_next(ctx)
    elif ctx.message.attachments:
        try:
            attachment = ctx.message.attachments[0]
            if attachment.filename.endswith(('.mp3', '.wav')):
                file_path = f"downloads/{attachment.filename}"
                await attachment.save(file_path)
                queue.append(file_path)
                await ctx.send(f"**Added to queue:** {attachment.filename}")
                if not ctx.voice_client.is_playing():
                    await play_next(ctx)
            else:
                await ctx.send("Please attach a valid .mp3 or .wav file.")
        except Exception as e:
            await ctx.send("There was an issue adding the attached file to the queue.")
    else:
        await ctx.send("Please provide a URL or attach an audio file.")


@bot.command(name='stop', help='Stops the whole playlist and disconnects the bot')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        queue.clear()
        voice_client.stop()
        await ctx.send("Stopped the playlist and cleared the queue.")
    if voice_client.is_connected():
        await voice_client.disconnect()
        await ctx.send("Bot has left the voice channel.")
    else:
        await ctx.send("No audio is playing.")


@bot.command(name='skip', help='Skips the current song')
async def skip(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Skipped the current song.")
        await play_next(ctx)
    else:
        await ctx.send("No audio is playing.")


@bot.command(name='rem', help='Removes a particular song from the playlist')
async def rem(ctx, index: int):
    if 0 < index <= len(queue):
        removed_song = queue.pop(index - 1)
        await ctx.send(f"Removed song at position {index}: {removed_song}")
    else:
        await ctx.send(f"Invalid index. There are {len(queue)} songs in the queue.")


@bot.command(name='channel', help='Sets the channel for announcements')
async def set_channel(ctx, channel: discord.TextChannel):
    global announcement_channel_id
    announcement_channel_id = channel.id
    await ctx.send(f"Announcement channel set to: {channel.mention}")


@bot.command(name='commands', help='Lists all commands and supported links')
async def commands(ctx):
    help_text = (
        "**Available Commands:**\n"
        "!join - Tells the bot to join the voice channel\n"
        "!leave - To make the bot leave the voice channel\n"
        "!play <url or attach file> - To add songs to playlist and join the voice channel\n"
        "!stop - Stops the whole playlist and disconnects the bot\n"
        "!skip - Skips the active song\n"
        "!rem <index> - Removes a particular song from the playlist\n"
        "!channel <#channel> - Sets the channel for song announcements\n"
        "!commands - Lists all commands and supported links\n"
        "!creds - Lists the credits to the creators\n\n"
        "**Supported Links:**\n"
        "- YouTube\n"
        "- SoundCloud\n"
        "- Spotify (will attempt to find a YouTube equivalent)\n"
        "- Bandcamp\n"
        "- Attachments: .mp3, .wav"
    )
    await ctx.send(help_text)


@bot.command(name='creds', help='Lists the credits to the creators')
async def creds(ctx):
    creds_text = (
        "This bot was created by [Your Name or Team Name].\n"
        "Powered by discord.py, yt-dlp, and other open-source projects."
    )
    await ctx.send(creds_text)


class BotThread(QThread):
    update_log = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        token = load_token()  # Load the token from the file
        bot.run(token)

    def stop_bot(self):
        bot.loop.stop()
        self.quit()


class BotGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.bot_thread = None
        self.log_data = ""

    def initUI(self):
        self.setWindowTitle('Discord Bot GUI')
        self.setGeometry(100, 100, 500, 400)

        layout = QVBoxLayout()

        self.log_viewer = QTextEdit(self)
        self.log_viewer.setReadOnly(True)
        layout.addWidget(self.log_viewer)

        self.boot_button = QPushButton('Boot', self)
        self.boot_button.clicked.connect(self.toggle_bot)
        layout.addWidget(self.boot_button)

        self.export_button = QPushButton('Export Log', self)
        self.export_button.clicked.connect(self.export_log)
        layout.addWidget(self.export_button)

        self.setLayout(layout)

    def toggle_bot(self):
        if self.boot_button.text() == 'Boot':
            self.boot_button.setText('Booting up...')
            self.boot_button.setStyleSheet("background-color: yellow")
            self.boot_button.setEnabled(False)
            self.start_bot()
        elif self.boot_button.text() == 'Stop':
            self.stop_bot()

    def start_bot(self):
        self.bot_thread = BotThread()
        self.bot_thread.update_log.connect(self.update_log)
        self.bot_thread.finished.connect(self.on_bot_stopped)
        self.bot_thread.start()
        self.log("Starting bot...")
        self.boot_button.setText('Stop')
        self.boot_button.setStyleSheet("background-color: green")
        self.boot_button.setEnabled(True)

    def stop_bot(self):
        if self.bot_thread:
            self.bot_thread.stop_bot()
            self.log("Stopping bot...")
            self.boot_button.setText('Boot')
            self.boot_button.setStyleSheet("background-color: none")
            self.boot_button.setEnabled(True)

    def on_bot_stopped(self):
        self.log("Bot stopped.")
        self.boot_button.setText('Boot')
        self.boot_button.setStyleSheet("background-color: none")
        self.boot_button.setEnabled(True)

    def log(self, message):
        self.log_data += message + "\n"
        self.log_viewer.append(message)

    def export_log(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Log", "", "Log Files (*.log);;All Files (*)")
        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.log_data)
            self.log(f"Log exported to {file_path}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = BotGUI()
    gui.show()
    sys.exit(app.exec_())
