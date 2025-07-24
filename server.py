import gradio as gr
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from collections import defaultdict
import os
from dotenv import load_dotenv
load_dotenv()

sp = None

id = None

# Tool

def auth_with_spotify():

    """
        It auths with the spotify and returns current user info to confirm the success of auth
    """
    global sp
    global id

    try:

        print("Client ID:", os.getenv("SPOTIPY_CLIENT_ID"))
        print("Client Secret:", os.getenv("SPOTIPY_CLIENT_SECRET"))
        print("Redirect URI:", os.getenv("SPOTIPY_REDIRECT_URI"))
        print("Scope:", os.getenv("SPOTIPY_SCOPE"))

        sp_oauth = SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope=os.getenv("SPOTIPY_SCOPE")
    )


        sp = spotipy.Spotify(auth_manager=sp_oauth)
        current_user = sp.current_user()

        if current_user.get("id") != None:
            id = current_user.get("id")

        return current_user

    except Exception as e:
        return f"error auth with spotify {e}"


# Tool

def get_artist_and_track(track_name):
    """
    Searches for a track and returns a list of dictionaries with artist name and track URI
    """
    if not sp:
        return "Please authenticate with Spotify first!"

    if not track_name.strip():
        return "Please enter a track name!"

    artist_song_list = []

    try:
        response = sp.search(q=f"track:{track_name}", type="track")
        items = response.get("tracks", {}).get("items", [])

        for item in items:
            artist = item["artists"][0]["name"] if item.get("artists") else None
            uri = item.get("uri")
            artist_song_list.append({"artist": artist, "uri": uri})

        return artist_song_list if artist_song_list else "No results found."
    except Exception as e:
        return f"Error occurred: {e}"


# Tool

def add_to_queue_song(uri_of_song):

    """
    Adds a song to the Spotify queue using its URI
    """

    if not sp:
        return "Please authenticate with Spotify first!"

    if not uri_of_song.strip():
        return "Please enter a track name!"

    try:
        sp.add_to_queue(uri_of_song)
        return "success adding song to the queue"

    except Exception as e:
        return f"error adding song to the queue, check if you have a active session error- {e}"


# Tool

def get_recently_played_songs(limit_song=5):
    """
    Retrieve the user's recently played tracks.
    
    Args:
        limit_song (int): Number of recent songs to retrieve.

    Returns:
        dict: Mapping of song names to artist names.
    """
    if not sp:
        return "Please authenticate with Spotify first!"

    if not limit_song:
        return "Please enter a number of songs"

    song_artist_map = {}

    try:
        res = sp.current_user_recently_played(limit=limit_song)
        items = res.get("items", [])

        if items:
            for item in items:
                track = item.get("track", {})
                song_name = track.get("name")
                artist_list = track.get("artists", [])

                artist_name = artist_list[0]["name"] if artist_list else "Unknown Artist"

                if song_name:
                    song_artist_map[song_name] = artist_name
        else:
            return "No recently played songs found."

        return song_artist_map

    except Exception as e:
        return f"Error retrieving recently played songs: {e}"
    

# Tool

def create_playlist(id, name, description="", public=True, collaborative=False):
    """
    Creates a playlist for the given user.

    Args:
        id (str): Spotify user ID.
        name (str): Name of the playlist (required).
        description (str, optional): Description of the playlist. Defaults to "".
        public (bool, optional): Whether the playlist is public. Defaults to True.
        collaborative (bool, optional): Whether the playlist is collaborative. Defaults to False.

    Keyword Args:
        Additional keyword arguments are not used in this function.

    Returns:
        str: Success or error message.
    """
    if not sp:
        return "Please authenticate with Spotify first!"

    if not id and name:
        return "Please enter id of user and playlist name"

    try:
        res = sp.user_playlist_create(id, name, description, public, collaborative)

        if res.get("name") is not None:
            return "playlist created success"
        else:
            return "error creating playlist"

    except Exception as e:
        return f"failed to create playlist error {e}"




# Tool

