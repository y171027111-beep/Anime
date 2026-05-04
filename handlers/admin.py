import random
from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_IDS, CHANNEL_ID
from database import (
    add_anime, get_anime, get_all_animes, delete_anime,
    get_user_count, get_top_animes, add_season, add_episode,
    get_seasons, get_episodes, get_episode_count, get_all_user_ids
)
from keyboards import admin_main_kb, cancel_kb, skip_kb, admin_anime_kb, user_main_kb

admin_router = Router()

def is_admin(uid): return uid in ADMIN_IDS

# ─── FSM ──────────────────────────────────────────────────────────────────────

class AddAnime(StatesGroup):
    poster   = State()
    title    = State()
    year     = State()
    quality  = State()
    language = State()
    genres   = State()
    code     = State()

class AddEpisode(StatesGroup):
    anime_code = State()
    season_num = State()
    ep_number  = State()
    ep_title   = State()
    file       = State()

class DeleteAnime(StatesGroup):
    code = State()

class Broadcast(StatesGroup):
    text = State()

# ─── Admin panel ──────────────────────────────────────────────────────────────

@admin_router.message(Command("admin"))
async def admin_panel(msg: Message):
    if not is_admin(msg.from_user.id):
        await msg.answer("⛔ Ruxsat yo'q!")
        return
    await msg.answer("⚙️ <b>Admin panel</b>", reply_markup=admin_main_kb(), parse_mode="HTML")

# ─── Statistika ───────────────────────────────────────────────────────────────

@admin_router.message(F.text == "📊 Statistika")
async def stats(msg: Message):
    if not is_admin(msg.from_user.id): return
    users = await get_user_count()
    animes = await get_all_animes()
    total_dl = sum(a['downloads'] for a in animes)
    top = await get_top_animes(1)
    best = top[0]['title'] if top else "—"
    await msg.answer(
        f"📊 <b>Statistika</b>\n\n"
        f"👤 Foydalanuvchilar: <b>{users}</b>\n"
        f"🎬 Animlar: <b>{len(animes)}</b>\n"
        f"📥 Jami ko'rilgan: <b>{total_dl}</b>\n"
        f"🔥 Eng mashhur: <b>{best}</b>",
        parse_mode="HTML"
    )

# ─── Barcha animlar ───────────────────────────────────────────────────────────

@admin_router.message(F.text == "📋 Barcha animlar")
async def all_animes(msg: Message):
    if not is_admin(msg.from_user.id): return
    animes = await get_all_animes()
    if not animes:
        await msg.answer("📭 Ma'lumotlar bazasi bo'sh.")
        return
    for a in animes:
        seasons = await get_seasons(a['code'])
        ep_count = await get_episode_count(a['code'])
        text = (
            f"🎬 <b>{a['title']}</b>\n"
            f"📅 {a['year']} | 🖥 {a['quality']}\n"
            f"📺 {len(seasons)} fasl | {ep_count} qism | 👁 {a['downloads']}\n"
            f"# KOD: <code>{a['code']}</code>"
        )
        await msg.answer(text, reply_markup=admin_anime_kb(a['code']), parse_mode="HTML")

# ══════════════════════════════════════════════════════════════════════════════
#  ANIME QO'SHISH FSM
# ══════════════════════════════════════════════════════════════════════════════

@admin_router.message(F.text == "➕ Anime qo'shish")
async def start_add_anime(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id): return
    await state.set_state(AddAnime.poster)
    await msg.answer(
        "🖼 <b>1/7 — Anime posterini yuboring:</b>\n\n"
        "(Rasm yoki video trailer)",
        reply_markup=skip_kb(), parse_mode="HTML"
    )

@admin_router.message(AddAnime.poster)
async def got_poster(msg: Message, state: FSMContext):
    if msg.text == "❌ Bekor qilish": await _cancel(msg, state); return
    poster_id = None
    if msg.photo:
        poster_id = msg.photo[-1].file_id
    elif msg.video:
        poster_id = msg.video.file_id
    await state.update_data(poster_id=poster_id)
    await state.set_state(AddAnime.title)
    await msg.answer("✏️ <b>2/7 — Anime nomini kiriting:</b>", parse_mode="HTML", reply_markup=cancel_kb())

