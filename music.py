
import os
import discord
import json
import requests
from youtube_dl import YoutubeDL
import asyncio # for handling asynchronous coroutines

class Music:
  def __init__(self):

    self.playList = None # queue for playing multiple songs
    
  # Settings for the music bot
    self.MUSIC_TOKEN = os.environ['YOUTUBE_TOKEN']
    self.NUM_SONGS = 5
    self.SONG_NUM_LIST = list(range(1,self.NUM_SONGS + 1))
    self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
  
  def parseSong(self, song):
    """This function parses video titles from a youtube search and returns a discord Embed object to display in chat to the user"""

    # 
    music_request = f"https://youtube.googleapis.com/youtube/v3/search?part=snippet&maxResults={self.NUM_SONGS}&q={song}&type=video&key={self.MUSIC_TOKEN}"

    song_embed =  discord.Embed(title = "Music to play", description = "Select which song you want to play below (type a number):", colour = discord.Colour.green())

    self.all_results = json.loads(requests.get(music_request).text)["items"]
    
    for index,result in enumerate(self.all_results):

      vid_title = str(index + 1) + "." + " " + result["snippet"]["title"]
      vid_description = result["snippet"]["description"]

      if len(vid_description) < 1:
        vid_description = "N/A"

      song_embed.add_field(name = vid_title, value = vid_description, inline = False)
    
    return song_embed
  
  async def playSong(self, mainBot, message):
    in_voice = message.author.voice
    
    if in_voice is None:
      await message.channel.send("You are currently not in a voice channel!")
      return

    prefix = message.content[0]
    song = message.content.split(prefix + "music play ")[-1]

    music_embed = self.parseSong(song)
    await message.channel.send(embed = music_embed)

    # Waits for a reply from the user
    def check(msg):
      return msg.author == message.author and msg.channel == message.channel and int(msg.content) in self.SONG_NUM_LIST

    try:
    
      msg = await mainBot.wait_for('message', check=check, timeout = 15)
      await message.channel.send("Now playing: " + msg.content)

      try:
        self.voice_bot = await in_voice.channel.connect()
      except discord.errors.ClientException:
        print("Bot already in the voice channel!")
    

      current_song_url = "https://www.youtube.com/watch?v=" + self.all_results[int(msg.content) - 1]["id"]["videoId"]

      if not self.voice_bot.is_playing():

        with YoutubeDL(self.YDL_OPTIONS) as ydl:
          info = ydl.extract_info(current_song_url, download=False)
        
        URL = info['formats'][0]['url']
        self.voice_bot.play(discord.FFmpegPCMAudio(URL, **self.FFMPEG_OPTIONS))
        self.voice_bot.is_playing()

      else:
        await message.channel.send("Already playing song")
        return


    except asyncio.TimeoutError:
      await message.channel.send("Sorry, your request for the song timed out...")
  
  async def stopSong(self, message):
    """Function to stop the bot from 
    playing the currently playing song"""

    in_voice = message.author.voice

    if in_voice is None:
      await message.channel.send("Music cannot be stopped if no user is in the channel!")
      return

    try:

      if self.voice_bot.is_playing():
        self.voice_bot.stop()
      else:
        await message.channel.send("No song is currently being played!")
        
    except AttributeError:
      await message.channel.send("I am currently not in a voice channel.")

