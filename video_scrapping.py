import os
import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime
import configparser

# YouTube API Key
config = configparser.ConfigParser()
config.read('config.ini')
api_key = config.get('API', 'key')

# Threshold for API usage (adjust as needed)
usage_threshold = 90  # Set to the percentage of your free quota limit

# Initialize YouTube API
youtube = build("youtube", "v3", developerKey=api_key)

# Function to search for a YouTube channel based on user input
def search_channel():
    user_query = input("Enter the name of the YouTube channel: ")

    # Use the search endpoint to find channels
    search_response = youtube.search().list(
        part="snippet",
        q=user_query,
        type="channel",
        maxResults=5  # Adjust as needed
    ).execute()

    # Display search results and let the user choose a channel
    print("Search Results:")
    for idx, item in enumerate(search_response.get("items", [])):
        print(f"{idx + 1}. {item['snippet']['title']}")

    selected_index = int(input("Enter the number of the channel you want to fetch data from: ")) - 1

    if 0 <= selected_index < len(search_response["items"]):
        selected_channel_id = search_response["items"][selected_index]["id"]["channelId"]
        return selected_channel_id, search_response["items"][selected_index]["snippet"]["title"]
    else:
        print("Invalid selection. Exiting.")
        return None, None

# Function to get video information
def get_video_info(channel_id, channel_name, max_results=50):
    # Fetch video information
    videos = youtube.search().list(
        part="id",
        channelId=channel_id,
        order="date",
        type="video",
        maxResults=max_results
    ).execute()

    video_data = []

    for video in videos['items']:
        video_id = video['id']['videoId']
        video_info = youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        ).execute()

        # Extract information
        video_link = f"https://www.youtube.com/watch?v={video_id}"
        title = video_info['items'][0]['snippet']['title']
        likes = int(video_info['items'][0]['statistics']['likeCount'])
        thumbnail_url = video_info['items'][0]['snippet']['thumbnails']['default']['url']

        # Store data in a dictionary
        video_dict = {
            'Video Link': video_link,
            'Title': title,
            'Likes': likes,
            'Thumbnail URL': thumbnail_url
        }

        # Append dictionary to the list
        video_data.append(video_dict)

    # Create a DataFrame from the list of dictionaries
    df = pd.DataFrame(video_data)

    # Save DataFrame to an Excel file with channel name and current date
    date_str = datetime.now().strftime("%Y%m%d%H%M%S")
    excel_file = f"{channel_name}_{date_str}.xlsx"
    df.to_excel(excel_file, index=False)
    print(f"Data saved to {excel_file}")

if __name__ == "__main__":
    # Search for a YouTube channel based on user input
    selected_channel_id, selected_channel_name = search_channel()

    if selected_channel_id:
        # Fetch video information for the selected channel
        get_video_info(selected_channel_id, selected_channel_name)
