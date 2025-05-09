import requests
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# for keeping tokens hidden but processible
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# discord setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)


# Flask API requests to answer user questions
async def send_flask_chat(question):

    url = f"http://34.48.125.135:5000/chat"  # GCP flask API endpoint
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "message": question
    }

    try:
        # process Flask's response
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result["reply"]
    except Exception as e:
        print(f"Gemini API error: {e}")
        return "Sorry, I need to take a quick break. Give me a sec and then ask again!"


# for chunking message into discord channel
async def send_long_message(channel, content):
    for i in range(0, len(content), 2000):
        await channel.send(content[i:i+2000])


# commmands
bot.remove_command("help")
@bot.command()
async def help(ctx):
    await ctx.send(f"Hello {ctx.author.name}! " \
                   "I am a chat bot, George, here to help answer all your questions! " \
                   "Although most bots lack current data, I am specialized in the masters, so ask away!")


# events
@bot.event
async def on_ready():
    print("Bot is running...")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Uh-oh, I don't know that command! Try '!help' to see how to interact with me!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    modified_message = "Here is the author of a query and the question: " + str(message.author) + " : " + message.content
    gemini_response = await send_flask_chat(modified_message)

    await send_long_message(message.channel, gemini_response)
            
    await bot.process_commands(message)
    
bot.run(BOT_TOKEN)
