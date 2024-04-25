import os

from dotenv import load_dotenv

from youtube_api import get_authenticated_service, get_playlists, create_playlist, get_playlist_videos
from openai_api import get_openai_response


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


def main():
    youtube = get_authenticated_service(CLIENT_SECRETS_FILE, SCOPES)
    #videos = get_playlist_videos(youtube, PLAYLIST_ID, 1000)
    #print(len(videos))
    playlists = get_playlists(youtube)
    for playlist in playlists:
        print(playlist['snippet']['title'])

    #id = create_playlist(youtube=youtube,title='test2')
    #print(id)

main()