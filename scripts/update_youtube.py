import os
import re
import requests

CHANNEL_ID = "UCii6kqnL8_rFaNeXfNj_aPw"
API_KEY = os.environ["YOUTUBE_API_KEY"]
README_PATH = "README.md"
YT_API = "https://www.googleapis.com/youtube/v3"


def fetch_latest_videos(max_results=3):
    resp = requests.get(f"{YT_API}/search", params={
        "key": API_KEY,
        "channelId": CHANNEL_ID,
        "part": "snippet",
        "order": "date",
        "maxResults": max_results,
        "type": "video",
    })
    resp.raise_for_status()
    return resp.json().get("items", [])


def fetch_most_popular_video():
    # Get all uploads playlist
    resp = requests.get(f"{YT_API}/channels", params={
        "key": API_KEY,
        "id": CHANNEL_ID,
        "part": "contentDetails",
    })
    resp.raise_for_status()
    uploads_id = resp.json()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # Get video IDs from uploads
    resp = requests.get(f"{YT_API}/playlistItems", params={
        "key": API_KEY,
        "playlistId": uploads_id,
        "part": "contentDetails",
        "maxResults": 50,
    })
    resp.raise_for_status()
    video_ids = [item["contentDetails"]["videoId"] for item in resp.json().get("items", [])]

    if not video_ids:
        return None

    # Get stats for all videos
    resp = requests.get(f"{YT_API}/videos", params={
        "key": API_KEY,
        "id": ",".join(video_ids),
        "part": "snippet,statistics",
    })
    resp.raise_for_status()
    videos = resp.json().get("items", [])

    return max(videos, key=lambda v: int(v["statistics"].get("viewCount", 0)))


def format_view_count(count):
    n = int(count)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M views"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K views"
    return f"{n} views"


def build_youtube_section(latest, popular):
    lines = []
    lines.append("## YouTube")
    lines.append("")
    lines.append("### Latest Videos")
    lines.append("")
    lines.append('<table><tr>')

    for video in latest:
        vid_id = video["id"]["videoId"]
        title = video["snippet"]["title"]
        thumb = video["snippet"]["thumbnails"]["high"]["url"]
        lines.append(f'<td align="center" width="33%">')
        lines.append(f'<a href="https://www.youtube.com/watch?v={vid_id}">')
        lines.append(f'<img src="{thumb}" alt="{title}" width="100%"/><br/>')
        lines.append(f'<strong>{title}</strong>')
        lines.append(f'</a>')
        lines.append(f'</td>')

    lines.append('</tr></table>')
    lines.append("")

    if popular:
        vid_id = popular["id"]
        title = popular["snippet"]["title"]
        thumb = popular["snippet"]["thumbnails"]["high"]["url"]
        views = format_view_count(popular["statistics"].get("viewCount", 0))
        lines.append("### Most Watched")
        lines.append("")
        lines.append(f'<div align="center">')
        lines.append(f'<a href="https://www.youtube.com/watch?v={vid_id}">')
        lines.append(f'<img src="{thumb}" alt="{title}" width="50%"/><br/>')
        lines.append(f'<strong>{title}</strong><br/>')
        lines.append(f'<sub>{views}</sub>')
        lines.append(f'</a>')
        lines.append(f'</div>')

    return "\n".join(lines)


def main():
    latest = fetch_latest_videos(3)
    popular = fetch_most_popular_video()
    section = build_youtube_section(latest, popular)

    with open(README_PATH, "r") as f:
        readme = f.read()

    updated = re.sub(
        r"<!-- YOUTUBE:START -->.*?<!-- YOUTUBE:END -->",
        f"<!-- YOUTUBE:START -->\n{section}\n<!-- YOUTUBE:END -->",
        readme,
        flags=re.DOTALL,
    )

    with open(README_PATH, "w") as f:
        f.write(updated)

    print("README updated with latest YouTube data.")


if __name__ == "__main__":
    main()
