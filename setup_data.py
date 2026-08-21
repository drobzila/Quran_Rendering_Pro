from pathlib import Path
import requests

URL = "https://raw.githubusercontent.com/drobzila/Quran_rendering/main/quran.json"
DEST = Path(__file__).resolve().parent / "quran.json"

if DEST.exists():
    print("quran.json موجود بالفعل")
else:
    print("جاري تنزيل بيانات القرآن...")
    r = requests.get(URL, timeout=60)
    r.raise_for_status()
    DEST.write_bytes(r.content)
    print(f"تم حفظ {DEST}")
