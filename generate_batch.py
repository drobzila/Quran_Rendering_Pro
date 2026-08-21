from __future__ import annotations

import json
import os
from pathlib import Path

import Quran
from metadata import build_metadata, save_metadata

COUNT = int(os.environ.get("BATCH_COUNT", "10"))
OUTPUT = Path(os.environ.get("OUTPUT_DIR", "batch_output"))
STYLES = ["minimal", "cinematic", "mushaf", "night", "golden"]
TITLE_FILE = Path(Quran.TITLE_FILE)


def read_rendered_reference() -> tuple[str, int]:
    if not TITLE_FILE.exists():
        raise RuntimeError("title.txt was not produced by the renderer")
    title = TITLE_FILE.read_text(encoding="utf-8").strip()
    if " | آية " not in title:
        raise RuntimeError(f"Unexpected title format: {title}")
    surah_name, number = title.rsplit(" | آية ", 1)
    return surah_name, int(number)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    ok = failed = 0

    for index in range(1, COUNT + 1):
        style = STYLES[(index - 1) % len(STYLES)]
        os.environ["VIDEO_STYLE"] = style
        path = OUTPUT / f"quran_{index:03d}_{style}.mp4"
        metadata_path = path.with_suffix(".json")

        try:
            Quran.render_one(str(path))
            surah_name, ayah_number = read_rendered_reference()
            metadata = build_metadata(surah_name, ayah_number, style)
            save_metadata(metadata, metadata_path)
            ok += 1
            print(f"✅ [{index}/{COUNT}] {style}: {path}")
        except Exception as exc:
            failed += 1
            print(f"❌ [{index}/{COUNT}] {style}: {exc}")

    print(f"\nFinished: {ok} succeeded / {failed} failed")


if __name__ == "__main__":
    main()
