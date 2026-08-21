from __future__ import annotations

import json
from pathlib import Path

STYLES = {
    "minimal": "عرض هادئ وبسيط للآية",
    "cinematic": "عرض بصري سينمائي للآية",
    "mushaf": "عرض مستوحى من صفحات المصحف",
    "night": "عرض ليلي هادئ للآية",
    "golden": "عرض ذهبي روحاني للآية",
}


def build_metadata(surah_name: str, ayah_number: int, style: str) -> dict:
    title = f"{surah_name} | آية {ayah_number} 🤍"
    description = (
        f"تلاوة قرآنية من سورة {surah_name}، الآية رقم {ayah_number}.\n\n"
        "نسأل الله أن يجعل القرآن نورًا لقلوبنا وهدىً ورحمة.\n\n"
        "#القرآن #قرآن #تلاوة #Islam #Quran #Shorts"
    )
    return {
        "title": title,
        "description": description,
        "tags": ["القرآن", "قرآن", "تلاوة", "Quran", "Islam", "Shorts", surah_name],
        "category_id": "22",
        "style": style,
        "surah_name": surah_name,
        "ayah_number": ayah_number,
    }


def save_metadata(metadata: dict, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return target
