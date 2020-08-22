#!/usr/bin/env python3

import requests
import json
import secrets
import jwt
from datetime import datetime as date

# Get links from Wallabag and store them in a file.


def get_wallabag_token(auth_url, client_id, client_secret, username, password):
    token_request = requests.post(
        auth_url,
        data={
            "grant_type": "password",
            "client_id": client_id,
            "client_secret": client_secret,
            "username": username,
            "password": password,
        },
    )
    token_json = token_request.json()
    wallabag_token = token_json["access_token"]
    return wallabag_token


def get_wallabag_entries(entries_url, wallabag_token):
    headers = {"Authorization": "Bearer " + wallabag_token}
    response = requests.get(entries_url, headers=headers)
    response_to_json = response.json()
    return response_to_json


def generate_html_file(html_file, links):
    link_list = []

    for x in links["_embedded"]["items"]:
        link_list.append(x["url"])

    with open(html_file, "w+") as html_file:
        html_file.write(
            '<p>These are the links that I currently have on my <a href="https://wallabag.org" target="_blank">Wallabag</a> instance.</p>'
            "This page is kept up to date with a simple Python script and a cron job.</p>"
            '<p>You can find the script on my <a href="https://github.com/uzantonomon/wallabag-to-ghost" target="_blank">GitHub</a>.</p>'
        )
        for link in link_list:
            html_file.write(
                '• <a href="'
                + link
                + '" target="_blank"'
                + '>'
                + ((link[:66] + "... ") if len(link) > 66 else link)
                + "</a>"
            )
            html_file.write("\n")
        html_file.close()


# Update a Ghost page with the links on a file.


def make_ghost_token(key_id):
    ghost_auth = key_id
    id, secret = ghost_auth.split(":")

    iat = int(date.now().timestamp())

    header = {"alg": "HS256", "typ": "JWT", "kid": id}
    payload = {"iat": iat, "exp": iat + 5 * 60, "aud": "/v3/admin/"}
    ghost_token = jwt.encode(
        payload, bytes.fromhex(secret), algorithm="HS256", headers=header
    )
    return ghost_token


def get_updated_at(page, complete_token):
    get_url = page
    headers = {"Authorization": "Ghost {}".format(complete_token.decode())}
    response = requests.get(get_url, headers=headers)
    response_json = response.json()
    current_date = response_json["pages"][0]["updated_at"]
    return current_date


def update_page(html_file, page, date):
    with open(html_file) as f:
        data = f.read().replace("\n", "<br />")
        url = page + "?source=html"
        headers = {"Authorization": "Ghost {}".format(complete_token.decode())}
        body = {
            "pages": [
                {"title": "Bookmarks", "html": data, "updated_at": date}
            ]
        }
    requests.put(url, json=body, headers=headers)


complete_token = get_wallabag_token(
    secrets.WALLABAG_AUTH_URL,
    secrets.WALLABAG_CLIENT_ID,
    secrets.WALLABAG_CLIENT_SECRET,
    secrets.WALLABAG_USERNAME,
    secrets.WALLABAG_PASSWORD,
)

entries = get_wallabag_entries(secrets.WALLABAG_ENTRIES_URL, complete_token)

generate_html_file(secrets.WALLABAG_HTML_FILE, entries)

complete_token = make_ghost_token(secrets.GHOST_AUTH)

complete_date = get_updated_at(secrets.GHOST_PAGE_TO_UPDATE, complete_token)

update_page(secrets.WALLABAG_HTML_FILE, secrets.GHOST_PAGE_TO_UPDATE, complete_date)
