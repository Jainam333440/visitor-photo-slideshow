# AI development log

Recorded by the AI assistant during this build. The rows paraphrase actual interactions and implementation checks. Student requests supplied the assignment, review-before-publication preference, and the later submission requirements. Other entries are assistant-led implementation and review checks, not invented student prompts.

| Interaction or check | Result and evidence |
| --- | --- |
| User provided the assignment and requested a preview before publication. | Built a local repository and kept publication pending review. |
| Inspect the runtime before choosing the stack. | The initial Flask import failed. aiohttp, Pillow and SQLite were available; the app uses those, with Python unittest for verification. |
| Translate return visits and simultaneous uploads into a precise playback rule. | Added a private code, explicit per-visit consent, FIFO queue and atomic insertion of the first photo plus earlier photos. See the first two commits. |
| Exercise image validation with a PNG missing its last 12 bytes. | **AI mistake 1.** The first implementation treated successful pixel decoding as sufficient. Pillow returned pixels and the corruption regression failed. Added an end-chunk check and PNG integrity verification before decoding. The same test then passed. |
| Check that an unauthorized request cannot trigger image decoding. | **AI mistake 2.** The initial route called the decoder before looking up the token. A test replaced the decoder with a function that raised if called; the route returned 500. Moved the visit check ahead of decoding and retained the transactional check before insertion. The same request now returns 400. |
| Check queue behavior under concurrency, name collisions, repeat visits and erasure. | The automated suite covers concurrent HTTP visitors and concurrent writes to one visit, saved-photo replay, expiry and deletion. The failing tests and fixes are separate commits so the reviewer can inspect both. |

| User supplied the complete repository and submission rules on 14 November 2026. | Recovered the original Git bundle and reran all nine existing tests successfully. Preserved the original six commits and their authorship. |
| Review rejected HTTP requests for consistent errors and privacy headers. | **AI mistake 3, found in this review:** raised HTTP exceptions bypassed the common response headers and returned plain text, although the client expects JSON. Added a regression test; it failed with `text/plain != application/json`. Moved the header check inside the try block and converted HTTP exceptions into JSON before setting headers. All ten tests passed. Commits `1492c5d` and `8c3c4ea` record reproduction and fix. |
| Prepare evidence and a truthful handoff for submission. | Added test results, a live-demo guide and Git publishing instructions. JavaScript syntax checks passed. Browser automation could not launch in this runtime, so visual and physical-TV checks remain explicitly pending. No public repository or deployment is claimed. |
