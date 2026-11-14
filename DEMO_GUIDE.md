# Live demo and explanation

## Three-minute presentation

**0:00–0:30 — Purpose:** “This app lets visitors enter their name and upload photos to a venue slideshow. The display is a separate browser page, which we can open on a TV or computer.”

**0:30–1:10 — First visit:** Open `/` and `/display` side by side. Enter a nickname, check consent and upload one JPEG. Save the return code privately. Explain: “The backend validates the actual image, removes metadata and saves it with a queue entry. The screen polls every half second and assigns an eight-second slot.”

**1:10–1:50 — Return visit:** In a new visitor tab, use the saved code and upload a different image. Explain: “The code identifies the visitor. Names are not unique, so two people named Sam do not share photos. The first accepted upload of a visit queues the new image and the previous images.”

**1:50–2:20 — Safety:** Show consent and the five-file/5-MiB limits. Explain: “Only JPEG and PNG images are accepted. Invalid files do not enter the queue. Visitors can use their code to erase their collection. The operator deletes the event database afterward.”

**2:20–3:00 — Engineering:** Show the passing tests, architecture diagram and commit history. Explain one AI mistake and its failing test from AI_LOG.md. Do not claim you personally wrote a prompt or performed a check that the log attributes to the assistant.

## Questions you should be able to answer

- **Why Python/aiohttp?** Small asynchronous server, simple routes, and browser clients; Pillow handles image decoding.
- **Why SQLite?** One supervised event on one server; transactions keep saved photos, quotas and playback entries consistent.
- **What happens during simultaneous uploads?** At most two images decode at once. Database transactions serialize writes. A completed upload joins the queue; it does not interrupt an existing slide.
- **Does upload completion mean immediate display?** It becomes eligible immediately. An idle screen picks it up on its next poll; a busy screen finishes earlier queue items first. This is documented as an assumption.
- **Why a private code?** Names collide. A random code works on another device without collecting email, phone numbers or face data. Losing it means losing access to that collection.
- **What is stored?** Private nickname, credential hashes, consent timestamp, normalized JPEGs and queue timing. No plain return code is stored in the database.
- **What is not production-ready?** There is no automatic content moderation, event login, global rate limit or automatic retention scheduler. This version targets a supervised trusted-network demo, not an unrestricted internet event.
- **How do you set configuration?** Set shell environment variables shown in .env.example. The app does not automatically load a .env file.
- **What did AI get wrong?** Review the PNG-integrity and pre-decoding authentication failures in the original commits, and the HTTP-error correction in this review.

Practise reading `static/visit.js`, `app.py`, `store.py`, then `static/display.js`. Use your own words; understanding the flow matters more than memorizing this script.