@admin_router.message(AddAnime.title)
async def got_title(msg: Message, state: FSMContext):
    if msg.text == "❌ Bekor qilish": await _cancel(msg, state); return
    await state.update_data(title=msg.text.strip())
    await state.set_state(AddAnime.year)
    await msg.answer("📅 <b>3/7 — Yilini kiriting:</b>\n<code>2024</code>", parse_mode="HTML")

@admin_router.message(AddAnime.year)
async def got_year(msg: Message, state: FSMContext):
    if msg.text == "❌ Bekor qilish": await _cancel(msg, state); return
    await state.update_data(year=msg.text.strip())
    await state.set_state(AddAnime.quality)
    await msg.answer("🖥 <b>4/7 — Sifatini kiriting:</b>\n<code>720p 1080p</code>", parse_mode="HTML")

@admin_router.message(AddAnime.quality)
async def got_quality(msg: Message, state: FSMContext):
    if msg.text == "❌ Bekor qilish": await _cancel(msg, state); return
    await state.update_data(quality=msg.text.strip())
    await state.set_state(AddAnime.language)
    await msg.answer("🌐 <b>5/7 — Tilini kiriting:</b>\n<code>Uzbek tilida</code>", parse_mode="HTML")

@admin_router.message(AddAnime.language)
async def got_language(msg: Message, state: FSMContext):
    if msg.text == "❌ Bekor qilish": await _cancel(msg, state); return
    await state.update_data(language=msg.text.strip())
    await state.set_state(AddAnime.genres)
    await msg.answer("🎭 <b>6/7 — Janrini kiriting:</b>\n<code>Ekshn, Fenteziya, Sarguzasht</code>", parse_mode="HTML")

@admin_router.message(AddAnime.genres)
async def got_genres(msg: Message, state: FSMContext):
    if msg.text == "❌ Bekor qilish": await _cancel(msg, state); return
    await state.update_data(genres=msg.text.strip())
    auto_code = str(random.randint(100, 999))
    await state.set_state(AddAnime.code)
    await msg.answer(
        f"🔢 <b>7/7 — Kodni kiriting:</b>\n\n"
        f"Taklif: <code>{auto_code}</code>\n"
        f"(Yoki o'z raqamingizni kiriting)",
        parse_mode="HTML"
    )

@admin_router.message(AddAnime.code)
async def got_code(msg: Message, state: FSMContext):
    if msg.text == "❌ Bekor qilish": await _cancel(msg, state); return
    code = msg.text.strip()
    data = await state.get_data()

    # Windows va Linux ikkalasida ishlaydi
    now = datetime.now()
    uploaded_at = f"{now.day} {now.strftime('%B').lower()}"

    await add_anime(
        code=code,
        title=data['title'],
        year=data.get('year', '2024'),
        language=data.get('language', 'Uzbek tilida'),
        quality=data.get('quality', '720p 1080p'),
        genres=data.get('genres', ''),
        poster_id=data.get('poster_id'),
        uploaded_at=uploaded_at
    )
    await state.clear()

    await msg.answer(
        f"✅ <b>{data['title']}</b> qo'shildi!\n"
        f"# KOD: <code>{code}</code>\n\n"
        f"Endi <b>fasl va qismlarni</b> qo'shing 👇",
        reply_markup=admin_main_kb(), parse_mode="HTML"
    )
    await msg.answer(
        "📢 Kanalga yuborishni xohlaysizmi?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📢 Ha, kanalga yuborish", callback_data=f"send_ch:{code}"),
                InlineKeyboardButton(text="➕ Qism qo'shish", callback_data=f"addep:{code}"),
            ]
        ])
    )

# ══════════════════════════════════════════════════════════════════════════════
#  FASL + QISM QO'SHISH FSM
# ══════════════════════════════════════════════════════════════════════════════

@admin_router.callback_query(F.data.startswith("addep:"))
async def start_add_episode(cb: CallbackQuery, state: FSMContext):
    if not is_admin(cb.from_user.id): return
    code = cb.data.split(":")[1]
    await state.set_state(AddEpisode.anime_code)
    await state.update_data(anime_code=code)
    await state.set_state(AddEpisode.season_num)

    seasons = await get_seasons(code)
    existing = ", ".join([str(s['number']) for s in seasons]) if seasons else "yo'q"
    await cb.message.answer(
        f"📺 <b>Qaysi faslga qo'shish?</b>\n\n"
        f"Mavjud fasllar: <b>{existing}</b>\n\n"
        f"Fasl raqamini kiriting (masalan: <code>1</code>)",
        reply_markup=cancel_kb(), parse_mode="HTML"
    )
    await cb.answer()

