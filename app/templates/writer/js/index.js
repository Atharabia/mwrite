async function loadDashboard() {
    let blogs = [];

    try {
        const res = await fetch("/api/writer/get-blogs");

        const data = await res.json();
        if (data.status === "SUCCESS" && Array.isArray(data.data)) {
            blogs = data.data;
        }
    } catch {
        // server unreachable — leave stats at zero
    }

    const totalViews = blogs.reduce((sum, b) => sum + (b.views ?? 0), 0);
    const published = blogs.filter((b) => b.status === "published").length;
    const drafts = blogs.filter((b) => b.status === "draft").length;

    setText("statViews", totalViews.toLocaleString());
    setText("statPosts", blogs.length.toLocaleString());
    setText("statPublished", published.toLocaleString());
    setText("statDrafts", drafts.toLocaleString());

    renderPosts(blogs);
}

function setText(id, val) {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
}

function renderPosts(blogs) {
    const tbody = document.getElementById("postsBody");
    if (!tbody) return;

    if (blogs.length === 0) {
        tbody.innerHTML = `
      <tr>
        <td colspan="4">
          <p class="empty-state">No posts yet — create your first one.</p>
        </td>
      </tr>`;
        return;
    }

    const recent = blogs.slice(0, 10);

    tbody.innerHTML = recent
        .map(
            (b) => `
    <tr class="post-row" data-href="/writer/edit/${b.id}" style="cursor:pointer">
      <td class="post-title-cell" title="${escHtml(b.title)}">${escHtml(b.title)}</td>
      <td><span class="status-badge ${b.status}">${b.status}</span></td>
      <td class="views-cell">${(b.views ?? 0).toLocaleString()}</td>
      <td class="date-cell">${formatDate(b.created_at)}</td>
    </tr>`,
        )
        .join("");

    tbody.querySelectorAll(".post-row").forEach((row) => {
        row.addEventListener("click", () => (window.location.href = row.dataset.href));
    });
}

function escHtml(str) {
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

function formatDate(iso) {
    return new Date(iso).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
    });
}

document.getElementById("newPostBtn")?.addEventListener("click", () => {
    window.location.href = "/writer/new";
});

document.getElementById("logoutBtn")?.addEventListener("click", async () => {
    await fetch("/api/writer/logout", { method: "POST" });
    window.location.replace("/writer/login");
});

loadDashboard();
