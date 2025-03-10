A Python script to automatically sync your [Wallabag](https://wallabag.org) archive with a [Ghost](https://ghost.org) blog page.

## Overview

This script retrieves all archived entries from your Wallabag instance and publishes them as a list of links on a Ghost blog page. The process is designed to be automated via a cron job, keeping your bookmarks page always up to date.

## Features

- Fetches all archived entries from Wallabag
- Generates HTML with bookmark links
- Updates a specified Ghost page with the bookmark list
- Handles pagination for large bookmark collections
- Trims long URLs for better display

## Requirements

- Python 3.x
- Required packages:
  - `requests`
  - `pyjwt`
  - `configparser`

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/uzantonomon/wallabag-to-ghost.git
   cd wallabag-to-ghost
   ```

2. Install dependencies:
   ```
   pip install requests pyjwt configparser
   ```

3. Create a `config.ini` file (see Configuration section below or copy the provided `.example` one)

## Setting up Wallabag API

1. Log in to your Wallabag instance
2. Go to the developer section (usually at `https://your-wallabag-instance/developer`)
3. Create a new client application:
   - Enter a name for your application (e.g., "Wallabag to Ghost")
   - Leave the redirect URI as the default
   - Click "Create a new client"
4. Note down the generated Client ID and Client Secret for your `config.ini` file

## Setting up Ghost API

1. Log in to your Ghost Admin panel
2. Go to "Settings" → "Integrations"
3. Scroll down to "Custom Integrations" and click "Add custom integration"
4. Name your integration (e.g., "Wallabag Sync")
5. You'll need two keys from this page:
   - Content API Key - For reading your current page content
   - Admin API Key - For updating the page content
6. You'll also need the page ID you want to update:
   - Navigate to the page in the Ghost editor
   - The page ID is in the URL: `https://your-ghost-blog/ghost/#/editor/page/[page-id]`

## Configuration

Create a `config.ini` file with the following structure:

```ini
[WALLABAG]
CLIENT_ID = your_wallabag_client_id
CLIENT_SECRET = your_wallabag_client_secret
USERNAME = your_wallabag_username
PASSWORD = your_wallabag_password
AUTH_URL = https://your-wallabag-instance/oauth/v2/token
ENTRIES_URL = https://your-wallabag-instance/api/entries
HTML_FILE = bookmarks.html

[GHOST]
PAGE_TO_UPDATE = https://your-ghost-blog/ghost/api/v3/admin/pages/your-page-id
BOOKMARKS_PAGE = https://your-ghost-blog/ghost/api/v3/content/pages/your-page-id
CONTENT_KEY = your_ghost_content_api_key
ADMIN_KEY = your_ghost_admin_api_key
```

## Usage

Run the script manually:

```
python3 wallabag_to_ghost.py
```

Or set up a cron job to run it automatically:

```
0 * * * * /path/to/python3 /path/to/wallabag_to_ghost.py
```

This example runs the script hourly.

## How It Works

1. Authenticates with Wallabag using OAuth2
2. Retrieves all archived entries with pagination support
3. Generates HTML with formatted links
4. Authenticates with Ghost Admin API
5. Updates the specified Ghost page with the formatted bookmarks
