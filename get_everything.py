import subprocess
import os
import json
import sys
import glob
from datetime import datetime

def get_all_video_urls(channel_id):
    print(f"📺 Getting video URLs from channel {channel_id}...")
    result = subprocess.run([
        "yt-dlp",
        f"https://www.youtube.com/channel/{channel_id}/videos",
        "--flat-playlist",
        "--dump-json"
    ], capture_output=True, text=True)

    videos = []
    for line in result.stdout.strip().splitlines():
        try:
            video = json.loads(line)
            videos.append(video["url"])
        except:
            continue
    return videos

def get_video_metadata(url):
    print(f"📄 Getting metadata for: {url}")
    result = subprocess.run([
        "yt-dlp",
        "--dump-json",
        url
    ], capture_output=True, text=True)

    data = json.loads(result.stdout)
    return {
        "title": data.get("title"),
        "thumbnail": data.get("thumbnail"),
        "upload_date": data.get("upload_date"),
        "video_url": url
    }

def download_and_parse_transcript(url):
    print(f"📝 Downloading transcript for: {url}")
    subprocess.run([
        "yt-dlp",
        "--write-sub",
        "--sub-lang", "en",
        "--skip-download",
        "--convert-subs", "vtt",
        url
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    vtt_files = sorted(glob.glob("*.en.vtt"), key=os.path.getmtime, reverse=True)
    if not vtt_files:
        subprocess.run([
            "yt-dlp",
            "--write-auto-sub",
            "--sub-lang", "en",
            "--skip-download",
            "--convert-subs", "vtt",
            url
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        vtt_files = sorted(glob.glob("*.en.vtt"), key=os.path.getmtime, reverse=True)

    if not vtt_files:
        return "", ""

    return parse_vtt_to_text(vtt_files[0]), vtt_files[0]

def parse_vtt_to_text(vtt_file):
    seen = set()
    cleaned_lines = []

    with open(vtt_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "-->" in line or line.startswith(("WEBVTT", "NOTE", "Kind:", "Language:")):
                continue
            while "<" in line and ">" in line:
                start, end = line.find("<"), line.find(">")
                if start != -1 and end != -1:
                    line = line[:start] + line[end + 1:]
                else:
                    break
            if line and line not in seen:
                cleaned_lines.append(line)
                seen.add(line)
    return " ".join(cleaned_lines)

def main(channel_id, before_date_str):
    before_date = datetime.strptime(before_date_str, "%Y-%m-%d")
    video_urls = get_all_video_urls(channel_id)

    print(f"🔎 Filtering videos uploaded on or before {before_date_str}")
    collected = []

    for url in video_urls:
        metadata = get_video_metadata(url)
        if not metadata["upload_date"]:
            continue

        upload_date = datetime.strptime(metadata["upload_date"], "%Y%m%d")
        if upload_date <= before_date:
            transcript, vtt_file = download_and_parse_transcript(url)
            metadata["transcript"] = transcript
            collected.append(metadata)

            filename = f"{metadata['title'][:50].replace(' ', '_').replace('/', '_')}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            if vtt_file and os.path.exists(vtt_file):
                os.remove(vtt_file)

    with open(f"{channel_id}_until_{before_date_str}.json", "w", encoding="utf-8") as f:
        json.dump(collected, f, ensure_ascii=False, indent=2)

    print("✅ All filtered videos processed and saved.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python get_channel_videos_before_date.py <channel_id> <before_date YYYY-MM-DD>")
        sys.exit(1)

    channel_id = sys.argv[1]
    before_date_str = sys.argv[2]
    main(channel_id, before_date_str)