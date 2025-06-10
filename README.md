---
title: Spotify MCP Server
emoji: 🎵
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.0.0
app_file: server.py
pinned: false
---

# Spotify MCP Server

A Gradio-based MCP server that provides a user-friendly interface to interact with Spotify's API. This server offers various tools for managing your Spotify experience, from authentication to playlist management and music playback control.

## Demo Video
[Watch the demo video](https://asset.cloudinary.com/dedgdfu0l/0f0cb2dda40de41f419c50b57e9e74c5)

## Features

- **Authentication**: Secure Spotify authentication using OAuth2
- **Music Search**: Search for tracks and get artist information
- **Queue Management**: Add songs to your Spotify queue (requires Spotify Premium)
- **Recently Played**: View your recently played tracks
- **Playlist Management**: 
  - Create new playlists
  - View existing playlists
  - Add songs to playlists
- **User Insights**:
  - View top artists
  - View top tracks
  - Get genre information

## Requirements

- Python 3.x
- Spotify Premium account (required for some queue management features)
- Spotify Developer account for API credentials

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install gradio spotipy
   ```

## Configuration

### Getting Spotify API Keys

1. Create an account on [developer.spotify.com](https://developer.spotify.com)
2. Navigate to the dashboard
3. Create a new app with the following settings:
   - Redirect URI: `http://127.0.0.1:5000/callback` (you can choose any port, but must use http and an explicit loopback address)
   - Note: You may need to restart your MCP environment (e.g., Claude Desktop) once or twice before it works

### Environment Variables

The server uses the following environment variables:
Please create a .env file with the credentials

- `CLIENT_ID`: Your Spotify API client ID
- `CLIENT_SECRET`: Your Spotify API client secret
- `REDIRECT_URI`: Your Spotify API redirect URI (default: http://127.0.0.1:5000/callback)

### Running Locally

This project is designed to run locally and is not yet set up for ephemeral environments (e.g., uvx usage). To run:

1. Clone this repository
2. Set up your environment variables
3. Run the server

## Example Queries for Claude Desktop

Try these example queries in Claude Desktop to explore different features:

### Music Discovery & Analytics
"Show me my top 10 artists and their genres from the last 6 months"

### Smart Playlist Creation
"Create a playlist of my top 20 tracks from this month"

### Queue Management
"Search for 'I Like Me Better' and add it to my queue"

### Playlist Organization
"Show me all my playlists"

### Music Curation
"Compare my top 10 tracks from this month with my all-time favorites"

### Quick Actions
"Show me my 5 most recently played songs"

## API Endpoints

The server exposes several endpoints through Gradio interfaces:

- `add_to_queue_song`: Add a song to the queue (Premium required)
- `get_artist_and_track`: Search for tracks
- `auth_with_spotify`: Authenticate with Spotify
- `get_recently_played_songs`: Get recently played tracks
- `create_playlist`: Create a new playlist
- `get_playlist_name_and_id`: Get playlist information
- `add_songs_to_playlist`: Add songs to a playlist
- `get_users_top_artists`: Get user's top artists
- `get_user_top_tracks`: Get user's top tracks

## Premium Features

The following features require a Spotify Premium account:
- Adding songs to queue

## Claude Desktop Configuration

To use this MCP server with Claude Desktop, add the following configuration to your settings (port number can vary, please check):

```json
{
  "mcpServers": {
    "gradio": {
      "command": "npx",
      "args": ["mcp-remote", "http://127.0.0.1:7860/gradio_api/mcp/sse"]
    }
  }
}
```

This configuration allows Claude Desktop to connect to the Gradio MCP server running on port 7860.

## Tags

mcp-server-track 