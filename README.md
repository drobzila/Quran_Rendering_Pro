# Quran Rendering Pro 🌙

نسخة مطوّرة من `Quran_rendering` لإنشاء فيديوهات قرآن عمودية 9:16 مع تنوع حقيقي في التصميم بدل تكرار قالب واحد.

## ما الجديد؟

- خمسة أنماط بصرية مختلفة: `minimal`, `cinematic`, `mushaf`, `night`, `golden`.
- تدوير الأنماط عند التوليد الدفعي.
- اختيار آيات لم تُستخدم سابقًا.
- جلب التلاوة آليًا.
- إخراج 1080×1920 مناسب لـ Shorts.
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

## إنشاء دفعة

```bash
BATCH_COUNT=10 python generate_batch.py
```

أو:

```bash
BATCH_COUNT=20 OUTPUT_DIR=batch_output python generate_batch.py
```

## اختيار نمط محدد

```bash
VIDEO_STYLE=night python Quran.py
```

## ملاحظة YouTube

تنوع القوالب وحده لا يضمن تحقيق الدخل. الهدف هو جعل كل فيديو مختلفًا بصريًا وبنيته أوضح، مع الحفاظ على قيمة المحتوى القرآني. يجب التأكد من حقوق وتراخيص التلاوات والمواد المستخدمة قبل النشر التجاري.

## البيانات

`setup_data.py` ينزّل `quran.json` عند الحاجة بدل تخزين ملف JSON كبير داخل المستودع. وملف البيانات الناتج مستثنى من Git.

## الترخيص

لم يتم تحديد ترخيص للمشروع بعد.