def get_playlist_name_and_id(limit_playlist=10):
    """
    Retrieve the user's playlists as a dictionary of {playlist_name: playlist_id}.
    Only returns playlists with both a name and an ID.
    """
    if not sp:
        return "Please authenticate with Spotify first!"

    try:
        playlists = sp.current_user_playlists(limit=limit_playlist)
        items = playlists.get("items", [])
        
        if not items:
            return "No playlists found."

        playlist_dict = {
            item["name"]: item["id"]
            for item in items
            if item.get("name") and item.get("id")
        }

        if not playlist_dict:
            return "No valid playlists found."

        return playlist_dict

    except Exception as e:
        return f"Error getting playlists: {e}"


# Tool

def add_songs_to_playlist(playlist_id: str, items: str, position=None):
    """
    Adds a list of song URIs to the specified playlist.

    Args:
        playlist_id (str): The ID of the playlist.
        items (str): Comma-separated Spotify track URIs or string representation of list
        position (str, optional): Position to insert songs

    Returns:
        str: Success or error message
    """
    try:

        if isinstance(items, str):

            if items.startswith('[') and items.endswith(']'):

                items = items.strip('[]').replace("'", "").replace('"', '')
                song_uris = [uri.strip() for uri in items.split(',')]
            else:

                song_uris = [uri.strip() for uri in items.split(',')]
        else:
            song_uris = items


        if position == "0":
            add_to_playlist = sp.playlist_add_items(playlist_id, song_uris, position=0)
        elif position == "":
            add_to_playlist = sp.playlist_add_items(playlist_id, song_uris)
        else:
            return "Error: Position must be '0' (for beginning) or left blank (for end)."

        if add_to_playlist is not None:
            return "success adding songs to playlist"

    except Exception as e:
        return f"error adding song to playlist {e}"


#Tool

def get_users_top_artists(limit: int, time_range: str = "medium_term"):
    """
    Use this tool to get the top artists of the user

    Args:
        limit (int): Number of artists to retrieve
        time_range (str): One of "short_term", "medium_term", "long_term". Default is "medium_term".

    Returns:
        dict: defaultdict containing genres and artist names
    """
    if not sp:
        return "Please authenticate with Spotify first."

    if not limit:
        return "Please enter number of artists to retrieve."

    # Handle blank input => default to medium_term
    if not time_range or not time_range.strip():
        time_range = "medium_term"

    # Only allow known ranges
    valid_ranges = {"short_term", "medium_term", "long_term"}
    if time_range not in valid_ranges:
        return f"Invalid time_range. Must be one of: {', '.join(valid_ranges)}"

    artist_and_genre = defaultdict(list)

    try:
        response = sp.current_user_top_artists(
            limit=limit,
            time_range=time_range
        )

        if response.get("items"):
            for item in response["items"]:
                genres = item.get("genres")
                artist_name = item.get("name")

                artist_and_genre["artist_name"].append(artist_name)
                artist_and_genre["genres"].append(genres)
        else:
            return "No top artists found."

        return artist_and_genre

    except Exception as e:
        return f"Error getting top artists: {e}"
    

#Tool

def get_user_top_tracks(limit_songs=5, time_range="medium_term", offset=0):
    """
    Use this tool to get the user's top tracks.

    Args:
        limit_songs (int): Number of top tracks to retrieve.
        time_range (str): One of "short_term", "medium_term", "long_term". Defaults to "medium_term".
        offset (int): Pagination offset.

    Returns:
        dict: Track names mapped to artist names.
    """
    if not sp:
        return "Please authenticate with Spotify first."

    if not limit_songs:
        return "Please provide the number of tracks to retrieve."

    # Default or blank fallback
    if not time_range or not time_range.strip():
        time_range = "medium_term"

    valid_ranges = {"short_term", "medium_term", "long_term"}
    if time_range not in valid_ranges:
        return f"Invalid time_range. Must be one of: {', '.join(valid_ranges)}"

    track_artist_map = {}

    try:
        result = sp.current_user_top_tracks(limit=limit_songs, offset=offset, time_range=time_range)

        if result.get("items"):
            for item in result["items"]:
                track_name = item.get("name")
                artists = item.get("album", {}).get("artists", [])
                artist_names = ", ".join([a.get("name") for a in artists]) if artists else "Unknown Artist"
                track_artist_map[track_name] = artist_names
        else:
            return "Error retrieving top tracks. Please try again."

        return track_artist_map

    except Exception as e:
        return f"Error retrieving top tracks: {e}"

