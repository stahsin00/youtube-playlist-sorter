import os

from dotenv import load_dotenv

import openai

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


load_dotenv()

CLIENT_SECRETS_FILE = os.getenv('CLIENT_SECRETS_PATH')
SCOPES = [os.getenv('YOUTUBE_API_SCOPES')]
PLAYLIST_ID = os.getenv('PLAYLIST_ID')
TEST_PLAYLIST_ID = os.getenv('TEST_PLAYLIST_ID')

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


def make_categories(youtube):
    prompt = ''

    prompt += 'Given the set of video titles, come up with playlist titles that all of the videos can be categorized into. Try to be broad with the categories such as \"Game Development\" or \"Art\" while limiting too much overlap between them. The video titles are as follows: '

    videos = get_all_playlist_videos(youtube,PLAYLIST_ID)
    prompt += videos

    return get_openai_response(prompt)


def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=8080, prompt='consent')

    return build('youtube', 'v3', credentials=credentials)


def add_video_to_playlist(youtube, playlist_id, video_id):
    request_body = {
        'snippet': {
            'playlistId': playlist_id,
            'resourceId': {
                'kind': 'youtube#video',
                'videoId': video_id
            }
        }
    }

    try:
        youtube.playlistItems().insert(part="snippet", body=request_body).execute()
    except Exception as e:
        print(f"Error: {e}")


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


def get_playlist_videos(youtube, playlist_id):
    max_results=50
    
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=max_results
    )
    response = request.execute()

    videos = ''
    items = response.get('items', [])
    for item in items:
        videos += ('\"' + item['snippet']['title'] + '\"; ')

    return videos


def get_all_playlist_videos(youtube, playlist_id):
    videos = ''

    max_results=50
    page_token = None

    while True:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=max_results,
            pageToken=page_token
        )
        response = request.execute()

        for item in response.get('items', []):
            videos += ('\"' + item['snippet']['title'] + '\"; ')

        page_token = response.get('nextPageToken')
        if not page_token:
            break

    return videos


def get_and_add_video(youtube, playlist_id):
    max_results=5
    
    try:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=max_results
        )
        response = request.execute()

        items = response.get('items', [])
        for item in items:
            video_id = item['snippet']['resourceId']['videoId']
            print(item['snippet']['title'])
            add_video_to_playlist(youtube, TEST_PLAYLIST_ID, video_id)

    except Exception as e:
        print(f"Error: {e}")


def main():
    youtube = get_authenticated_service()
    #print_playlist_videos(youtube,PLAYLIST_ID)
    #response = get_openai_response("hello! im just testing api calls")
    #print(response)
    #get_and_add_video(youtube, PLAYLIST_ID)
    response = make_categories(youtube)
    print(response)

main()