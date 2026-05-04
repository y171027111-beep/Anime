# 🎌 Anime Bot — To'liq qo'llanma

## Tuzilma
```
anime_bot_v2/
├── bot.py
├── config.py
├── database.py
├── keyboards.py
├── requirements.txt
└── handlers/
    ├── __init__.py
    ├── user.py
    └── admin.py
```

## O'rnatish
```bash
pip install -r requirements.txt
```

## config.py ni to'ldiring
```python
BOT_TOKEN  = "1234567890:AAA..."    # @BotFather
CHANNEL_ID = "@sizning_kanalingiz"  # Bot kanal admin bo'lishi shart!
ADMIN_IDS  = [123456789]            # @userinfobot orqali ID oling
```

## Ishga tushirish
```bash
python bot.py
```

---

## Qanday ishlaydi?

### Foydalanuvchi:
1. Kanaldan postni ko'radi — **1-FASL** tugmasini bosadi
2. Yoki botga **kod** yozadi (masalan `404`)
3. Bot posterni + ma'lumotni ko'rsatadi + **1-FASL, 2-FASL...** tugmalari
4. Faslni bosadi → **1-qism, 2-qism...** tugmalari chiqadi
5. Qismni bosadi → **video yuboriladi** + Oldingi/Keyingi tugmalar

### Admin (`/admin`):
| Tugma | Nima qiladi |
|---|---|
| ➕ Anime qo'shish | Poster, nom, yil, sifat, til, janr, kod so'raydi |
| ➕ Fasl/Qism qo'shish | Fasl raqami, qism raqami, nom (ixtiyoriy), video so'raydi |
| 📢 Kanalga yuborish | Rasmga o'xshash format: poster + ma'lumot + FASL tugmalari |
| 📋 Barcha animlar | Hammasi + qo'shish/o'chirish tugmalari |
| 📊 Statistika | Foydalanuvchi, anime, ko'rilish soni |
| 📣 Xabar yuborish | Hammaga broadcast |

### Kanal post formati (3-rasmga o'xshash):
```
🎬 | Iblis lordi 2099
────────────────────
📅 Yil: 2024
🎭 Janr: Ekshn, Fenteziya, Sarguzasht
🌐 Til: Uzbek tilida
🖥 Sifat: 720p 1080p
📤 Yuklangan: 2 marta
# KODI: « 404 »
🤖 BOT - @Anikineuzbot

[1-FASL]
[2-FASL]   ← botga olib boradi
```
