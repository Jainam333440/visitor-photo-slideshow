import asyncio
import io
from pathlib import Path
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from aiohttp.test_utils import AioHTTPTestCase
from PIL import Image
from app import create_app
from store import MAX_BYTES, SECONDS, Store, normalize


def sample(fmt="PNG", **options):
    buf = io.BytesIO()
    Image.new("RGB", (20, 10), "coral").save(buf, fmt, **options)
    return buf.getvalue()


class PhotoChecks(unittest.TestCase):
    def test_reject_corrupt_and_wrong_format(self):
        for data in [b"hello", sample("GIF"), sample()[:-12]]:
            with self.subTest(length=len(data)), self.assertRaises(ValueError):
                normalize(data)

    def test_normalization_removes_metadata(self):
        exif = Image.Exif()
        exif[270] = "Private caption"
        with Image.open(io.BytesIO(normalize(sample("JPEG", exif=exif)))) as im:
            self.assertEqual(im.format, "JPEG")
            self.assertFalse(im.getexif())

    def test_pixel_and_animation_limits(self):
        buf = io.BytesIO()
        Image.new("1", (4001, 4000)).save(buf, "PNG")
        with self.assertRaises(ValueError):
            normalize(buf.getvalue())
        buf = io.BytesIO()
        Image.new("RGB", (8, 8)).save(buf, "PNG", save_all=True,
            append_images=[Image.new("RGB", (8, 8), "red")])
        with self.assertRaises(ValueError):
            normalize(buf.getvalue())


class QueueChecks(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "event.sqlite3"
        self.store = Store(self.path)
        self.visitor = self.store.visit("Sam", "")

    def order(self):
        with self.store.transaction() as db:
            return [r[0] for r in db.execute("SELECT jpeg FROM queue JOIN photo ON photo.id=queue.photo ORDER BY queue.id")]

    def test_return_and_name_collision(self):
        self.store.upload(self.visitor["token"], b"first")
        other = self.store.visit("Sam", "")
        self.store.upload(other["token"], b"other")
        returning = Store(self.path).visit("Sam", self.visitor["code"])
        for item in [b"new", b"later"]:
            self.store.upload(returning["token"], item)
        self.assertEqual(self.order(), [b"first", b"other", b"new", b"first", b"later"])

    def test_concurrent_uploads_and_limit(self):
        with ThreadPoolExecutor(5) as pool:
            list(pool.map(lambda i: self.store.upload(self.visitor["token"], bytes([i])), range(5)))
        self.assertEqual(sorted(self.order()), [bytes([i]) for i in range(5)])
        with self.assertRaises(ValueError):
            self.store.upload(self.visitor["token"], b"x")
        self.assertEqual(len(self.order()), 5)

    def test_timing_and_erasure(self):
        for photo in [b"a", b"b"]:
            self.store.upload(self.visitor["token"], photo)
        now = time.time()
        first = self.store.current(now)["slide"]
        self.assertEqual(self.store.current(now+SECONDS-0.01)["slide"], first)
        self.assertNotEqual(self.store.current(now+SECONDS)["slide"], first)
        self.store.erase(self.visitor["code"])
        self.assertIsNone(self.store.current(now+SECONDS)["slide"])
        self.assertIsNone(self.store.image(first))
        with self.assertRaises(ValueError):
            self.store.visit("Sam", self.visitor["code"])


class HttpChecks(AioHTTPTestCase):
    async def test_error_responses_are_json_and_not_cached(self):
        responses = [
            await self.client.post("/api/visit", json={}),
            await self.client.get("/api/image/999"),
            await self.post("photo", data=io.BytesIO(b"x" * (MAX_BYTES + 1))),
        ]
        self.assertEqual([r.status for r in responses], [403, 404, 413])
        for response in responses:
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.headers.get("Cache-Control"), "no-store")
            self.assertIn("error", await response.json())

    async def get_application(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        return create_app(Path(self.tmp.name) / "test.sqlite3")

    async def post(self, path, **kw):
        headers = kw.pop("headers", {})
        return await self.client.post("/api/"+path, headers={"X-Guestbook":"1", **headers}, **kw)

    async def test_consent_and_pages(self):
        for path in ["/", "/display", "/static/visit.js", "/static/display.js", "/static/style.css"]:
            self.assertEqual((await self.client.get(path)).status, 200)
        for payload in [{"name":"Sam","consent":False}, {"name":" ","consent":True}, {"name":"Sam","consent":True,"code":"unknown"}]:
            self.assertEqual((await self.post("visit", json=payload)).status, 400)
        self.assertEqual((await self.client.post("/api/visit", json={})).status, 403)

    async def test_reject_oversize_and_unauthorized_decode(self):
        self.assertEqual((await self.post("photo", data=io.BytesIO(b"x"*(MAX_BYTES+1)))).status, 413)
        with patch("app.normalize", side_effect=AssertionError("Decoded before checking visit")):
            self.assertEqual((await self.post("photo", data=sample())).status, 400)

    async def test_two_visitors_upload_and_delete(self):
        forms = await asyncio.gather(*(self.post("visit", json={"name":"Kim","consent":True}) for _ in range(2)))
        visits = [await r.json() for r in forms]
        uploads = await asyncio.gather(*(self.post("photo", data=sample(), headers={"X-Visit":v["token"]}) for v in visits))
        self.assertEqual([r.status for r in uploads], [201, 201])
        slide = (await (await self.client.get("/api/current")).json())["slide"]
        response = await self.client.get(f"/api/image/{slide}")
        self.assertEqual(response.content_type, "image/jpeg")
        self.assertTrue((await response.read()).startswith(b"\xff\xd8"))
        for v in visits:
            self.assertEqual((await self.post("erase", json={"code":v["code"]})).status, 200)
        self.assertEqual((await self.client.get(f"/api/image/{slide}")).status, 404)
        self.assertIsNone((await (await self.client.get("/api/current")).json())["slide"])
