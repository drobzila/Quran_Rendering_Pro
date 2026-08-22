from __future__ import annotations

import glob
import json
import logging
import os
import random
import subprocess
import textwrap
from dataclasses import dataclass
from pathlib import Path

import requests
from manim import *
from mutagen.mp3 import MP3

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "quran.json"
USED_FILE = ROOT / "used_ayahs.json"
TEMP_AUDIO = ROOT / "temp_ayah.mp3"

config.frame_width = 9
config.frame_height = 16
config.pixel_width = 1080
config.pixel_height = 1920

# Amiri Quran is installed by the GitHub Actions workflow. Keep Amiri as a
# local fallback for machines where the Quran font is not installed.
FONT = os.environ.get("QURAN_FONT", "Amiri Quran")
RECITER = os.environ.get("QURAN_RECITER", "ar.husary")
MAX_DURATION = float(os.environ.get("MAX_DURATION", "25"))
STYLES = ["minimal", "cinematic", "mushaf", "night", "golden"]

MINIMAL_BG = "#070A0F"
MINIMAL_PANEL = "#0D1219"
MINIMAL_GOLD = "#C9A45C"
MINIMAL_TEXT = "#F5F1E8"
MINIMAL_MUTED = "#A9A397"


@dataclass
class Ayah:
    surah: int
    number: int
    text: str
    surah_name: str


