from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)

# ─── USER ─────────────────────────────────────────────────────────────────────

def user_main_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🔥 Eng ko'p ko'rilgan animelar")],
        [KeyboardButton(text="🔍 Kod orqali qidirish"), KeyboardButton(text="📢 Kanal")],
    ], resize_keyboard=True)

# ─── Anime topilganda — fasllar tugmalari ─────────────────────────────────────

def seasons_kb(seasons, anime_code):
    """Har bir fasl uchun tugma — rasmdagiday: 1-FASL, 2-FASL ..."""
    buttons = []
    for s in seasons:
        buttons.append([InlineKeyboardButton(
            text=f"{s['number']}-FASL",
            callback_data=f"season:{s['id']}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ─── Qismlar ro'yxati ─────────────────────────────────────────────────────────

def episodes_kb(episodes, season_id, anime_code):
    """Har bir qism uchun tugma — 1-qism, 2-qism ..."""
    buttons = []
    row = []
    for i, ep in enumerate(episodes):
        label = f"{ep['number']}-qism"
        if ep['title']:
            label += f" | {ep['title'][:20]}"
        row.append(InlineKeyboardButton(
            text=f"▶ {ep['number']}-qism",
            callback_data=f"ep:{ep['id']}"
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="⬅️ Fasllarga qaytish", callback_data=f"seasons:{anime_code}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ─── Qism ko'rilgandan keyin ──────────────────────────────────────────────────

def all_episodes_kb(episodes, current_ep_id, season_id, anime_code, has_prev, has_next):
    """Video tagida: barcha qismlar + oldingi/keyingi + qaytish — 2-rasmdagiday"""
    buttons = []

    # Barcha qismlar — 4 tadan qator
    row = []
    for ep in episodes:
        label = f"▶ {ep['number']}-qism" if ep['id'] == current_ep_id else f"{ep['number']}-qism"
        row.append(InlineKeyboardButton(
            text=label,
            callback_data=f"ep:{ep['id']}"
        ))
        if len(row) == 4:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    # Oldingi / Keyingi navigatsiya
    nav = []
    if has_prev:
        nav.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"prev:{current_ep_id}:{season_id}:{anime_code}"))
    if has_next:
        nav.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"next:{current_ep_id}:{season_id}:{anime_code}"))
    if nav:
        buttons.append(nav)

    # Fasllarga qaytish
    buttons.append([InlineKeyboardButton(text="⬅️ Fasllarga qaytish", callback_data=f"seasons:{anime_code}")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


    buttons = []
    nav = []
    if has_prev:
        nav.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"prev:{ep_id}:{season_id}:{anime_code}"))
    if has_next:
        nav.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"next:{ep_id}:{season_id}:{anime_code}"))
    if nav:
        buttons.append(nav)
    buttons.append([InlineKeyboardButton(text="📋 Barcha qismlar", callback_data=f"season:{season_id}")])
    buttons.append([InlineKeyboardButton(text="🏠 Bosh sahifa", callback_data="home")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ─── TOP ro'yxat ──────────────────────────────────────────────────────────────

def top_kb(animes):
    medals = ["🥇","🥈","🥉"]
    buttons = []
    for i, a in enumerate(animes):
        icon = medals[i] if i < 3 else f"{i+1}."
        buttons.append([InlineKeyboardButton(
            text=f"{icon} {a['title']}  |  KOD: {a['code']}",
            callback_data=f"anime:{a['code']}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ─── ADMIN ────────────────────────────────────────────────────────────────────

def admin_main_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="➕ Anime qo'shish")],
        [KeyboardButton(text="📋 Barcha animlar"), KeyboardButton(text="📊 Statistika")],
        [KeyboardButton(text="📣 Xabar yuborish"), KeyboardButton(text="🗑 Anime o'chirish")],
        [KeyboardButton(text="👤 Foydalanuvchi paneli")],
    ], resize_keyboard=True)

def cancel_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="❌ Bekor qilish")]
    ], resize_keyboard=True)

def skip_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="⏭ O'tkazib yuborish"), KeyboardButton(text="❌ Bekor qilish")]
    ], resize_keyboard=True)

def admin_anime_kb(code):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Fasl/Qism qo'shish", callback_data=f"addep:{code}"),
            InlineKeyboardButton(text="📢 Kanalga", callback_data=f"send_ch:{code}"),
        ],
        [InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"del:{code}")]
    ])