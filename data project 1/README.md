## Data Project 1 - DS2002
- **Source 1 -->** Kaggle dataset of Top 100 Streamed Spotify Songs
    - link --> "https://www.kaggle.com/code/ludovicocuoghi/spotify-top-100-streamed-songs-analysis/input"
- **Source 2 -->** MuiscBrainz for API queries for each artist

#### Overall
- Uses Pandas to read in a .csv file and create a dataframe
- Uses the artists in this dataframe to query the MusicBrainz API and build a new dataframe
- Merges the two dataframes into one, cleans unecessary columns, runs analysis on this dataframe, then stores it as a SQL databse with sqlite
- Uses existing dataframe to build a return file for the user of choice types .csv, .json. sql

#### Running
- Done in Google Colab
- Ensure "Top 100 most streamed - Sheet1.csv" is in the content directory
- Run each code block in order
- Most information is in outputs (whats currently going on with the code, errors, etc.) with print statements (instead of comments)
- No local syntax errors
