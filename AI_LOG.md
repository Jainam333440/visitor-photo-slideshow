# AI development log

Recorded by the AI assistant during this build. The rows paraphrase actual interactions and implementation checks. Only the assignment and review-before-publication instruction came from the student.

| Interaction or check | Result and evidence |
| --- | --- |
| User provided the assignment and requested a preview before publication. | Built a local repository and kept publication pending review. |
| Inspect the runtime before choosing the stack. | The initial Flask import failed. aiohttp, Pillow and SQLite were available; the app uses those, with Python unittest for verification. |
| Translate return visits and simultaneous uploads into a precise playback rule. | Added a private code, explicit per-visit consent, FIFO queue and atomic insertion of the first photo plus earlier photos. See the first two commits. |
| Exercise image validation with a PNG missing its last 12 bytes. | **AI mistake 1.** The first implementation treated successful pixel decoding as sufficient. Pillow returned pixels and the corruption regression failed. Added an end-chunk check and PNG integrity verification before decoding. The same test then passed. |
| Check that an unauthorized request cannot trigger image decoding. | **AI mistake 2.** The initial route called the decoder before looking up the token. A test replaced the decoder with a function that raised if called; the route returned 500. Moved the visit check ahead of decoding and retained the transactional check before insertion. The same request now returns 400. |
| Check queue behavior under concurrency, name collisions, repeat visits and erasure. | The automated suite covers concurrent HTTP visitors and concurrent writes to one visit, saved-photo replay, expiry and deletion. The failing tests and fixes are separate commits so the reviewer can inspect both. |
