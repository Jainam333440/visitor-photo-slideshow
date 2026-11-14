# Test results

Executed on 14 November 2026 using Python 3.12.14, aiohttp 3.14.4 and Pillow 13.0.0.

Command: `python -m unittest -v` — **10 tests passed** (0 failures).

| Test | Verified result |
| --- | --- |
| test_consent_and_pages | Pages/assets load; missing consent, blank names, unknown codes and missing request header rejected |
| test_error_responses_are_json_and_not_cached | 403, 404 and 413 errors return JSON and no-store headers |
| test_reject_oversize_and_unauthorized_decode | Oversized bodies rejected; unauthorized uploads never invoke the decoder |
| test_two_visitors_upload_and_delete | Concurrent visitors remain separate; JPEG served; erasure removes active media |
| test_normalization_removes_metadata | Re-encoded JPEG contains no original EXIF metadata |
| test_pixel_and_animation_limits | Over-16-megapixel and animated images rejected |
| test_reject_corrupt_and_wrong_format | Text, GIF and incomplete PNG rejected |
| test_concurrent_uploads_and_limit | Concurrent database writes respect five-upload quota |
| test_return_and_name_collision | Stored data survives a new Store instance; codes identify returning visitors; same names remain separate |
| test_timing_and_erasure | Queue advances at eight seconds; deletion removes photos, queue and credentials |

`node --check static/visit.js` and `node --check static/display.js`: both passed.
The test fixtures are synthetic images and temporary databases, never visitor photos.

## Manual acceptance checks — not yet executed

Browser automation was attempted but blocked by the runtime's Chromium launch restrictions. API tests are not proof of visual behavior. Complete this checklist on your laptop before submitting; record actual outcomes instead of marking untested rows as passed.

| Steps | Expected result | Status |
| --- | --- | --- |
| Open visitor and display tabs; upload a JPEG with consent | Photo appears on idle display within polling/network delay | Pending |
| Wait through multiple queued photos | Each receives an eight-second server slot; queue ends on waiting screen | Pending |
| Return in a new tab with saved code and a new photo | New and previous photos play; no extra replay on subsequent files in same visit | Pending |
| Upload from two browser windows at once | All accepted images play, with no interrupted slot | Pending |
| Erase using private code | Current photo disappears on next poll; old code rejected | Pending |
| Disconnect/reconnect display network | Reconnecting message, then playback resumes | Pending |
| Open on a phone and on a TV/HDMI screen | Form readable; image fits; fullscreen usable | Pending |
| Open final GitHub URL in logged-out/incognito window | README and source accessible with no login | Pending publication |
