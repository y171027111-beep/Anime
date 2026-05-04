from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from config import CHANNEL_ID
from database import (
    get_anime, get_seasons, get_episodes, get_episode,
    get_top_animes, register_user, increment_downloads, get_episode_count
)
from keyboards import user_main_kb, seasons_kb, episodes_kb, top_kb, all_episodes_kb

user_router = Router()

# ─── /start ───────────────────────────────────────────────────────────────────

@user_router.message(CommandStart())
async def cmd_start(msg: Message):
    await register_user(msg.from_user.id, msg.from_user.username, msg.from_user.full_name)

    # /start 404  →  to'g'ridan anime ko'rsatish (kanaldan kelsa)
    args = msg.text.split()
    if len(args) > 1:
        await show_anime_card(msg, args[1])
        return

    await msg.answer(
        f"🎌 <b>Assalomu alaykum, {msg.from_user.first_name}!</b>\n\n"
        "🎬 Anime kodini yuboring yoki quyidagi bo'limlardan foydalaning.\n\n"
        f"📢 Kodlarni kanaldan toping: <b>{CHANNEL_ID}</b>",
        reply_markup=user_main_kb(),
        parse_mode="HTML"
    )

# ─── Tugmalar ─────────────────────────────────────────────────────────────────

@user_router.message(F.text == "🔥 Eng ko'p ko'rilgan animelar")
async def top_list(msg: Message):
    animes = await get_top_animes(10)
    if not animes:
        await msg.answer("📭 Hozircha anime mavjud emas.")
        return
    await msg.answer("🔥 <b>Eng ko'p ko'rilgan animelar:</b>", reply_markup=top_kb(animes), parse_mode="HTML")

@user_router.message(F.text == "🔍 Kod orqali qidirish")
async def search_hint(msg: Message):
    await msg.answer("🔢 <b>Anime kodini kiriting:</b>\n\nMasalan: <code>404</code>", parse_mode="HTML")

@user_router.message(F.text == "📢 Kanal")
async def channel_btn(msg: Message):
    await msg.answer(f"📢 Rasmiy kanal: <b>{CHANNEL_ID}</b>", parse_mode="HTML")

# ─── Kod kiritilganda ──────────────────────────────────────────────────────────

@user_router.message(F.text.regexp(r'^\d+$'))
async def handle_code(msg: Message):
    await show_anime_card(msg, msg.text.strip())

# ─── Anime kartasini ko'rsatish (poster + ma'lumot + FASL tugmalari) ──────────

async def show_anime_card(msg: Message, code: str):
    anime = await get_anime(code)
    if not anime:
        await msg.answer(
            f"❌ <b>{code}</b> kodli anime topilmadi.\n📢 Kodlar: <b>{CHANNEL_ID}</b>",
            parse_mode="HTML"
        )
        return

    await increment_downloads(code)
    seasons = await get_seasons(code)
    ep_count = await get_episode_count(code)

    caption = build_anime_caption(anime, ep_count)

    if anime['poster_id']:
        await msg.answer_photo(
            photo=anime['poster_id'],
            caption=caption,
            parse_mode="HTML",
            reply_markup=seasons_kb(seasons, code) if seasons else None
        )
    else:
        await msg.answer(caption, parse_mode="HTML",
                         reply_markup=seasons_kb(seasons, code) if seasons else None)

def build_anime_caption(anime, ep_count=0):
    return (
        f"🎬 | <b>{anime['title']}</b>\n"
        f"{'─'*20}\n"
        f"📅 Yil: <b>{anime['year']}</b>\n"
        f"🎭 Janr: <b>{anime['genres']}</b>\n"
        f"🌐 Til: <b>{anime['language']}</b>\n"
        f"🖥 Sifat: <b>{anime['quality']}</b>\n"
        + (f"📤 Yuklangan: <b>{anime['uploaded_at']}</b>\n" if anime['uploaded_at'] else "")
        + f"# KODI: « <code>{anime['code']}</code> »\n\n"
        f"🤖 BOT - @Anikineuzbot"
    )

# ─── Top dan anime tanlash ─────────────────────────────────────────────────────

@user_router.callback_query(F.data.startswith("anime:"))
async def cb_anime(cb: CallbackQuery):
    code = cb.data.split(":")[1]
    await show_anime_card(cb.message, code)
    await cb.answer()

# ─── Fasl tanlash → qismlar ro'yxati ─────────────────────────────────────────

