import aiosqlite

DB_PATH = "data/sciscinet_vt_cs.db"


async def get_db():
    """Get async database connection."""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db
