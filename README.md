# YouTube Transcript API Setup (Docker + Ngrok)

## Folder Structure (Local Docker + Ngrok)

```
docker/
├── app.py
├── requirements.txt
├── Dockerfile
```

---

## To Build and Run the Docker Container Locally:

```bash
docker build -t youtube-transcript-api .
docker run -p 8080:8080 youtube-transcript-api
```

---

## To Expose it with Ngrok

Make sure you have [ngrok](https://ngrok.com/) installed. Then run:

```bash
ngrok http 8080
```

Ngrok will give you a public HTTPS URL like:

```
https://1234-56-78-90-xyz.ngrok-free.app
```

You can now send your `POST` requests from **n8n** or **curl** to that URL:

```bash
curl -X POST https://1234-56-78-90-xyz.ngrok-free.app/transcript \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://www.youtube.com/watch?v=FuqNluMTIR8"}'
```

---
