from __future__ import annotations

import os
from pathlib import Path
import random
import Quran

COUNT = int(os.environ.get("BATCH_COUNT", "10"))
OUTPUT = Path(os.environ.get("OUTPUT_DIR", "batch_output"))

# Rotate through genuinely different compositions rather than rendering one template repeatedly.
STYLES = ["minimal", "cinematic", "mushaf", "night", "golden"]


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    ok = 0
    failed = 0
    for index in range(1, COUNT + 1):
        style = STYLES[(index - 1) % len(STYLES)]
        os.environ["VIDEO_STYLE"] = style
        path = OUTPUT / f"quran_{index:03d}_{style}.mp4"
        try:
            Quran.render_one(str(path))
            ok += 1
            print(f"✅ [{index}/{COUNT}] {style}: {path}")
        except Exception as exc:
            failed += 1
            print(f"❌ [{index}/{COUNT}] {style}: {exc}")
    print(f"\nFinished: {ok} succeeded / {failed} failed")


if __name__ == "__main__":
    main()
