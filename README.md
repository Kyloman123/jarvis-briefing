# Jarvis Briefing

A personal command-center dashboard for:

- Priority email briefing through Gmail read-only OAuth
- Selected stock watchlist
- Top news/manual briefing items
- Tasks, notes, and command capture

## Run Locally

The local server enables live stock refresh through `/api/stocks`.

```bash
python3 server.py
```

Then open:

```text
http://127.0.0.1:8765/
```

## Host On GitHub Pages

GitHub Pages can host the static app from `index.html`.

1. Push this repository to GitHub.
2. Open the repo on GitHub.
3. Go to **Settings** -> **Pages**.
4. Set **Source** to deploy from the `main` branch and `/root`.
5. Save.

Your hosted site will look like:

```text
https://YOUR_USERNAME.github.io/YOUR_REPO/
```

## Gmail Setup

Create a Google OAuth web client and add your hosted GitHub Pages origin to **Authorized JavaScript origins**.

For local use:

```text
http://127.0.0.1:8765
```

For GitHub Pages:

```text
https://YOUR_USERNAME.github.io
```

Paste the OAuth Client ID into **Sources** in the app, then click **Connect Gmail**.

## Hosted Stock Refresh Note

GitHub Pages is static hosting, so it cannot run `server.py`.

Live stock refresh works locally through the Python server. On GitHub Pages, the app will keep showing saved/fallback stock data unless you connect a hosted API proxy later.
