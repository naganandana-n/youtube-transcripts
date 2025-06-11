from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

def get_video_id(url):
    query = parse_qs(urlparse(url).query)
    return query.get("v", [None])[0]

@app.route("/transcript", methods=["POST"])
def transcript():
    data = request.get_json()
    if not data or "video_url" not in data:
        return jsonify({"error": "Missing 'video_url' in JSON body"}), 400

    video_url = data["video_url"]
    video_id = get_video_id(video_url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([item['text'] for item in transcript])
        return jsonify({"transcript": full_text})
    except NoTranscriptFound:
        return jsonify({"error": "No transcript found for this video"}), 404
    except TranscriptsDisabled:
        return jsonify({"error": "Transcripts are disabled for this video"}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)