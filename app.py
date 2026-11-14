"""Run with python app.py. The display and visitor pages share this server."""
import asyncio
import os
import time
from pathlib import Path

from aiohttp import web
from store import MAX_BYTES, Store, normalize

STATIC = Path(__file__).resolve().parent / "static"


@web.middleware
async def policy(request, handler):
    if request.method == "POST" and request.headers.get("X-Guestbook") != "1":
        raise web.HTTPForbidden(text="Use the visitor form.")
    try:
        response = await handler(request)
    except ValueError as exc:
        response = web.json_response({"error": str(exc)}, status=400)
    response.headers.update({"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff",
                             "Referrer-Policy": "no-referrer", "X-Frame-Options": "DENY"})
    return response


def create_app(path):
    store = Store(path)
    app = web.Application(middlewares=[policy], client_max_size=MAX_BYTES + 1)
    slots = asyncio.Semaphore(2)

    async def visit(request):
        data = await request.json()
        if not isinstance(data, dict):
            raise ValueError("Invalid form.")
        name, code = data.get("name"), data.get("code", "")
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 60 or not isinstance(code, str):
            raise ValueError("Enter a name of 1 to 60 characters.")
        if data.get("consent") is not True:
            raise ValueError("Permission is required to display photos.")
        return web.json_response(store.visit(name.strip(), code.strip()), status=201)

    async def upload(request):
        token = request.headers.get("X-Visit", "")
        async with slots:
            raw = await request.read()
            if len(raw) > MAX_BYTES:
                raise web.HTTPRequestEntityTooLarge(max_size=MAX_BYTES, actual_size=len(raw))
            jpeg = await asyncio.to_thread(normalize, raw)
            store.upload(token, jpeg)
        return web.json_response({"queued": True}, status=201)

    async def erase(request):
        data = await request.json()
        if not isinstance(data, dict) or not isinstance(data.get("code"), str):
            raise ValueError("Enter your private code.")
        store.erase(data["code"].strip())
        return web.json_response({"erased": True})

    async def state(request):
        return web.json_response(store.current(time.time()))

    async def photo(request):
        row = store.image(int(request.match_info["id"]))
        if not row:
            raise web.HTTPNotFound()
        return web.Response(body=row[0], content_type="image/jpeg")

    async def page(request):
        return web.FileResponse(STATIC / ("display.html" if request.path == "/display" else "index.html"))

    app.router.add_get("/", page)
    app.router.add_get("/display", page)
    app.router.add_static("/static/", STATIC)
    app.router.add_post("/api/visit", visit)
    app.router.add_post("/api/photo", upload)
    app.router.add_post("/api/erase", erase)
    app.router.add_get("/api/current", state)
    app.router.add_get(r"/api/image/{id:\d+}", photo)
    return app


if __name__ == "__main__":
    web.run_app(create_app(os.getenv("PHOTO_DB", "event.sqlite3")),
                host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8000")))
