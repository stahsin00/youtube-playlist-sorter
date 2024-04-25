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

categories = [
    "Mathematics and Algorithms",
    "Game Development and Game Design",
    "Coding and Development",
    "Hacking and Cybersecurity",
    "Web Development",
    "AI and Machine Learning",
    "Science and Technology",
    "Space and Astronomy",
    "Art and Illustration",
    "Writing, Storytelling, and Worldbuilding",
    "Music and Soundscapes",
    "Nature and Gardening",
    "Travel and Exploration",
    "Culture, Traditions, and History",
    "Mythology and Folklore",
    "Lifestyle, Productivity, and Wellness",
    "Popular Culture, Film, and Media",
    "Human Mind and Behavior",
    "Other"
    ]


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

    # TODO
    #videos = get_all_playlist_videos(youtube,PLAYLIST_ID)
    #prompt += videos

    return get_openai_response(prompt)


def get_categories():
    categories_string = ''
    for category in categories:
        categories_string += (f'\"{category}\", ')
    return categories_string


def place_in_category(snippet, categories_string):
    prompt = (f"Given the following list of categories: \[{categories_string}\], in which category would you place a video with the following info: ")

    video_info = (f"\[title: {snippet['title']}, description: {snippet['description']}\]")
    prompt += video_info

    prompt += ". Reply with only the category name and no other explanation."

    return get_openai_response(prompt)


def count_categorized_playlist_videos(youtube, playlist_id):
    categories_dict = {}
    categories_string = get_categories()

    videos = get_playlist_videos(youtube, playlist_id)

    try:
        for video in videos:
            response_cat = place_in_category(video['snippet'], categories_string)
            if response_cat in categories_dict:
                categories_dict[response_cat] += 1
            else:
                categories_dict[response_cat] = 1
    except Exception as e:
        print(f"Error: {e}")

    for key, value in categories_dict.items():
        print(f"\"{key}\" : {value}")


def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=8080, prompt='consent')

    return build('youtube', 'v3', credentials=credentials)


def get_playlists(youtube, max_allowed = 500):
    playlists = []

    max_results=50
    page_token = None

    try: 
        while max_allowed > 0:
            current_batch_size = min(max_results, max_allowed)
            max_allowed -= current_batch_size

            request = youtube.playlists().list(
                part="snippet",
                mine=True,
                maxResults=current_batch_size,
                pageToken=page_token
            )
            response = request.execute()

            items = response.get('items', [])
            playlists.extend({'id':item['id'],'snippet':item['snippet']} for item in items)

            page_token = response.get('nextPageToken')
            if not page_token:
                break
    except Exception as e:
        print(f"Error: {e}")

    return playlists


def create_playlist(youtube, title):
    request_body = {
        'snippet': {
            'title': title
        },
        'status': {
            'privacyStatus': 'private'
        }
    }

    try:
        response = youtube.playlists().insert(part='snippet,status', body=request_body).execute()
        return response['id']
    except Exception as e:
        print(f"Error: {e}")
        return None


def get_playlist_videos(youtube, playlist_id, max_allowed = 500):
    videos = []

    max_results=50
    page_token = None

    try: 
        while max_allowed > 0:
            current_batch_size = min(max_results, max_allowed)
            max_allowed -= current_batch_size

            request = youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=current_batch_size,
                pageToken=page_token
            )
            response = request.execute()

            items = response.get('items', [])
            videos.extend({'id':item['id'],'snippet':item['snippet']} for item in items)

            page_token = response.get('nextPageToken')
            if not page_token:
                break
    except Exception as e:
        print(f"Error: {e}")

    return videos


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


def remove_video_from_playlist(youtube, playlistitem_id):
    try:
        youtube.playlistItems().delete(id=playlistitem_id).execute()
    except Exception as e:
        print(f"Error: {e}")


def main():
    youtube = get_authenticated_service()
    #videos = get_playlist_videos(youtube, PLAYLIST_ID, 1000)
    #print(len(videos))
    playlists = get_playlists(youtube)
    for playlist in playlists:
        print(playlist['snippet']['title'])

main()