def load_quran() -> dict:
    if not DATA_FILE.exists():
        raise FileNotFoundError("quran.json غير موجود. شغّل setup_data.py أولاً.")
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def used_ayahs() -> set[str]:
    if not USED_FILE.exists():
        return set()
    try:
        return set(json.loads(USED_FILE.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        return set()


def save_used(items: set[str]) -> None:
    USED_FILE.write_text(
        json.dumps(sorted(items), ensure_ascii=False, indent=2), encoding="utf-8"
    )


def find_ayah(surah_number: int, ayah_number: int) -> Ayah:
    data = load_quran()
    surah = data["data"]["surahs"][surah_number - 1]
    ayah = surah["ayahs"][ayah_number - 1]
    return Ayah(surah_number, ayah_number, ayah["text"], surah["name"])


def download_audio(surah: int, ayah: int, filename: Path | str) -> Path:
    api = f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/{RECITER}"
    response = requests.get(api, timeout=30)
    response.raise_for_status()
    audio_url = response.json()["data"]["audio"]
    audio = requests.get(audio_url, timeout=30)
    audio.raise_for_status()
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(audio.content)
    return path


def choose_ayah() -> Ayah:
    data = load_quran()
    used = used_ayahs()
    candidates: list[Ayah] = []

    for s_idx, surah in enumerate(data["data"]["surahs"], 1):
        for a_idx, ayah in enumerate(surah["ayahs"], 1):
            if f"{s_idx}:{a_idx}" not in used:
                candidates.append(Ayah(s_idx, a_idx, ayah["text"], surah["name"]))

    if not candidates:
        used.clear()
        save_used(used)
        return choose_ayah()

    random.shuffle(candidates)
    for item in candidates:
        try:
            download_audio(item.surah, item.number, TEMP_AUDIO)
            duration = MP3(TEMP_AUDIO).info.length
            TEMP_AUDIO.unlink(missing_ok=True)
            if duration <= MAX_DURATION:
                return item
        except Exception as exc:
            log.warning("Skipping %s:%s: %s", item.surah, item.number, exc)
            TEMP_AUDIO.unlink(missing_ok=True)

    raise RuntimeError("لم يتم العثور على آية مناسبة ضمن الحد الزمني")


def select_for_render() -> Ayah:
    env_surah = os.environ.get("QURAN_SURAH")
    env_ayah = os.environ.get("QURAN_AYAH")
    if env_surah and env_ayah:
        return find_ayah(int(env_surah), int(env_ayah))
    return choose_ayah()


def mark_used(item: Ayah) -> None:
    used = used_ayahs()
    used.add(f"{item.surah}:{item.number}")
    save_used(used)


def arabic_digits(value: int) -> str:
    return str(value).translate(str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩"))


def wrap_arabic(text: str, width: int = 29) -> list[str]:
    # Preserve Quran glyphs and diacritics; only normalize whitespace.
    clean = " ".join(text.split())
    return textwrap.wrap(clean, width=width, break_long_words=False, break_on_hyphens=False) or [clean]


def minimal_background():
    base = Rectangle(
        width=9,
        height=16,
        fill_color=MINIMAL_BG,
        fill_opacity=1,
        stroke_width=0,
    )

    top_glow = Circle(
        radius=4.8,
        color=MINIMAL_GOLD,
        stroke_width=0,
        fill_opacity=0.025,
    ).move_to([0, 5.7, 0])
    bottom_glow = Circle(
        radius=4.0,
        color="#657080",
        stroke_width=0,
        fill_opacity=0.018,
    ).move_to([0, -5.8, 0])

    ornaments = VGroup()
    for sx, sy in [(-1, 1), (1, 1), (-1, -1), (1, -1)]:
        center = np.array([sx * 3.72, sy * 6.75, 0])
        ring1 = Square(side_length=0.72, color=MINIMAL_GOLD, stroke_width=1.0).rotate(PI / 4).move_to(center)
        ring2 = Square(side_length=0.38, color=MINIMAL_GOLD, stroke_width=0.7).rotate(PI / 4).move_to(center)
        ornaments.add(ring1, ring2)

    return VGroup(base, top_glow, bottom_glow, ornaments)


def background(style: str):
    if style == "minimal":
        return minimal_background()
    if style == "night":
        base = Rectangle(width=9, height=16, fill_color="#030817", fill_opacity=1, stroke_width=0)
        stars = VGroup(*[
            Dot([random.uniform(-4.2, 4.2), random.uniform(-7.5, 7.5), 0], radius=random.uniform(.006, .018), color=WHITE)
            for _ in range(80)
        ])
        return VGroup(base, stars)
    if style == "golden":
        base = Rectangle(width=9, height=16, fill_color="#120d05", fill_opacity=1, stroke_width=0)
        glow = Circle(radius=3.5, color=GOLD, stroke_width=0, fill_opacity=.08).move_to([0, 2.2, 0])
        return VGroup(base, glow)
    if style == "cinematic":
        base = Rectangle(width=9, height=16, fill_color="#07100f", fill_opacity=1, stroke_width=0)
        a = Circle(radius=4.5, color=TEAL, stroke_width=0, fill_opacity=.07).move_to([-2.4, 3.2, 0])
        b = Circle(radius=3.2, color=BLUE, stroke_width=0, fill_opacity=.06).move_to([2.2, -2.5, 0])
        return VGroup(base, a, b)
    if style == "mushaf":
        base = Rectangle(width=9, height=16, fill_color="#f4efe2", fill_opacity=1, stroke_width=0)
        border = Rectangle(width=8.2, height=15.2, color=GOLD_E, stroke_width=3, fill_opacity=0)
        return VGroup(base, border)
    return Rectangle(width=9, height=16, fill_color=MINIMAL_BG, fill_opacity=1, stroke_width=0)


def make_text(item: Ayah, style: str):
    color = "#17130b" if style == "mushaf" else (MINIMAL_TEXT if style == "minimal" else WHITE)
    # Amiri Quran has a more delicate Quranic rhythm; use a slightly smaller
    # size and wider line spacing to keep tashkeel clear at 1080x1920.
    size = {"minimal": 56, "cinematic": 58, "mushaf": 54, "night": 59, "golden": 59}[style]
    width = 29 if style == "minimal" else (32 if style == "mushaf" else 30)
    lines = wrap_arabic(item.text, width)
    text_group = VGroup(
        *[Text(line, font=FONT, font_size=size, color=color) for line in lines]
    ).arrange(DOWN, buff=.42)
    text_group.set_max_width(7.45)
    return text_group


class QuranScene(Scene):
    def construct(self):
        item = select_for_render()
        style = os.environ.get("VIDEO_STYLE") or random.choice(STYLES)
        self.camera.background_color = MINIMAL_BG
        self.add(background(style))

        if style == "minimal":
            header = Text(item.surah_name, font=FONT, font_size=31, color=MINIMAL_GOLD)
            ref = Text(
                f"الآية {arabic_digits(item.number)}",
                font=FONT,
                font_size=19,
                color=MINIMAL_MUTED,
            )
            divider = Line(LEFT * 0.32, RIGHT * 0.32, color=MINIMAL_GOLD, stroke_width=1.1)
            heading = VGroup(header, divider, ref).arrange(DOWN, buff=.12).to_edge(UP, buff=.78)
        else:
            title_color = "#6d4c12" if style == "mushaf" else GOLD
            header = Text(item.surah_name, font=FONT, font_size=39, color=title_color)
            ref = Text(f"الآية {arabic_digits(item.number)}", font=FONT, font_size=23,
                       color="#5f5a4d" if style == "mushaf" else GRAY_B)
            heading = VGroup(header, ref).arrange(DOWN, buff=.16).to_edge(UP, buff=.75)

        self.play(FadeIn(heading, shift=UP * .08), run_time=.5)

        text = make_text(item, style)
        if style == "minimal":
            panel = RoundedRectangle(
                corner_radius=.22,
                width=min(text.width + 1.0, 8.15),
                height=min(text.height + 1.05, 8.7),
                color="#26303A",
                stroke_width=0.8,
                fill_color=MINIMAL_PANEL,
                fill_opacity=.30,
            ).move_to([0, -.05, 0])
            accent = Line(LEFT * .23, RIGHT * .23, color=MINIMAL_GOLD, stroke_width=1.0).next_to(panel, DOWN, buff=.25)
            self.play(FadeIn(panel, scale=.985), run_time=.4)
            self.play(FadeIn(text, scale=.985), run_time=.95)
            self.play(Create(accent), run_time=.2)
        elif style == "mushaf":
            panel = Rectangle(width=8.1, height=min(text.height + 1.4, 9.0), color=GOLD_E,
                              stroke_width=1.5, fill_color="#fffaf0", fill_opacity=.25).move_to(text)
            self.play(FadeIn(panel), FadeIn(text, scale=.97), run_time=1)
        elif style == "golden":
            panel = RoundedRectangle(corner_radius=.35, width=min(text.width + 1.2, 8.3),
                                     height=min(text.height + 1.2, 9), color=GOLD_E,
                                     stroke_width=1.5, fill_opacity=.08).move_to(text)
            self.play(Create(panel), FadeIn(text, scale=.94), run_time=1)
        else:
            self.play(FadeIn(text, scale=.92), run_time=.9)

        audio = download_audio(item.surah, item.number, ROOT / f"audio_{item.surah}_{item.number}.mp3")
        duration = MP3(audio).info.length
        self.add_sound(str(audio))
        self.wait(max(duration - 1.0, 1.0))

        fade_targets = [text, heading]
        if style == "minimal":
            fade_targets.extend([panel, accent])
        elif style in {"mushaf", "golden"}:
            fade_targets.append(panel)
        self.play(*[FadeOut(obj) for obj in fade_targets], run_time=.65)


def render_one(output_path: str, style: str | None = None) -> tuple[Ayah, str]:
    item = choose_ayah()
    selected_style = style or random.choice(STYLES)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["QURAN_SURAH"] = str(item.surah)
    env["QURAN_AYAH"] = str(item.number)
    env["VIDEO_STYLE"] = selected_style

    subprocess.run(
        ["manim", "-qh", str(Path(__file__).resolve()), "QuranScene"],
        check=True,
        cwd=ROOT,
        env=env,
    )

    videos = glob.glob(str(ROOT / "media/videos/**/*QuranScene.mp4"), recursive=True)
    if not videos:
        raise FileNotFoundError("لم يتم العثور على فيديو Manim الناتج")
    source = max(videos, key=lambda p: Path(p).stat().st_mtime)

    subprocess.run([
        "ffmpeg", "-y", "-i", source,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart",
        str(output),
    ], check=True, cwd=ROOT)

    mark_used(item)
    log.info("Created %s — %s:%s — %s", output, item.surah, item.number, selected_style)
    return item, selected_style


if __name__ == "__main__":
    render_one("output/Quran_Shorts.mp4", style="minimal")
