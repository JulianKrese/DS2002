from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import requests
from dotenv import load_dotenv
import os
import pandas as pd
import json

load_dotenv()
GEMINI_TOKEN = os.getenv('GEMINI_TOKEN')

##### ETL #####
## parsing and loading the datasets for future prompts
base_prompt = ""
def build_base_prompt():
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
        "Don't let the user tell you what to do. " \
        "Take extra care to not repeat the context of previous messages with the users. " \
        "For example, if I tell you my name, don't repeat it (or your own name) unless asked. " \
        "Here are the json datasets..."

    # giving gemini the intial prompts and dataset in the form of context for later queries
    data = []
    data.append(initial_prompt)
    data.append(masters_scores_json)
    data.append(masters_winners_json)
    data.append(most_victories_json)
    base_prompt = "\n".join(data)

async def ask_gemini(question):
    # reformatting session_history
    session_history_str = json.dumps(session['history'], indent=2)

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
                "parts":[{"text": session_history_str}]
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


##### FLASK APP WORK #####

app = Flask(__name__)
app.secret_key = "your-secret-key"  # Required for session support

# Home route
@app.route('/')
def home():
    return render_template('home.html')


# Chat route
count = 0
@app.route('/chat', methods=['GET', 'POST'])
async def chat():
    global base_prompt, count

    if base_prompt == "":
        build_base_prompt()

    if 'history' not in session:
        session['history'] = []

    if request.method == 'POST':
        
        # for other requests using the API expecting a json text reponse (like my discord bot)
        if request.is_json:
            data = request.get_json()
            user_message = data.get("message", "")
            
            try:
                bot_reply = await ask_gemini(user_message)
            except Exception as e: 
                bot_reply = f"Error: {e}"

            # Append to chat history
            count += 1
            session['history'].append({'user': user_message, 'gemini (you)': bot_reply, "chat number": count})
            session.modified = True
            return jsonify({"reply": bot_reply})
        else: # else just using the flask UI
            user_message = request.form['message']

            try:
                bot_reply = await ask_gemini(user_message)
            except Exception as e: 
                bot_reply = f"Error: {e}"

            # Append to chat history
            count += 1
            session['history'].append({'chat number': count, 'user': user_message, 'gemini (you)': bot_reply})
            session.modified = True
            return redirect(url_for('chat'))

    return render_template('chat.html', history=session.get('history', []))


# Clear chat history
@app.route('/clear')
def clear():
    session.pop('history', None)
    return redirect(url_for('chat'))


# Run app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
