from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

def add_cover(mp3_path, image_path):
    """ מוסיף תמונה לקובץ MP3 """
    audio = MP3(mp3_path, ID3=ID3)

    # אם אין תגיות ID3, נוסיף אותן
    if audio.tags is None:
        audio.tags = ID3()

    # קריאת תמונת הקובץ
    with open(image_path, "rb") as img:
        image_data = img.read()

    # הוספת התמונה לקובץ MP3
    audio.tags.add(APIC(
        encoding=3,  # UTF-8
        mime="image/jpeg",  # סוג תמונה (image/png אם התמונה בפורמט PNG)
        type=3,  # 3 = תמונת עטיפה קדמית (Cover Front)
        desc="Cover",
        data=image_data
    ))

    # שמירת השינויים
    audio.save()
    # print(f"✅ תמונה נוספה בהצלחה לקובץ: {mp3_path}")

