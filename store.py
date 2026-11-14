"""SQLite-backed event state. All queue changes use a single write transaction."""
import hashlib
import io
import secrets
import sqlite3
import time
from contextlib import contextmanager

from PIL import Image, ImageOps, UnidentifiedImageError

SECONDS = 8
MAX_BYTES = 5 * 1024 * 1024


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def normalize(raw):
    try:
        with Image.open(io.BytesIO(raw), formats=["JPEG", "PNG"]) as im:
            if im.width * im.height > 16_000_000 or getattr(im, "n_frames", 1) != 1:
                raise ValueError("Use a still image under 16 megapixels.")
            if im.format == "PNG":
                if not raw.endswith(bytes.fromhex("0000000049454e44ae426082")):
                    raise ValueError("The PNG file is incomplete.")
                with Image.open(io.BytesIO(raw)) as probe:
                    probe.verify()
            im.load()
            rgba = ImageOps.exif_transpose(im).convert("RGBA")
            rgba.thumbnail((1920, 1920))
            canvas = Image.new("RGB", rgba.size, "white")
            canvas.paste(rgba, mask=rgba.getchannel("A"))
            output = io.BytesIO()
            canvas.save(output, "JPEG", quality=85)
            return output.getvalue()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, SyntaxError) as exc:
        raise ValueError("Choose an undamaged JPEG or PNG image.") from exc


class Store:
    def __init__(self, path):
        self.path = path
        with self.transaction() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS visitor(id INTEGER PRIMARY KEY, name TEXT, code TEXT UNIQUE);
                CREATE TABLE IF NOT EXISTS visit(token TEXT PRIMARY KEY, owner INTEGER REFERENCES visitor ON DELETE CASCADE,
                    consent_at REAL, uploads INTEGER DEFAULT 0);
                CREATE TABLE IF NOT EXISTS photo(id INTEGER PRIMARY KEY, owner INTEGER REFERENCES visitor ON DELETE CASCADE, jpeg BLOB);
                CREATE TABLE IF NOT EXISTS queue(id INTEGER PRIMARY KEY AUTOINCREMENT, photo INTEGER REFERENCES photo ON DELETE CASCADE,
                    started REAL);
            """)

    @contextmanager
    def transaction(self):
        db = sqlite3.connect(self.path, timeout=10)
        try:
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("BEGIN IMMEDIATE")
            with db:
                yield db
        finally:
            db.close()

    def visit(self, name, code):
        with self.transaction() as db:
            if code:
                row = db.execute("SELECT id FROM visitor WHERE code=?", (digest(code),)).fetchone()
                if not row:
                    raise ValueError("Return code was not recognized.")
                owner = row[0]
            else:
                code = secrets.token_urlsafe(18)
                owner = db.execute("INSERT INTO visitor(name,code) VALUES(?,?)", (name, digest(code))).lastrowid
            token = secrets.token_urlsafe(24)
            db.execute("INSERT INTO visit(token,owner,consent_at) VALUES(?,?,?)", (digest(token), owner, time.time()))
            return {"token": token, "code": code}

    def check_visit(self, token):
        with self.transaction() as db:
            if not db.execute("SELECT 1 FROM visit WHERE token=?", (digest(token),)).fetchone():
                raise ValueError("Start a visit before uploading.")

    def upload(self, token, jpeg):
        with self.transaction() as db:
            row = db.execute("SELECT owner, uploads FROM visit WHERE token=?", (digest(token),)).fetchone()
            if not row:
                raise ValueError("Start a visit before uploading.")
            owner, count = row
            previous = db.execute("SELECT id FROM photo WHERE owner=? ORDER BY id", (owner,)).fetchall()
            if count >= 5 or len(previous) >= 30:
                raise ValueError("Limit reached: five photos per visit and 30 saved photos.")
            photo = db.execute("INSERT INTO photo(owner,jpeg) VALUES(?,?)", (owner, jpeg)).lastrowid
            entries = [(photo,)] + (previous if count == 0 else [])
            db.executemany("INSERT INTO queue(photo) VALUES(?)", entries)
            db.execute("UPDATE visit SET uploads=uploads+1 WHERE token=?", (digest(token),))

    def current(self, now):
        with self.transaction() as db:
            db.execute("DELETE FROM queue WHERE started IS NOT NULL AND started<=?", (now - SECONDS,))
            row = db.execute("SELECT id,started FROM queue ORDER BY id LIMIT 1").fetchone()
            if not row:
                return {"slide": None}
            slide, started = row
            if started is None:
                db.execute("UPDATE queue SET started=? WHERE id=?", (now, slide))
            return {"slide": slide}

    def image(self, slide):
        with self.transaction() as db:
            return db.execute("""SELECT jpeg FROM queue JOIN photo ON photo.id=queue.photo
                WHERE queue.id=? AND started>?""", (slide, time.time()-SECONDS)).fetchone()

    def erase(self, code):
        with self.transaction() as db:
            if not db.execute("DELETE FROM visitor WHERE code=?", (digest(code),)).rowcount:
                raise ValueError("Return code was not recognized.")
