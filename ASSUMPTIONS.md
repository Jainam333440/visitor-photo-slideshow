# Decisions for the venue demo

| Gap in the brief | Decision and reason |
| --- | --- |
| Venue and scale | One supervised event, one server, one active display, and a small number of simultaneous visitors on a trusted network. Guests can upload from their phones. |
| Identity | Ask for a name or nickname and issue a random private return code. Names can repeat. A code works across devices. Losing it means starting a new collection or asking the operator to erase the event database. |
| Public display | Only the image is displayed. The visitor must confirm permission from everyone pictured before each batch. Returning visitors explicitly consent to replay of their saved photos. |
| Timing | Each photo gets eight seconds. An idle screen checks every half second. A completed upload joins the back of the queue. Interrupting the current photo would shorten someone else's turn. |
| Previous visits | When the first valid file of a visit arrives, enqueue it, then all previously saved photos once in original order. Later valid files in that visit join as they complete. Submitting the form again starts a new visit. |
| Idle behavior | Show a waiting screen after the queue runs out. This limits unnecessary repeat exposure. |
| Retention | Keep photos for the event so visitors can return. Visitors can erase their collection and queued entries using their code. The operator stops the app and deletes the event database at event end. No automatic expiry. |
| Formats and limits | Accept static JPEG and PNG only, up to 5 MiB and 16 million pixels each. Normalize orientation, resize to 1920 pixels on the longest edge and remove metadata. Allow up to five photos per visit and 30 stored per visitor to bound work. |
| Client and network | Use a modern browser with JavaScript. Keep codes off the display and out of URLs. On a shared visitor device, reload after use. An operator supervises content. Use HTTPS outside a trusted demo network. |
