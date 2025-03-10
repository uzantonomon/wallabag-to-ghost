#!/usr/bin/env python3
"""Get Wallabag archived entries and update a Ghost page with them"""

import configparser
from datetime import datetime as date
import requests
import jwt

config = configparser.ConfigParser()
config.read("config.ini")

WALLABAG_CLIENT_ID = config["WALLABAG"]["CLIENT_ID"]
WALLABAG_CLIENT_SECRET = config["WALLABAG"]["CLIENT_SECRET"]
WALLABAG_USERNAME = config["WALLABAG"]["USERNAME"]
WALLABAG_PASSWORD = config["WALLABAG"]["PASSWORD"]
WALLABAG_AUTH_URL = config["WALLABAG"]["AUTH_URL"]
WALLABAG_ENTRIES_URL = config["WALLABAG"]["ENTRIES_URL"]
WALLABAG_HTML_FILE = config["WALLABAG"]["HTML_FILE"]

GHOST_PAGE_TO_UPDATE = config["GHOST"]["PAGE_TO_UPDATE"]
GHOST_BOOKMARKS = config["GHOST"]["BOOKMARKS_PAGE"]
GHOST_CONTENT_KEY = config["GHOST"]["CONTENT_KEY"]
GHOST_ADMIN_KEY = config["GHOST"]["ADMIN_KEY"]


def get_wallabag_token(auth_url, client_id, client_secret, username, password):
    """Get the Wallabag authentication token"""
    token_request = requests.post(
        auth_url,
        data={
            "grant_type": "password",
            "client_id": client_id,
            "client_secret": client_secret,
            "username": username,
            "password": password,
        },
        timeout=10,
    )

    token_json = token_request.json()
    wallabag_token = token_json["access_token"]
    return wallabag_token


def get_wallabag_entries(entries_url, wallabag_token):
    """Get all the archived Wallabag entries"""
    headers = {"Authorization": f"Bearer {wallabag_token}"}
    urls = []
    page = 1

    while True:
        response = requests.get(
            f"{entries_url}?page={page}&perPage=100", headers=headers, timeout=10
        )

        data = response.json()

        if "_embedded" not in data or "items" not in data["_embedded"]:
            break

        urls.extend(entry["url"] for entry in data["_embedded"]["items"])

        if "pages" in data and page >= data["pages"]:
            break

        page += 1

    return urls


def generate_html_file(html_file, links):
    """Build the final page file"""
    with open(html_file, "w+", encoding="utf-8") as html_file:
        html_file.write(
            '<p>These are the links that I currently have on my <a href="https://wallabag.org" target="_blank">Wallabag</a> instance.</p>'  # pylint: disable=line-too-long
            "This page is kept up to date with a simple Python script and a cron job.</p>"
            '<p>You can find the script on my <a href="https://github.com/uzantonomon/wallabag-to-ghost" target="_blank">GitHub</a>.</p>'
        )
        for link in links:
            html_file.write(
                '• <a href="'
                + link
                + '" target="_blank"'
                + ">"
                + ((link[:66] + "... ") if len(link) > 66 else link)
                + "</a>"
            )
            html_file.write("\n")
        html_file.close()


def make_ghost_token(key_id):
    """Generate the Ghost authentication token"""
    ghost_auth = key_id
    ghost_id, secret = ghost_auth.split(":")

    iat = int(date.now().timestamp())

    header = {"alg": "HS256", "typ": "JWT", "kid": ghost_id}
    payload = {"iat": iat, "exp": iat + 5 * 60, "aud": "/v3/admin/"}
    ghost_token = jwt.encode(
        payload, bytes.fromhex(secret), algorithm="HS256", headers=header
    )
    return ghost_token


def get_updated_at(page, ghost_key):
    """Get the date where the page was last updated"""
    response = requests.get(page + "?key=" + ghost_key, timeout=10)
    response_json = response.json()
    current_date = response_json["pages"][0]["updated_at"]
    return current_date


def update_page(html_file, page, final_date, ghost_token):
    """Publish the updated version of the page"""
    with open(html_file, encoding="utf-8") as f:
        data = f.read().replace("\n", "<br />")
        url = page
        headers = {"Authorization": f"Ghost {ghost_token}"}
        body = {
            "pages": [{"title": "Bookmarks", "html": data, "updated_at": final_date}]
        }
    requests.put(url, json=body, headers=headers, timeout=10)


complete_token = get_wallabag_token(
    WALLABAG_AUTH_URL,
    WALLABAG_CLIENT_ID,
    WALLABAG_CLIENT_SECRET,
    WALLABAG_USERNAME,
    WALLABAG_PASSWORD,
)

entries = get_wallabag_entries(WALLABAG_ENTRIES_URL, complete_token)

generate_html_file(WALLABAG_HTML_FILE, entries)

GHOST_TOKEN = make_ghost_token(GHOST_ADMIN_KEY)

complete_date = get_updated_at(GHOST_BOOKMARKS, GHOST_CONTENT_KEY)

update_page(WALLABAG_HTML_FILE, GHOST_PAGE_TO_UPDATE, complete_date, GHOST_TOKEN)
