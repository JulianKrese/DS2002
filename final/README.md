### Overall
- Using Google Cloud Platform to publicly host a reachable chatbot
  - accessible with a UI browser-based frontend or as an API request for backends
- Utilizes flask with Gemini integration
- Codebase Extras...
  - a locally working discord bot version of the chatbot
  - screenshots of working examples
  - using bootstrap for nicer UI
  - there does seem to be some context issues with Gemini, probably because all the text it gets to process at once. fairly unavoidable

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
