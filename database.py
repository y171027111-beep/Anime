import aiosqlite

DB = "anime.db"

async def init_db():
    async with aiosqlite.connect(DB) as db:
        # Animlar jadvali
        await db.execute("""
        CREATE TABLE IF NOT EXISTS animes (
            code        TEXT PRIMARY KEY,
            title       TEXT NOT NULL,
            year        INTEGER DEFAULT 2024,
            language    TEXT DEFAULT 'Uzbek tilida',
            quality     TEXT DEFAULT '720p 1080p',
            genres      TEXT DEFAULT '',
            poster_id   TEXT,
            uploaded_at TEXT DEFAULT '',
            downloads   INTEGER DEFAULT 0,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")

        # Fasllar jadvali  (1-FASL, 2-FASL ...)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS seasons (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            anime_code  TEXT NOT NULL,
            number      INTEGER NOT NULL,
            title       TEXT DEFAULT '',
            UNIQUE(anime_code, number),
            FOREIGN KEY(anime_code) REFERENCES animes(code) ON DELETE CASCADE
        )""")

        # Qismlar jadvali  (1-qism, 2-qism ...)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS episodes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            season_id   INTEGER NOT NULL,
            anime_code  TEXT NOT NULL,
            number      INTEGER NOT NULL,
            title       TEXT DEFAULT '',
            file_id     TEXT NOT NULL,
            file_type   TEXT DEFAULT 'video',
            duration    TEXT DEFAULT '',
            FOREIGN KEY(season_id) REFERENCES seasons(id) ON DELETE CASCADE
        )""")

        # Foydalanuvchilar
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id        INTEGER PRIMARY KEY,
            username  TEXT,
            full_name TEXT,
            joined_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")

        await db.commit()

# ─── ANIME ────────────────────────────────────────────────────────────────────

async def add_anime(code, title, year, language, quality, genres, poster_id, uploaded_at):
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
            INSERT OR REPLACE INTO animes
            (code,title,year,language,quality,genres,poster_id,uploaded_at)
            VALUES(?,?,?,?,?,?,?,?)
        """, (code, title, year, language, quality, genres, poster_id, uploaded_at))
        await db.commit()

async def get_anime(code):
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM animes WHERE code=?", (code,)) as c:
            return await c.fetchone()

async def get_all_animes():
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM animes ORDER BY created_at DESC") as c:
            return await c.fetchall()

async def get_top_animes(limit=10):
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM animes ORDER BY downloads DESC LIMIT ?", (limit,)) as c:
            return await c.fetchall()

async def delete_anime(code):
    async with aiosqlite.connect(DB) as db:
        await db.execute("DELETE FROM animes WHERE code=?", (code,))
        await db.commit()

async def increment_downloads(code):
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE animes SET downloads=downloads+1 WHERE code=?", (code,))
        await db.commit()

# ─── SEASONS ──────────────────────────────────────────────────────────────────

async def add_season(anime_code, number, title=""):
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
            INSERT OR IGNORE INTO seasons (anime_code, number, title)
            VALUES (?, ?, ?)
        """, (anime_code, number, title))
        await db.commit()
        async with db.execute(
            "SELECT id FROM seasons WHERE anime_code=? AND number=?", (anime_code, number)
        ) as c:
            row = await c.fetchone()
            return row[0] if row else None

async def get_seasons(anime_code):
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM seasons WHERE anime_code=? ORDER BY number", (anime_code,)
        ) as c:
            return await c.fetchall()

async def get_season(season_id):
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM seasons WHERE id=?", (season_id,)) as c:
            return await c.fetchone()

# ─── EPISODES ─────────────────────────────────────────────────────────────────

async def add_episode(season_id, anime_code, number, title, file_id, file_type, duration):
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
            INSERT INTO episodes (season_id, anime_code, number, title, file_id, file_type, duration)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (season_id, anime_code, number, title, file_id, file_type, duration))
        await db.commit()

async def get_episodes(season_id):
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM episodes WHERE season_id=? ORDER BY number", (season_id,)
        ) as c:
            return await c.fetchall()

async def get_episode(ep_id):
    async with aiosqlite.connect(DB) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM episodes WHERE id=?", (ep_id,)) as c:
            return await c.fetchone()

async def delete_episode(ep_id):
    async with aiosqlite.connect(DB) as db:
        await db.execute("DELETE FROM episodes WHERE id=?", (ep_id,))
        await db.commit()

async def get_episode_count(anime_code):
    async with aiosqlite.connect(DB) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM episodes WHERE anime_code=?", (anime_code,)
        ) as c:
            row = await c.fetchone()
            return row[0]

# ─── USERS ────────────────────────────────────────────────────────────────────

async def register_user(uid, username, full_name):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (id,username,full_name) VALUES(?,?,?)",
            (uid, username, full_name)
        )
        await db.commit()

async def get_user_count():
    async with aiosqlite.connect(DB) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as c:
            return (await c.fetchone())[0]

async def get_all_user_ids():
    async with aiosqlite.connect(DB) as db:
        async with db.execute("SELECT id FROM users") as c:
            return await c.fetchall()
