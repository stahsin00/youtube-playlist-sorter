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

    videos = get_all_playlist_videos(youtube,PLAYLIST_ID)
    prompt += videos

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

def categorize_playlist_videos(youtube, playlist_id):
    max_results=5
    
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=max_results
    )
    response = request.execute()

    categories_string = get_categories()

    items = response.get('items', [])
    for item in items:
        response = place_in_category(item['snippet'], categories_string)
        print(f"\"{item['snippet']['title']}\": {response}")
        user_input = input("Press Y to continue or N to exit: ")
        user_input = user_input.upper()
        if (user_input == 'N'):
            return


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
    #response = make_categories(youtube)
    #print(response)
    #print(get_categories())
    categorize_playlist_videos(youtube,PLAYLIST_ID)

main()