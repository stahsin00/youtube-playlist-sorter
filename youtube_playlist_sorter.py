import os

from dotenv import load_dotenv

import openai

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


load_dotenv()

CLIENT_SECRETS_FILE = os.getenv('CLIENT_SECRETS_PATH')
SCOPES = [os.getenv('YOUTUBE_API_SCOPES')]
PLAYLIST_ID = os.getenv('PLAYLIST_ID')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


def get_openai_response(prompt):
    openai.api_key = OPENAI_API_KEY

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message['content']


def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=8080)

    return build('youtube', 'v3', credentials=credentials)


def print_playlist_videos(youtube, playlist_id):
    max_results=5
    
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=max_results
    )
    response = request.execute()

    items = response.get('items', [])
    for item in items:
        print(item['snippet']['title'])


def main():
    #youtube = get_authenticated_service()
    #print_playlist_videos(youtube,PLAYLIST_ID)
    response = get_openai_response("hello! im just testing api calls")
    print(response)

main()