### Overall
- Using Google Cloud Platform to publicly host a reachable chatbot
  - accessible with a UI browser-based frontend or as an API request for backends
- Utilizes flask with Gemini integration
- Misc...
  - screenshots of working examples
  - using bootstrap for nicer UI
  - Dataset Sources...
      - https://github.com/lucasgwartz/Masters/blob/main/Masters_Scores.xlsx
      - https://github.com/lucasgwartz/Masters/blob/main/Masters_Winners.xlsx
      - https://github.com/lucasgwartz/Masters/blob/main/Most_Victories.xlsx
  - there does seem to be some context issues with Gemini, probably because all the text it has to process at once. fairly unavoidable
  - Discord...
    - a locally working discord bot version of the chatbot
    - "discord_bot.py" must be running locally and have the bot imported. Screenshots shown to verify the code (as running locally is a pain)

### Documentation
- Endpoint --> http://34.48.125.135:5000
  - This is the homepage (sparse)
  - To reach the chatbot, go down the /chat route
- Supports post requests via the chat route
  - http://34.48.125.135:5000/chat
  - Requests Requirements...
    - headers --> "Content-Type": "application/json"
    - data --> "message": question
  - Managing the Response...
    - in the form of ... {"reply": bot_reply}
    - so get the result as json with ... result["reply"]
