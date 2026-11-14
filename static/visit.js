const el = id => document.getElementById(id);
async function post(path, body, extra = {}) {
  const res = await fetch("/api/" + path, {method:"POST", body,
    headers: {"X-Guestbook":"1", "Content-Type":"application/json", ...extra}});
  if (res.status === 413) throw Error("A file exceeds 5 MiB.");
  const data = await res.json();
  if (!res.ok) throw Error(data.error || "Request failed.");
  return data;
}
el("share").onsubmit = async event => {
  event.preventDefault();
  const files = Array.from(el("photos").files);
  const button = event.target.querySelector("button");
  if (files.length > 5 || files.some(f => f.size > 5 * 1024 * 1024)) {
    el("message").textContent = "Choose up to five files, each at most 5 MiB.";
    return;
  }
  button.disabled = true;
  let sent = 0;
  try {
    const visit = await post("visit", JSON.stringify({name:el("name").value, code:el("code").value, consent:el("agree").checked}));
    el("secret").textContent = visit.code;
    el("receipt").hidden = false;
    el("code").value = visit.code;
    for (const file of files) {
      el("message").textContent = "Uploading " + file.name;
      await post("photo", file, {"X-Visit":visit.token, "Content-Type":"application/octet-stream"});
      sent++;
    }
    el("message").textContent = sent + " photo(s) queued for the venue screen.";
    el("photos").value = "";
  } catch (err) {
    el("message").textContent = sent + " uploaded. " + err.message + " Select only remaining files to retry.";
  } finally {
    el("agree").checked = false;
    button.disabled = false;
  }
};
el("remove").onsubmit = async event => {
  event.preventDefault();
  if (!confirm("Permanently erase all photos associated with this code?")) return;
  try {
    await post("erase", JSON.stringify({code:el("removeCode").value}));
    el("share").reset(); event.target.reset(); el("receipt").hidden = true; el("secret").textContent = "";
    el("message").textContent = "Collection erased and removed from the slideshow.";
  } catch(err) { el("message").textContent = err.message; }
};
