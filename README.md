# Quran Rendering Pro 🌙

نسخة مطوّرة من `Quran_rendering` لإنشاء فيديوهات قرآن عمودية 9:16 مع تنوع حقيقي في التصميم بدل تكرار قالب واحد.

## المزايا

- خمسة أنماط بصرية مختلفة: `minimal`, `cinematic`, `mushaf`, `night`, `golden`.
- تدوير الأنماط عند التوليد الدفعي.
- اختيار آيات لم تُستخدم سابقًا قبل بدء دورة جديدة.
- جلب التلاوة آليًا والتحقق من مدة الصوت.
- إخراج 1080×1920 مناسب لـ Shorts.
- إنشاء ملف metadata مستقل لكل فيديو.
- رفع اختياري إلى YouTube عبر API.
- عدم تخزين ملفات البيانات الكبيرة أو الأسرار داخل Git.

## التثبيت

```bash
pip install -r requirements.txt
python setup_data.py
```

تأكد من تثبيت FFmpeg وManim وإتاحة الخط `Amiri` للنظام.

## إنشاء فيديو واحد

```bash
python Quran.py
```

يمكن اختيار النمط:

```bash
VIDEO_STYLE=night python Quran.py
```

## إنشاء دفعة

```bash
BATCH_COUNT=10 python generate_batch.py
```

أو:

```bash
BATCH_COUNT=20 OUTPUT_DIR=batch_output python generate_batch.py
```

ينتج النظام لكل فيديو ملفًا بجانب الفيديو، مثل:

```text
batch_output/
├── quran_001_minimal.mp4
├── quran_001_minimal.json
├── quran_002_cinematic.mp4
├── quran_002_cinematic.json
└── ...
```

## YouTube Upload

`upload.py` لا يحتوي أي أسرار أو رموز دخول. ضع ملف OAuth token محليًا فقط، وسيتم تجاهله بواسطة Git.

لرفع فيديو يدويًا بعد التأكد منه:

```bash
YOUTUBE_TOKEN=token.pkl \
VIDEO_FILE=batch_output/quran_001_minimal.mp4 \
METADATA_FILE=batch_output/quran_001_minimal.json \
YOUTUBE_PRIVACY=private \
python upload.py
```

استخدم `private` للاختبار أولًا، ثم غيّره إلى `public` بعد مراجعة الفيديو والبيانات. لا تضع `client_secret.json` أو `token.pkl` داخل المستودع.

## تنويع المحتوى

التنوع البصري هنا ليس مجرد تغيير لون الخلفية؛ الأنماط تغيّر تركيب المشهد، اللوحة، الخلفية، وطريقة ظهور النص. ومع ذلك، **التنوع وحده لا يضمن تحقيق الدخل**. يجب أن تكون الفيديوهات ذات قيمة واضحة، وألا تكون إنتاجًا جماعيًا متشابهًا بصورة جوهرية.

## حقوق التلاوات

مصدر الـAPI لا يعني تلقائيًا أن كل تسجيل صوتي متاح للاستخدام التجاري. يجب التحقق من حقوق وترخيص التلاوة المحددة المستخدمة في القناة قبل النشر أو تحقيق الدخل.

## أمان Git

الملفات التالية مستثناة من Git: البيانات المحلية، ملفات الصوت المؤقتة، نواتج الفيديو، مفاتيح OAuth، وملفات token. راجع `.gitignore` قبل أي commit.

## الترخيص

لم يتم تحديد ترخيص للمشروع بعد.
