# youtube-playlist-sorter

#### YouTube Playlist Sorter is a Python-based script to automate the categorization of YouTube videos into playlists based on their content. It uses YouTube Data API and OpenAI's GPT-3.5 Turbo model to fetch videos from a specified YouTube playlist, analyze their titles and descriptions, and organize them into new or existing playlists based on generated or user-defined categories.

## Features
- Video Fetching: Automatically fetches videos from the user's YouTube playlists.
- Automatic Category Selection: Uses OpenAI's GPT model to generate categories based on video titles.
- Manual Category Selection: Users can manually input categories for organizing videos.
- Playlist Management: Creates new playlists and moves videos into appropriate categories.
- Interactive CLI: Provides a basic command-line interface for category selection and user feedback.

## Instructions

### Prerequisites
- Python 3.6+
- A Google account with access to the YouTube Data API

### Environmental Variables
CLIENT_SECRETS_PATH='path/to/client_secrets.json'  
YOUTUBE_API_SCOPES='https://www.googleapis.com/auth/youtube'  
PLAYLIST_ID='your_default_playlist_id'  
SAMPLE_PLAYLIST_ID='your_sample_playlist_id'  
OPENAI_API_KEY='your_openai_api_key'  

### API
- Enable YouTube Data API and obtain the necessary files from Google Developers Console
- Obtain an OpenAI API key for using GPT-3.5 Turbo model

## Usage
`python main.py`

## Next Steps
- Better Error Handling and Logging
- Quota and API Rate Limit Management
- Batch OpenAI Categorization Requests
- Research more Categorization Methods
- Schedule Periodic Automatic Sorting
- Optimization
