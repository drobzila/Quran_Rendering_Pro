from __future__ import annotations

import os
from pathlib import Path

import Quran
from metadata import build_metadata, save_metadata

COUNT = int(os.environ.get("BATCH_COUNT", "10"))
OUTPUT = Path(os.environ.get("OUTPUT_DIR", "batch_output"))
STYLES = ["minimal", "cinematic", "mushaf", "night", "golden"]


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    ok = failed = 0

    for index in range(1, COUNT + 1):
        style = STYLES[(index - 1) % len(STYLES)]
        path = OUTPUT / f"quran_{index:03d}_{style}.mp4"
        metadata_path = path.with_suffix(".json")

        try:
            item, actual_style = Quran.render_one(str(path), style=style)
            metadata = build_metadata(item.surah_name, item.number, actual_style)
            save_metadata(metadata, metadata_path)
            ok += 1
            print(f"✅ [{index}/{COUNT}] {actual_style}: {path}")
        except Exception as exc:
            failed += 1
            print(f"❌ [{index}/{COUNT}] {style}: {exc}")

    print(f"\nFinished: {ok} succeeded / {failed} failed")


if __name__ == "__main__":
    main()
