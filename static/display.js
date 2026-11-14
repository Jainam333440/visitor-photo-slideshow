const picture = document.getElementById("picture");
const statusLine = document.getElementById("status");
let current = null;
async function refresh() {
  try {
    const response = await fetch("/api/current", {cache:"no-store"});
    if (!response.ok) throw Error("Offline");
    const {slide} = await response.json();
    if (slide !== current || slide === null) {
      picture.hidden = true;
      if (slide !== null) {
        picture.src = "/api/image/" + slide;
        await picture.decode();
        picture.hidden = false;
      }
      current = slide;
    }
    statusLine.textContent = "Share a photo from the visitor page to see it here.";
  } catch {
    current = null;
    picture.hidden = true;
    statusLine.textContent = "Reconnecting to the venue server…";
  } finally {
    setTimeout(refresh, 500);
  }
}
document.getElementById("full").onclick = async () => {
  try { await document.documentElement.requestFullscreen(); }
  catch { statusLine.textContent = "Use the browser’s full-screen control."; }
};
refresh();
