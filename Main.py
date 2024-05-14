import sys
sys.dont_write_bytecode = True
import discord
import Processor

from colorama import Fore, Back, Style; from discord.ext import commands

bot = commands.Bot(command_prefix='.',intents=discord.Intents.all(), case_insensitive= True)

@bot.event
async def on_ready():
    bot.remove_command("help")
    await Processor.load(bot)
    print(Fore.MAGENTA + "{} has loaded successfully".format(bot.user) + Back.BLACK + Style.RESET_ALL)


bot.run("")