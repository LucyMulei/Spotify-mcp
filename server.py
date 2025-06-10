import gradio as gr
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from collections import defaultdict
import os


CLIENT_ID  = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI =  os.getenv("REDIRECT_URI")


SCOPE = "playlist-read-private playlist-read-collaborative user-top-read user-read-currently-playing user-read-recently-played user-modify-playback-state playlist-modify-public playlist-modify-private"

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
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPE,client_id=CLIENT_ID,client_secret=CLIENT_SECRET,redirect_uri=REDIRECT_URI))

        current_user = sp.current_user()

        if current_user.get("id") != None:
            id = current_user.get("id")

        return current_user

    except Exception as e:
        return f"error auth with spotify {e}"




# Tool
def get_artist_and_track(track_name):

    """
    Searches for a track and returns artist info and URIs
    """

    if not sp:
        return "Please authenticate with Spotify first!"

    if not track_name.strip():
        return "Please enter a track name!"

    artist_song = defaultdict(list)

    response = sp.search(q="track:"+track_name,type="track")

    if response:
        items = response.get("tracks", {}).get("items", [])
        if items:
            for item in items:
                if item and item.get("artists")[0]:
                        artist_song["uri"].append(item["uri"])
                        artist_song["name"].append(item["artists"][0].get("name"))
                else:
                        artist_song["uri"].append(None)
                        artist_song["name"].append(None)

    return artist_song


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

    if not sp:
        return "Please authenticate with Spotify first!"

    if not limit_song:
        return "Please enter a number of songs"

    artist_song = defaultdict(list)

    res = sp.current_user_recently_played(limit_song)

    items = res.get("items",[])

    if items:
        for item in items:
            if item and item.get("track"):
                track = item.get("track",{})

                if (track and track.get("name",{})) or (track and track.get("artists",[])):

                    artist_song["artist_name"].append(track.get("artists")[0].get("name"))
                    artist_song["song_name"].append(track.get("name"))

                else:
                    artist_song["artist_name"].append(None)
                    artist_song["song_name"].append(None)


    return artist_song

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
        Use this tool to get playlist name and id , mostly useful in tasks that needs id of playlist

        it takes args like limit_playlist which is number of paylist you want to retrieve

    """
    playlist_name_and_id = defaultdict(list)

    try:
        result = sp.current_user_playlists(limit_playlist)

        if result.get("items") != None:

            for item in result["items"]:

                if (item and item.get("name")) or (item and item.get("id")):

                    playlist_name_and_id["name"].append(item.get("name"))
                    playlist_name_and_id["id"].append(item.get("id"))

                else:
                    playlist_name_and_id["name"].append(None)
                    playlist_name_and_id["id"].append(None)


        return playlist_name_and_id

    except Exception as e:
        return f"error getting playlists name and id error {e}"



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

        pos = int(position) if position and position.strip() else None

        add_to_playlist = sp.playlist_add_items(playlist_id, song_uris, pos)

        if add_to_playlist is not None:
            return "success adding songs to playlist"

    except Exception as e:
        return f"error adding song to playlist {e}"



#Tool
def get_users_top_artists(limit_artists=5,offset=0,time_range="medium_term"):

    """
        Use this tool to get the top artist of the user

        Args:
            limit_artists (int): number of artists to retrieve
            time_range (str): it can be "medium_term", "short_term" , "long_term" default is "medium_term"

        Returns:
            dict: defaultdict containing genres and artist_name

    """
    if not sp:
        return "Please authenticate with Spotify first!"

    if not limit_artists:
        return "Please enter number of artists to retireve "

    artist_and_genre = defaultdict(list)

    try:
        response = sp.current_user_top_artists(limit_artists, offset, time_range)

        if response.get("items"):
            for item in response["items"]:
                genres = item.get("genres")
                artist_name = item.get("name")

                artist_and_genre["artist_name"].append(artist_name)
                artist_and_genre["genres"].append(genres)
        else:
            return "failed to extract top artists please retry the tool"

        return artist_and_genre

    except Exception as e:
        return f"error getting top artists error {e}"




#Tool
def get_user_top_tracks(limit_songs=5,time_range="medium_term",offset=0):

    topTracks_and_their_artists = defaultdict(list)

    try:

        result = sp.current_user_top_tracks(limit_songs,offset,time_range)

        if result.get("items"):
            for item in result["items"]:
                topTracks_and_their_artists["track_name"].append(item.get("name"))

                album_artists = item.get("album", {}).get("artists", [])

                if album_artists:
                    for artist in album_artists:

                        topTracks_and_their_artists["artist_name"].append(artist.get("name"))

                else:
                    topTracks_and_their_artists["artist_name"].append(None)
        else:
            return "error retrieving top tracks retry the tool again"

        return topTracks_and_their_artists

    except Exception as e:
        return f"error retieving top tracks error -{e}"



gr.Markdown("hello")


gr_mcp_tool1 = gr.Interface(fn=add_to_queue_song,inputs="text",outputs="text")
gr_mcp_tool2 = gr.Interface(fn=get_artist_and_track,inputs="text",outputs="text")
gr_mcp_tool3 = gr.Interface(fn=auth_with_spotify,inputs=None,outputs=gr.Textbox(label="Authentication Status"))
gr_mcp_tool4 = gr.Interface(fn=get_recently_played_songs,inputs=gr.Number(label="Number of Songs"),outputs=gr.JSON(label="Recently Played Songs"))
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

gr_mcp_tool8 = gr.Interface(fn=get_users_top_artists,inputs=[gr.Number(label="number of artists to retrieve ")
                                                             ,gr.Textbox(label="time_range",info="time range has options of 'medium_term', 'short_term' , 'long_term' default is 'medium_term'")]
                                                             ,outputs=gr.JSON(label="genre and artist name"))

gr_mcp_tool9 = gr.Interface(fn=get_user_top_tracks,inputs=[gr.Number(label="number of tracks to retrieve ")
                                                             ,gr.Textbox(label="time_range",info="time range has options of 'medium_term', 'short_term' , 'long_term' default is 'medium_term'")]
                                                             ,outputs=gr.JSON(label="topTrack and artist name"))

with gr.Blocks() as app:
    gr.Markdown("# 🎵 Spotify MCP Tools")
    gr.Markdown("Welcome to the Spotify Music Control Panel, Below are the tools available in the Spotify MCP server.")
    gr.Markdown("Due to Limitations in the Authication of the Spotify account Please Run it locally with your Spotify Developer Credentials ,checkout the Readme file to know more about the setup")


    gr.TabbedInterface(
        [gr_mcp_tool1, gr_mcp_tool2, gr_mcp_tool3, gr_mcp_tool4,
         gr_mcp_tool5, gr_mcp_tool6, gr_mcp_tool7, gr_mcp_tool8, gr_mcp_tool9],
        tab_names=[
            "Add to Queue", "Get Artist & Track", "Authenticate", "Recently Played",
            "Create Playlist", "Playlist Info", "Add Songs to Playlist", "Top Artists", "Top Tracks"
        ]
    )


app.launch(mcp_server=True)