@admin_router.message(AddEpisode.season_num)
async def got_season_num(msg: Message, state: FSMContext):
    if msg.text == "❌ Bekor qilish": await _cancel(msg, state); return
    if not msg.text.isdigit():
        await msg.answer("❌ Raqam kiriting!"); return
    await state.update_data(season_num=int(msg.text))
    await state.set_state(AddEpisode.ep_number)
    await msg.answer(
        "🔢 <b>Qism raqamini kiriting:</b>\n<code>1</code>",
        parse_mode="HTML"
    )

@admin_router.message(AddEpisode.ep_number)
async def got_ep_number(msg: Message, state: FSMContext):
    if msg.text == "❌ Bekor qilish": await _cancel(msg, state); return
    if not msg.text.isdigit():
        await msg.answer("❌ Raqam kiriting!"); return
    await state.update_data(ep_number=int(msg.text))
    await state.set_state(AddEpisode.ep_title)
    await msg.answer(
        "✏️ <b>Qism nomini kiriting (ixtiyoriy):</b>\n\n"
        "Masalan: <code>Birinchi uchrashuv</code>\n"
        "Yoki o'tkazib yuboring",
        reply_markup=skip_kb(), parse_mode="HTML"
    )

@admin_router.message(AddEpisode.ep_title)
async def got_ep_title(msg: Message, state: FSMContext):
    if msg.text == "❌ Bekor qilish": await _cancel(msg, state); return
    title = "" if msg.text == "⏭ O'tkazib yuborish" else msg.text.strip()
    await state.update_data(ep_title=title)
    await state.set_state(AddEpisode.file)
    await msg.answer(
        "🎬 <b>Qism videosini yuboring:</b>\n\n"
        "(Video, gif yoki rasm)",
        reply_markup=cancel_kb(), parse_mode="HTML"
    )

@admin_router.message(AddEpisode.file)
async def got_ep_file(msg: Message, state: FSMContext):
    if msg.text == "❌ Bekor qilish": await _cancel(msg, state); return

    file_id, file_type, duration = None, None, ""
    if msg.video:
        file_id = msg.video.file_id
        file_type = "video"
        secs = msg.video.duration or 0
        duration = f"{secs//60}:{secs%60:02d}"
    elif msg.photo:
        file_id = msg.photo[-1].file_id
        file_type = "photo"
    elif msg.document:
        file_id = msg.document.file_id
        file_type = "document"
    elif msg.animation:
        file_id = msg.animation.file_id
        file_type = "video"

    if not file_id:
        await msg.answer("❌ Fayl yuboring!"); return

    data = await state.get_data()
    await state.clear()

    anime_code = data['anime_code']
    season_num = data['season_num']
    ep_number  = data['ep_number']
    ep_title   = data.get('ep_title', '')

    # Fasl yaratish (yoki mavjudni topish)
    season_id = await add_season(anime_code, season_num)

    # Qism qo'shish
    await add_episode(season_id, anime_code, ep_number, ep_title, file_id, file_type, duration)

    anime = await get_anime(anime_code)
    await msg.answer(
        f"✅ <b>{anime['title']}</b>\n"
        f"📺 {season_num}-FASL | {ep_number}-qism qo'shildi!"
        + (f"\n📝 {ep_title}" if ep_title else ""),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Yana qism qo'shish", callback_data=f"addep:{anime_code}"),
                InlineKeyboardButton(text="📢 Kanalga yuborish", callback_data=f"send_ch:{anime_code}"),
            ],
            [InlineKeyboardButton(text="🏠 Admin panel", callback_data="admin_home")]
        ]),
        parse_mode="HTML"
    )

# ─── Kanalga yuborish ─────────────────────────────────────────────────────────

