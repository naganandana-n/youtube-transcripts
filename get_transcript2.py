import subprocess
import os
import sys
import json
import glob

def download_vtt(url):
    print("Trying to download manual subtitles...")
    result = subprocess.run([
        "yt-dlp",
        "--write-sub",
        "--sub-lang", "en",
        "--skip-download",
        "--convert-subs", "vtt",
        url
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # If manual subs weren't found, try auto subs
    vtt_files = sorted(glob.glob("*.en.vtt"), key=os.path.getmtime, reverse=True)
    if not vtt_files:
        print("No manual subs found. Trying auto-generated subtitles...")
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
        print("❌ No .en.vtt subtitle file found.")
        sys.exit(1)

    return vtt_files[0]

def parse_vtt(vtt_file):
    transcript = []
    with open(vtt_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    entry = {}
    for line in lines:
        line = line.strip()
        if "-->" in line:
            start, end = line.split(" --> ")
            entry = {"start": start, "end": end, "text": ""}
        elif line and not line.startswith(("WEBVTT", "NOTE")):
            if "text" in entry:
                entry["text"] += line + " "
        elif line == "" and entry:
            entry["text"] = entry["text"].strip()
            transcript.append(entry)
            entry = {}

    return transcript

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_transcript2.py <YouTube URL>")
        sys.exit(1)

    url = sys.argv[1]

    vtt_file = download_vtt(url)
    transcript = parse_vtt(vtt_file)

    json_filename = vtt_file.replace(".en.vtt", ".json")
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(transcript, f, indent=2, ensure_ascii=False)

    os.remove(vtt_file)

    print(f"✅ Transcript saved as: {json_filename}")
    print(f"🗑️  Deleted temporary file: {vtt_file}")