gr.Markdown("hello")


gr_mcp_tool1 = gr.Interface(fn=add_to_queue_song,inputs="text",outputs="text")

gr_mcp_tool2 = gr.Interface(
    fn=get_artist_and_track,
    inputs="text",
    outputs=gr.Textbox(label="Track : Artist", lines=15)
)

gr_mcp_tool3 = gr.Interface(fn=auth_with_spotify,inputs=None,outputs=gr.Textbox(label="Authentication Status"))

gr_mcp_tool4 = gr.Interface(
    fn=get_recently_played_songs,
    inputs=[
        gr.Number(label="Number of Recently Played Songs", value=5)
    ],
    outputs=gr.JSON(label="Song : Artist")
)

gr_mcp_tool5 = gr.Interface(
    fn=create_playlist,
    inputs=[
        gr.Textbox(label="User ID", placeholder="Enter Spotify user ID"),
        gr.Textbox(label="Playlist Name", placeholder="Enter playlist name")
    ],
    outputs="text")

gr_mcp_tool6 = gr.Interface(fn=get_playlist_name_and_id,inputs=gr.Number(label="number of playlists"),outputs=gr.JSON(label="playlist name and id"))


gr_mcp_tool7 = gr.Interface(
    fn=add_songs_to_playlist,
    inputs=[
        gr.Textbox(
            label="Playlist ID",
            placeholder="e.g. 6PgF6BC39K31SCyMIhlNVs",
            info="The Spotify playlist ID where you want to add songs"
        ),
        gr.Textbox(
            label="Song URIs (comma separated)",
            placeholder="e.g. ['spotify:track:abc123', 'spotify:track:def456', 'spotify:track:ghi789']",
            info="Enter Spotify track URIs separated by commas e.g. ['spotify:track:abc123', 'spotify:track:def456', 'spotify:track:ghi789']",
            lines=3
        ),
        gr.Textbox(
            label="Position (optional)",
            placeholder="e.g. 0 for beginning, leave empty for end",
            info="Position to insert songs (0 = beginning, empty = end)"
        )
    ],
    outputs=gr.Textbox(label="Result"))

gr_mcp_tool8 = gr.Interface(
    fn=get_users_top_artists,
    inputs=[
        gr.Number(label="Number of Artists to Retrieve"),
        gr.Dropdown(
            choices=["short_term", "medium_term", "long_term"],
            value="medium_term",  # Default value
            label="Time Range",
            info="Choose the time range for top artists"
        )
    ],
    outputs=gr.JSON(label="Genres and Artist Names")
)

gr_mcp_tool9 = gr.Interface(
    fn=get_user_top_tracks,
    inputs=[
        gr.Number(label="Number of Tracks to Retrieve", value=5),
        gr.Dropdown(
            choices=["short_term", "medium_term", "long_term"],
            label="Time Range",
            value="medium_term",
            info="Choose time range for top tracks"
        )
    ],
    outputs=gr.JSON(label="Top Tracks and Artist Names")
)

with gr.Blocks() as app:
    gr.Markdown("# 🎵 Spotify MCP Tools")
    gr.Markdown("Welcome to the Spotify Music Control Panel. Below are the tools available in the Spotify MCP server.")
    gr.Markdown("IMPORTANT !! - Due to Limitations in the Authentication of the Spotify account Please Run it locally with your Spotify Developer Credentials , checkout the Readme file to know more about the setup.")


    gr.TabbedInterface(
        [gr_mcp_tool3, gr_mcp_tool1, gr_mcp_tool2 , gr_mcp_tool4,
         gr_mcp_tool5, gr_mcp_tool6, gr_mcp_tool7, gr_mcp_tool8, gr_mcp_tool9],
        tab_names=[
            "Authenticate","Add to Queue", "Get Artist & Track", "Recently Played",
            "Create Playlist", "Playlist Info", "Add Songs to Playlist", "Top Artists", "Top Tracks"
        ]
    )


app.launch(mcp_server=True)
