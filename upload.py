from __future__ import annotations

import json
import os
import pickle
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

ROOT = Path(__file__).resolve().parent


def load_credentials():
    token_file = Path(os.environ.get("YOUTUBE_TOKEN", ROOT / "token.pkl"))
    if not token_file.exists():
        raise FileNotFoundError(
            f"YouTube token not found: {token_file}. Set YOUTUBE_TOKEN or create token.pkl locally."
        )
    with token_file.open("rb") as fh:
        return pickle.load(fh)


def upload_video(video_path: str | Path, metadata_path: str | Path, privacy: str = "private") -> str:
    video = Path(video_path)
    metadata_file = Path(metadata_path)
    if not video.exists():
        raise FileNotFoundError(video)
    if not metadata_file.exists():
        raise FileNotFoundError(metadata_file)

    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    youtube = build("youtube", "v3", credentials=load_credentials())

    body = {
        "snippet": {
            "title": metadata["title"],
            "description": metadata["description"],
            "tags": metadata.get("tags", []),
            "categoryId": metadata.get("category_id", "22"),
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=MediaFileUpload(str(video), mimetype="video/mp4", resumable=True),
    )
    response = request.execute()
    video_id = response["id"]
    print(f"Uploaded: https://www.youtube.com/watch?v={video_id}")
    return video_id


if __name__ == "__main__":
    video = os.environ.get("VIDEO_FILE")
    metadata = os.environ.get("METADATA_FILE")
    privacy = os.environ.get("YOUTUBE_PRIVACY", "private")
    if not video or not metadata:
        raise SystemExit("Set VIDEO_FILE and METADATA_FILE before running upload.py")
    upload_video(video, metadata, privacy)
