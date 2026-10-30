// FTU Labs — K65 member cards, built from /k65/members.json

document.addEventListener("DOMContentLoaded", () => {
  const grid = document.getElementById("k65-grid");
  if (!grid) return;

  const el = (tag, cls, text) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text) e.textContent = text;
    return e;
  };

  fetch("/k65/members.json", { cache: "no-store" })
    .then((r) => (r.ok ? r.json() : []))
    .then((members) => {
      grid.textContent = "";
      const count = document.querySelector(".k65-count");
      if (count) count.textContent = `(${members.length})`;
      if (!members.length) {
        grid.appendChild(el("p", "k65-empty", "Chưa có ai. Bạn là người đầu tiên!"));
        return;
      }
      members.forEach((m) => {
        const card = el("div", "member");
        const avatar = el("div", "member-avatar");
        const img = el("img");
        img.src = `https://github.com/${encodeURIComponent(m.github)}.png?size=96`;
        img.alt = "";
        img.loading = "lazy";
        avatar.appendChild(img);
        card.append(avatar, el("div", "member-name", m.name), el("div", "member-role", m.role));
        if (m.bio) card.appendChild(el("p", "member-bio", m.bio));
        const links = el("div", "member-links");
        const gh = el("a", "", "GitHub");
        gh.href = `https://github.com/${encodeURIComponent(m.github)}`;
        links.appendChild(gh);
        Object.entries(m.links || {}).forEach(([label, url]) => {
          if (!/^https?:\/\//.test(url)) return;
          const a = el("a", "", label);
          a.href = url;
          a.rel = "noopener";
          links.appendChild(a);
        });
        card.appendChild(links);
        grid.appendChild(card);
      });
    })
    .catch(() => {
      grid.textContent = "";
      grid.appendChild(el("p", "k65-empty", "Không tải được danh sách. Thử tải lại trang."));
    });
});
