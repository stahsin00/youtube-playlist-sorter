from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


def get_authenticated_service(client_secret_file, scopes):
    flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes)
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