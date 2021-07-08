import discord
import os
import subprocess
import sys

from music import Music


try:
  subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", 'discord.py[voice]'])
except subprocess.CalledProcessError:
  print("Discord Voice module already installed!")

class Bot(discord.Client):
  def __init__(self):
    super().__init__(intents=discord.Intents.all())

    self.PREFIX = '*'
    self.BOT_TOKEN = os.environ['TOKEN']
    self.musicBot = Music()


  def run(self):
    super().run(self.BOT_TOKEN, reconnect=True)
  
  async def on_ready(self):
    print(f'We have logged in as {self.user}')

  async def on_message(self, message):
    if message.author == self.user:
      return

    if message.content.startswith(self.PREFIX + 'hello'):
      await message.channel.send('Hello!' + " " + message.author.name)

    elif message.content.startswith(self.PREFIX + "music" + " " +  "play"):
      await self.musicBot.playSong(self,message)
    
    elif message.content.startswith(self.PREFIX + "music" + " " +  "stop"):
      await self.musicBot.stopSong(message)
    
  async def on_member_join(self, member):
    join_embed = discord.Embed(title = "Welcome!", description = "Enjoy your stay but do adhere to the following rules!", colour = discord.Colour.orange)

    await member.dm_channel.send(embed = join_embed)
        

bot = Bot()
