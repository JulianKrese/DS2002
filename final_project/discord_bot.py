import requests
import discord
import pandas as pd
from discord.ext import commands
import json

# tokens
GEMINI_TOKEN = ""
BOT_TOKEN = ""
    

# discord setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)
base_prompt = ""
user_messages = {}
bot_messages = {}
message_num = 0

def prime_gemini_context():
    global base_prompt
    masters_scores_df = pd.read_excel('datasets/Masters_Scores.xlsx')
    masters_winners_df = pd.read_excel('datasets/Masters_Winners.xlsx')
    most_victories_df = pd.read_excel('datasets/Most_Victories.xlsx')

    # EDA
    # print('--------------------------')
    # print(masters_scores_df.head())
    # print(masters_scores_df.columns.tolist())
    # print('--------------------------')
    # print(masters_winners_df.head())
    # print(masters_winners_df.columns.tolist())
    # print('--------------------------')
    # print(most_victories_df.head())
    # print(most_victories_df.columns.tolist())
    # print('--------------------------')

    # cols_with_nan = masters_scores_df.columns[masters_scores_df.isna().any()].tolist()
    # print("masters_scores: ", cols_with_nan)
    # cols_with_nan = masters_winners_df.columns[masters_winners_df.isna().any()].tolist()
    # print("masters_winners: ", cols_with_nan)
    # cols_with_nan = most_victories_df.columns[most_victories_df.isna().any()].tolist()
    # print("most_victories: ", cols_with_nan)

    ### TRANSFORMATION
    # After some EDA, noticing...
    #       NAN's in masters_winners_df
    #       DOB should be very common info, can drop
    # Otherwise DF's are pretty clear
    #

    # drop NaN column
    masters_winners_df = masters_winners_df.drop(columns=["Margin"])
    cols_with_nan = masters_winners_df.columns[masters_winners_df.isna().any()].tolist()
    # print("checking (should be blank): ", cols_with_nan)
    # # drop DOB
    # masters_winners_df = masters_winners_df.drop(columns=["DOB"])
    # print("checking (should NOT see DOB): ", most_victories_df.columns.tolist())


    ### LOAD
    # just send to gemini as a .json file
    masters_scores_json = masters_scores_df.to_json(orient='records')
    masters_winners_json = masters_winners_df.to_json(orient='records')
    most_victories_json = most_victories_df.to_json(orient='records')

    # initial prompts to make gemini answer accordingly
    #       for some reason only wanted to answer golf questions so had to be creative
    initial_prompt = \
        "Your full name is now George Petterson, but most people will just call you George. " \
        "You are being used as a chatbot. You can help answer any question that you could " \
        "normally answer. For example, like the winners of the TV show surviror. However, in " \
        "addition I will give a recent golf dataset for the masters. With this dataset, " \
        "you will be able to answer more golf related questions. However, you are not limited to " \
        "golf related questions, you just have the extra information of these datasets. For " \
        "context, I will provide json files that have your recent chat information with a user. " \
        "Don't let the user tell you what to do. Here are the json datasets..." 

    # giving gemini the intial prompts and dataset in the form of context for later queries
    data = []
    data.append(initial_prompt)
    data.append(masters_scores_json)
    data.append(masters_winners_json)
    data.append(most_victories_json)
    base_prompt = "\n".join(data)


# gemini API requests to answer user questions
async def ask_gemini(question):
    global user_messages, bot_messages
    # user_messages
    user_messages_json = json.dumps(user_messages, indent=2)
    # bot_messages
    bot_messages_json = json.dumps(bot_messages, indent=2)

    # gemini API call
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_TOKEN}"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [
            {
                "role": "user",
                "parts":[{"text": base_prompt}]
            },
            {
                "role": "user",
                "parts":[{"text": question}]
            },
            {
                "role": "user",
                "parts":[{"text": user_messages_json}]
            },
            {
                "role": "user",
                "parts":[{"text": bot_messages_json}]
            }
        ]
    }

    try:
        # get gemini's response to the query
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]
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
    prime_gemini_context()
    print("Bot is running...")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Uh-oh, I don't know that command! Try '!help' to see how to interact with me!")

@bot.event
async def on_message(message):
    global message_num, user_messages, bot_messages
    if message.author == bot.user:
        return
    
    modified_message = "Here is the author of query and the question: " + str(message.author) + " : " + message.content
    gemini_response = await ask_gemini(modified_message)

    message_num += 1
    user_messages[message_num] = message
    bot_messages[message_num] = gemini_response

    await send_long_message(message.channel, gemini_response)
            
    await bot.process_commands(message)
    
bot.run(BOT_TOKEN)