@admin_router.callback_query(F.data.startswith("send_ch:"))
async def send_to_channel(cb: CallbackQuery):
    if not is_admin(cb.from_user.id): return
    code = cb.data.split(":")[1]
    anime = await get_anime(code)
    if not anime:
        await cb.answer("❌ Topilmadi!", show_alert=True); return

    bot_info = await cb.bot.get_me()
    seasons = await get_seasons(code)
    ep_count = await get_episode_count(code)

    caption = (
        f"🎬 | <b>{anime['title']}</b>\n"
        f"{'─'*20}\n"
        f"📅 Yil: <b>{anime['year']}</b>\n"
        f"🎭 Janr: <b>{anime['genres']}</b>\n"
        f"🌐 Til: <b>{anime['language']}</b>\n"
        f"🖥 Sifat: <b>{anime['quality']}</b>\n"
        + (f"📤 Yuklangan: <b>{anime['uploaded_at']}</b>\n" if anime['uploaded_at'] else "")
        + f"# KODI: « <code>{code}</code> »\n\n"
        f"🤖 BOT - @{bot_info.username}"
    )

    # Fasl tugmalari — rasmdagiday
    season_buttons = []
    for s in seasons:
        season_buttons.append([InlineKeyboardButton(
            text=f"{s['number']}-FASL",
            url=f"https://t.me/{bot_info.username}?start={code}"
        )])

    # Agar fasl yo'q bo'lsa bitta tugma
    if not season_buttons:
        season_buttons = [[InlineKeyboardButton(
            text="▶️ Ko'rish",
            url=f"https://t.me/{bot_info.username}?start={code}"
        )]]

    kb = InlineKeyboardMarkup(inline_keyboard=season_buttons)

    try:
        if anime['poster_id']:
            await cb.bot.send_photo(
                CHANNEL_ID,
                photo=anime['poster_id'],
                caption=caption,
                parse_mode="HTML",
                reply_markup=kb
            )
        else:
            await cb.bot.send_message(CHANNEL_ID, caption, parse_mode="HTML", reply_markup=kb)

        await cb.answer("✅ Kanalga yuborildi!", show_alert=True)
    except Exception as e:
        await cb.answer(f"❌ Xato: {e}", show_alert=True)

# ─── Anime o'chirish ──────────────────────────────────────────────────────────

@admin_router.message(F.text == "🗑 Anime o'chirish")
async def start_delete(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id): return
    await state.set_state(DeleteAnime.code)
    await msg.answer("🔢 O'chirish uchun anime kodini kiriting:", reply_markup=cancel_kb())

@admin_router.message(DeleteAnime.code)
async def do_delete(msg: Message, state: FSMContext):
    if msg.text == "❌ Bekor qilish": await _cancel(msg, state); return
    await delete_anime(msg.text.strip())
    await state.clear()
    await msg.answer(f"✅ <code>{msg.text}</code> o'chirildi.", reply_markup=admin_main_kb(), parse_mode="HTML")

@admin_router.callback_query(F.data.startswith("del:"))
async def del_inline(cb: CallbackQuery):
    if not is_admin(cb.from_user.id): return
    code = cb.data.split(":")[1]
    await delete_anime(code)
    await cb.message.delete()
    await cb.answer(f"✅ {code} o'chirildi!", show_alert=True)

# ─── Broadcast ────────────────────────────────────────────────────────────────

@admin_router.message(F.text == "📣 Xabar yuborish")
async def start_broadcast(msg: Message, state: FSMContext):
    if not is_admin(msg.from_user.id): return
    await state.set_state(Broadcast.text)
    await msg.answer("✍️ Barcha foydalanuvchilarga yuboriladigan xabarni kiriting:", reply_markup=cancel_kb())

@admin_router.message(Broadcast.text)
async def do_broadcast(msg: Message, state: FSMContext):
    if msg.text == "❌ Bekor qilish": await _cancel(msg, state); return
    await state.clear()
    users = await get_all_user_ids()
    ok, fail = 0, 0
    for (uid,) in users:
        try:
            await msg.bot.send_message(uid, msg.text, parse_mode="HTML")
            ok += 1
        except:
            fail += 1
    await msg.answer(f"📣 Yuborildi!\n✅ {ok} ta\n❌ {fail} ta", reply_markup=admin_main_kb())

# ─── Foydalanuvchi paneli ─────────────────────────────────────────────────────

@admin_router.message(F.text == "👤 Foydalanuvchi paneli")
async def to_user_panel(msg: Message):
    if not is_admin(msg.from_user.id): return
    await msg.answer("👤 Foydalanuvchi paneli:", reply_markup=user_main_kb())

# ─── Admin home callback ──────────────────────────────────────────────────────

@admin_router.callback_query(F.data == "admin_home")
async def cb_admin_home(cb: CallbackQuery):
    await cb.message.answer("⚙️ Admin panel:", reply_markup=admin_main_kb())
    await cb.answer()

# ─── Bekor qilish ─────────────────────────────────────────────────────────────

async def _cancel(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("❌ Bekor qilindi.", reply_markup=admin_main_kb())