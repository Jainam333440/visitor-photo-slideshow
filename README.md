# Guestbook · Visitor Photo Slideshow

Visitors enter a name, give permission and upload photos from a browser. A separate screen plays accepted photos for eight seconds each. A private return code lets visitors replay earlier photos across devices or erase their collection. Names and return codes stay off the venue display.

## Run on Windows

Install Python 3.12, then open PowerShell in the extracted project folder (the folder containing app.py). These commands use the virtual environment directly.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

On macOS or Linux, run:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

Open **http://127.0.0.1:8000/** for visitors. Select **Open display** to open **http://127.0.0.1:8000/display** in another tab. Put that tab on the TV via HDMI or use a second browser window. The display must stay open and in the foreground for normal playback.

For separate devices, connect to the same trusted Wi-Fi. On Windows, set `$env:HOST="0.0.0.0"` before starting the server and use `ipconfig` to find the laptop's Wi-Fi IPv4 address. Open `http://<laptop-IP>:8000/` on a phone and `http://<laptop-IP>:8000/display` on the TV. Allow the server through the private-network firewall if needed. On Linux/macOS, prefix the launch command with `HOST=0.0.0.0`.

## Three-minute live demo

1. Open the visitor and display windows side by side. Upload one JPEG as “Sam” after checking the consent box. Copy the private code. The waiting screen picks up the photo within one poll plus transfer time.
2. Open a fresh visitor tab, enter “Sam” and the saved code, then upload a different photo. Watch the new image followed by the earlier image. Each gets an eight-second slot.
3. Use a fresh tab with the same name and a blank code. Upload a third image. This visitor gets a separate collection.
4. Under **Privacy and photo removal**, enter the original code and confirm erasure. The other visitor's collection remains available.

## Stack and verification

Python 3.12, aiohttp, Pillow, SQLite, HTML, CSS and JavaScript. Run the ten automated tests with `.\.venv\Scripts\python.exe -m unittest -v` on Windows or `.venv/bin/python -m unittest -v` on Linux/macOS. All ten passed during the submission review on 14 November 2026. The tests use temporary databases and synthetic images. A physical smart TV and the venue Wi-Fi still need an on-site demo check.

See [ASSUMPTIONS.md](ASSUMPTIONS.md), [ARCHITECTURE.md](ARCHITECTURE.md) and [AI_LOG.md](AI_LOG.md) for the agreed behavior, diagram and actual debugging record. Read the code in this order: static/visit.js (form), app.py (requests), store.py (data), static/display.js (screen).

## Event data and configuration

The default database is event.sqlite3 in the working folder. Stop the server and delete the event database and any associated SQLite sidecar files after the event. Keep the event folder on a private device and control any backups. The repository excludes event databases, local environment settings and virtual environments. The .env.example lists optional environment variables. Set them in your shell; the app reads the environment directly.

This version runs locally; no deployed website link is available. A live deployment is optional under the assignment. See [SUBMISSION.md](SUBMISSION.md) to publish the source repository while preserving its real commit history. See [TEST_RESULTS.md](TEST_RESULTS.md) for executed checks and remaining manual checks, and [DEMO_GUIDE.md](DEMO_GUIDE.md) for a short explanation you can practise.
