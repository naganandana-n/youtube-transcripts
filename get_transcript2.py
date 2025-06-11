import subprocess
import os
import sys
import glob
import json

def download_vtt(url):
    print("Downloading subtitles...")
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

def parse_vtt_to_text(vtt_file):
    seen = set()
    cleaned_lines = []

    with open(vtt_file, "r", encoding="utf-8") as f:
        content = f.readlines()

    for line in content:
        line = line.strip()
        if not line or "-->" in line or line.startswith(("WEBVTT", "NOTE", "Kind:", "Language:")):
            continue

        # Strip <tags>
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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_transcript2.py <YouTube URL>")
        sys.exit(1)

    url = sys.argv[1]
    vtt_file = download_vtt(url)
    transcript_text = parse_vtt_to_text(vtt_file)

    output_file = vtt_file.replace(".en.vtt", ".json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"transcript": transcript_text}, f, ensure_ascii=False, indent=2)

    os.remove(vtt_file)
    print(f"✅ Clean transcript saved as {output_file}")