@user_router.callback_query(F.data.startswith("season:"))
async def cb_season(cb: CallbackQuery):
    season_id = int(cb.data.split(":")[1])
    episodes = await get_episodes(season_id)

    from database import get_season
    season = await get_season(season_id)
    anime_code = season['anime_code']

    if not episodes:
        await cb.answer("📭 Bu faslda qism yo'q!", show_alert=True)
        return

    text = f"📺 <b>{season['number']}-FASL — Qismlar ro'yxati:</b>\n\n"
    text += f"Jami: <b>{len(episodes)} ta qism</b>"

    await cb.message.answer(text, reply_markup=episodes_kb(episodes, season_id, anime_code), parse_mode="HTML")
    await cb.answer()

# ─── Fasllarga qaytish ────────────────────────────────────────────────────────

@user_router.callback_query(F.data.startswith("seasons:"))
async def cb_seasons(cb: CallbackQuery):
    anime_code = cb.data.split(":")[1]
    anime = await get_anime(anime_code)
    seasons = await get_seasons(anime_code)
    ep_count = await get_episode_count(anime_code)

    if not seasons:
        await cb.answer("📭 Fasl yo'q!", show_alert=True)
        return

    caption = build_anime_caption(anime, ep_count)
    await cb.message.answer(caption, reply_markup=seasons_kb(seasons, anime_code), parse_mode="HTML")
    await cb.answer()

# ─── Qism bosildi → video + tagida barcha qismlar ────────────────────────────

@user_router.callback_query(F.data.startswith("ep:"))
async def cb_episode(cb: CallbackQuery):
    ep_id = int(cb.data.split(":")[1])
    ep = await get_episode(ep_id)
    if not ep:
        await cb.answer("❌ Qism topilmadi!", show_alert=True)
        return

    from database import get_season
    season = await get_season(ep['season_id'])
    all_eps = await get_episodes(ep['season_id'])
    ids = [e['id'] for e in all_eps]
    idx = ids.index(ep_id)
    has_prev = idx > 0
    has_next = idx < len(ids) - 1

    anime = await get_anime(ep['anime_code'])

    # Caption: anime nomi + fasl/qism
    caption = (
        f"🎬 <b>{anime['title']}</b>\n"
        f"📺 {season['number']}-FASL • {ep['number']}-qism"
        + (f" — {ep['title']}" if ep['title'] else "") + "\n"
        f"🌐 {anime['language']}  •  🖥 {anime['quality']}\n"
        f"# KOD: <code>{anime['code']}</code>"
    )

    # Video tagida: barcha qismlar + oldingi/keyingi + qaytish
    kb = all_episodes_kb(all_eps, ep_id, ep['season_id'], ep['anime_code'], has_prev, has_next)

    if ep['file_type'] == 'video':
        await cb.message.answer_video(video=ep['file_id'], caption=caption, parse_mode="HTML", reply_markup=kb)
    elif ep['file_type'] == 'photo':
        await cb.message.answer_photo(photo=ep['file_id'], caption=caption, parse_mode="HTML", reply_markup=kb)
    else:
        await cb.message.answer_document(document=ep['file_id'], caption=caption, parse_mode="HTML", reply_markup=kb)

    await cb.answer()

# ─── Oldingi / Keyingi qism ────────────────────────────────────────────────────

@user_router.callback_query(F.data.startswith("next:") | F.data.startswith("prev:"))
async def cb_nav(cb: CallbackQuery):
    parts = cb.data.split(":")
    direction, ep_id, season_id, anime_code = parts[0], int(parts[1]), int(parts[2]), parts[3]

    all_eps = await get_episodes(season_id)
    ids = [e['id'] for e in all_eps]
    idx = ids.index(ep_id)

    new_idx = idx + 1 if direction == "next" else idx - 1
    if new_idx < 0 or new_idx >= len(ids):
        await cb.answer("Bu tomon qism yo'q!", show_alert=True)
        return

    new_ep_id = ids[new_idx]
    # Qayta ishlatish uchun callback data o'zgartiramiz
    cb.data = f"ep:{new_ep_id}"
    await cb_episode(cb)

# ─── Home ─────────────────────────────────────────────────────────────────────

@user_router.callback_query(F.data == "home")
async def cb_home(cb: CallbackQuery):
    await cb.message.answer("🏠 Bosh sahifa:", reply_markup=user_main_kb())
    await cb.answer()