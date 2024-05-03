import os
import random

from dotenv import load_dotenv
from tqdm import tqdm

from youtube_api import get_authenticated_service, get_playlists, create_playlist, get_playlist_videos, move_video, add_video_to_playlist
from openai_api import place_in_category

load_dotenv()

CLIENT_SECRETS_FILE = os.getenv('CLIENT_SECRETS_PATH')
SCOPES = [os.getenv('YOUTUBE_API_SCOPES')]

PLAYLIST_ID = os.getenv('PLAYLIST_ID')
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


def sample_videos(videos, sample_size = 50):
    return random.sample(videos, min(sample_size, len(videos)))


def create_sample(youtube, videos, sample_size = 50):
    sample = sample_videos(videos, sample_size)

    for video in tqdm(sample, desc="Collecting sample."):
        add_video_to_playlist(youtube, SAMPLE_PLAYLIST_ID, video['snippet']['resourceId']['videoId'])

    return sample


def categorize(youtube, videos, playlists):
    categories_string = ', '.join(f'"{category}"' for category in categories)

    try:
        for video in tqdm(videos, desc="Processing videos"):
            response_cat = place_in_category(video['snippet'], categories_string, OPENAI_API_KEY)

            if response_cat not in categories:
                response_cat = "Other"

            if response_cat not in playlists:
                id = create_playlist(youtube, response_cat)
                playlists[response_cat] = id

            move_video(youtube, video['snippet']['resourceId']['videoId'], video['id'], playlists[response_cat])

        print("Processing complete.")
    except Exception as e:
        print(f"Error: {e}")


def main():
    max_allowed = 50

    youtube = get_authenticated_service(CLIENT_SECRETS_FILE, SCOPES)

    use_sample = input("Would you like to work with a sample? (Y/N): ").strip().lower()

    while use_sample not in ["y","n"]:
        print("Invalid input. Please enter 'Y' or 'N'.")
        use_sample = input("Would you like to work with a sample? (Y/N): ").strip().lower()

    if use_sample == "y":
        videos = get_playlist_videos(youtube, PLAYLIST_ID)
        videos = create_sample(youtube, videos)
        print("Sample collected.")
    else:
        videos = get_playlist_videos(youtube, PLAYLIST_ID, max_allowed)

    # TODO : Generate category from video info

    playlists = get_playlists(youtube, categories)

    categorize(youtube, videos, playlists)


if __name__ == "__main__":
    main()