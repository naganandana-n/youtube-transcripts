from flask import Flask, request, jsonify
import subprocess
import glob
import os
import json
import time

app = Flask(__name__)

def download_vtt(url):
    # Try manual subs first
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
        # Try auto-generated subs
        subprocess.run([
            "yt-dlp",
            "--write-auto-sub",
            "--sub-lang", "en",
            "--skip-download",
            "--convert-subs", "vtt",
            url
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        vtt_files = sorted(glob.glob("*.en.vtt"), key=os.path.getmtime, reverse=True)

    return vtt_files[0] if vtt_files else None

def parse_vtt_to_text(vtt_file):
    seen = set()
    cleaned_lines = []

    with open(vtt_file, "r", encoding="utf-8") as f:
        content = f.readlines()

    for line in content:
        line = line.strip()
        if not line or "-->" in line or line.startswith(("WEBVTT", "NOTE", "Kind:", "Language:")):
            continue

        # Remove <tags>
        while "<" in line and ">" in line:
            start = line.find("<")
            end = line.find(">", start)
            if start != -1 and end != -1:
                line = line[:start] + line[end+1:]
            else:
                break

        line = line.strip()
        if line and line not in seen:
            cleaned_lines.append(line)
            seen.add(line)

    return " ".join(cleaned_lines)

@app.route("/transcript", methods=["POST"])
def get_transcript():
    data = request.get_json()
    url = data.get("video_url")

    if not url:
        return jsonify({"error": "Missing 'video_url'"}), 400

    try:
        vtt_file = download_vtt(url)
        if not vtt_file:
            return jsonify({"error": "No subtitles found for this video."}), 404

        transcript = parse_vtt_to_text(vtt_file)
        os.remove(vtt_file)

        return jsonify({"transcript": transcript})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=8080)