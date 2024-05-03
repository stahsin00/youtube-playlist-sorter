import os
import random

from dotenv import load_dotenv

from youtube_api import get_authenticated_service, get_playlists, create_playlist, get_playlist_videos, add_video_to_playlist
from openai_api import place_in_category

load_dotenv()

CLIENT_SECRETS_FILE = os.getenv('CLIENT_SECRETS_PATH')
SCOPES = [os.getenv('YOUTUBE_API_SCOPES')]
PLAYLIST_ID = os.getenv('PLAYLIST_ID')
TEST_PLAYLIST_ID = os.getenv('TEST_PLAYLIST_ID')
SAMPLE_PLAYLIST_ID = os.getenv('SAMPLE_PLAYLIST_ID')

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


def get_categories():
    categories_string = ', '.join(f'"{category}"' for category in categories)
    return categories_string


def sample_videos(videos, sample_size):
    return random.sample(videos, min(sample_size, len(videos)))


def count_categorized_playlist_videos(videos):
    categories_string = get_categories()
    categories_dict = {}

    try:
        for video in videos:
            response_cat = place_in_category(video['snippet'], categories_string, OPENAI_API_KEY)
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

    videos = get_playlist_videos(youtube, SAMPLE_PLAYLIST_ID, 1000)
    playlists = get_playlists(youtube, categories)


    #count_categorized_playlist_videos(videos)

    #this_sample = sample_videos(videos, 50)

    #for video in this_sample:
    #    add_video_to_playlist(youtube, SAMPLE_PLAYLIST_ID, video['snippet']['resourceId']['videoId'])


    #print(len(videos))
    #playlists = get_playlists(youtube)
    #for playlist in playlists:
    #    print(playlist['snippet']['title'])

    #id = create_playlist(youtube=youtube,title='test2')
    #print(id)

main()