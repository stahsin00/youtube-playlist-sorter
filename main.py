import os
import random

from dotenv import load_dotenv
from tqdm import tqdm

from youtube_api import get_authenticated_service, get_playlists, create_playlist, get_playlist_videos, move_video, add_video_to_playlist
from openai_api import place_in_category, generate_categories

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
    updated_videos = []

    for video in tqdm(sample, desc="Collecting sample."):
        response = add_video_to_playlist(youtube, SAMPLE_PLAYLIST_ID, video['snippet']['resourceId']['videoId'])
        
        if response:
            updated_videos.append({'id':response['id'],'snippet':response['snippet']})

    return updated_videos


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


def make_categories_automatically(youtube, videos):
    global categories

    try:
        print("Generating categories.")
        videos = get_playlist_videos(youtube, PLAYLIST_ID)
        sample = sample_videos(videos)
        titles = [video['snippet']['title'] for video in sample]
        categories = generate_categories(titles, OPENAI_API_KEY).split('\n')
        print("Categories generated.")
    except Exception as e:
        print(f"Error: {e}")
        print("Failed to generate categories. Using default.")


def make_categories_manually():
    global categories

    categories = []

    while True:
        try:
            number_of_categories = int(input("How many categories do you want to enter? "))
            break
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    for i in range(number_of_categories):
        category = input(f"Enter category {i + 1}: ")
        categories.append(category)


def make_categories(youtube, videos, choice):
    if choice == "2":
        make_categories_automatically(youtube, videos)
    elif choice == "3":
        make_categories_manually()


def display_categories():
    print("The categories are: ")
    for i, category in enumerate(categories):
        print(f"{i+1}. {category}")


def edit_categories():
    global categories

    while True:
        try:
            display_categories()

            print("Which category would you like to edit?")
            category_index = int(input("Enter the number of the category: "))-1

            if not 0 <= category_index < len(categories):
                print("Invalid input.")
                continue

            print(f"Editing: \"{categories[category_index]}\"")
            categories[category_index] = input("Enter the new category: ").strip()
            break
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def finalize_categories():
    while True:
        display_categories()

        print("Proceed?")
        print("1: Proceed to next step")
        print("2: Edit categories")
        choice = input("Enter your choice (1 or 2): ").strip()

        if choice not in ["1", "2"]:
            print("Invalid input. Please enter '1' or '2'.")
            continue

        return choice


def select_categories(youtube, videos):
    while True:
        print("Select how to handle categories:")
        print("1: Use default categories")
        print("2: Automatically generate categories")
        print("3: Enter categories manually")
        choice = input("Enter your choice (1, 2, or 3): ").strip()

        if choice not in ["1", "2", "3"]:
            print("Invalid input. Please enter '1', '2', or '3'.")
            continue

        break

    make_categories(youtube, videos, choice)

    choice = finalize_categories()
    
    while choice == "2":
        edit_categories()
        choice = finalize_categories()


def main():
    max_allowed = 50
    videos = []

    # Authenticate and connect to YouTube
    youtube = get_authenticated_service(CLIENT_SECRETS_FILE, SCOPES)

    # Category selection and validation process
    select_categories(youtube, videos)
    while len(categories) <= 0:
        print("Must include atleast 1 category.")
        select_categories(youtube, videos)

    # Decision to work with a sample of videos or all videos
    use_sample = input("Would you like to work with a sample? (Y/N): ").strip().lower()
    while use_sample not in ["y","n"]:
        print("Invalid input. Please enter 'Y' or 'N'.")
        use_sample = input("Would you like to work with a sample? (Y/N): ").strip().lower()

    # Fetch and process videos based on user decision
    if use_sample == "y":
        if len(videos) == 0:
            videos = get_playlist_videos(youtube, PLAYLIST_ID)
        videos = create_sample(youtube, videos)
        print("Sample collected.")
    else:
        videos = get_playlist_videos(youtube, PLAYLIST_ID, max_allowed)

    # Fetch playlists and categorize videos
    playlists = get_playlists(youtube, categories)
    categorize(youtube, videos, playlists)


if __name__ == "__main__":
    main()