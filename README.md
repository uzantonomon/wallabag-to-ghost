Tested only on Python 3.

* Get the necessary secrets:
  * **Wallabag** (replace _<YOUR_WALLABAG_URL>_ with your URL):
    * Follow the instructions here: https://<YOUR_WALLABAG_URL>/developer/howto/first-app
  * **Ghost**:
    * Follow the instructions here: https://ghost.org/docs/admin-api/#token-authentication
    * The ID of the page you want to update (check the URL when opening the page on the Ghost editor): https://<YOUR_GHOST_URL>m/ghost/#/editor/page/your-page-id

* Create a ```secrets.py``` with the following:

```
WALLABAG_CLIENT_ID = "your-wallabag-client-id"
WALLABAG_CLIENT_SECRET = "your-wallabag-client-secret"
WALLABAG_USERNAME = "your-wallabag-username"
WALLABAG_PASSWORD = "your-wallabag-password"
WALLABAG_AUTH_URL = "https://wallabag.example.com/oauth/v2/token"
WALLABAG_ENTRIES_URL = "https://wallabag.example.com/api/entries.json?perPage=999"
WALLABAG_HTML_FILE = "links.html"
GHOST_AUTH = "your-ghost-admin-api-key-id"
GHOST_PAGE_TO_UPDATE = "https://ghost.example.com/ghost/api/v3/admin/pages/your-page-id"
```

* Install necessary packages (use _venv_):
```$ pip3 install -r requirements.txt```

* Run ```wallabag-to-ghost.py``` with **cron**, for example, to keep your page updated.

```
$ crontab -e
$ 0 * * * * /path/to/env/bin/python /home/example/wallabag-to-ghost.py
```

You can find the final page <a href="https://diogoferreira.pt/bookmarks/" target="_blank">here</a>.
