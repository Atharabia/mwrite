const PAGE_SIZE = 5;
let currentPage = 1;
let totalPages = 1;


async function loadPage(page) {
    const res = await fetch(`/api/reader/get-blogs?page=${page}&size=${PAGE_SIZE}`);
    const json = await res.json();

    if (json.status !== "SUCCESS") return;

    const { items, total, pages } = json.data;
    totalPages = pages;
    currentPage = page;

    renderPosts(items, total);
    renderPagination();
}

function renderPosts(items, total) {
    const list = document.getElementById("postList");
    const empty = document.getElementById("emptyState");

    if (items.length === 0) {
        list.innerHTML = "";
        empty.style.display = "block";
        document.getElementById("pagination").style.display = "none";
        return;
    }

    empty.style.display = "none";
    document.getElementById("pagination").style.display =
        total > PAGE_SIZE ? "flex" : "none";

    list.innerHTML = items
        .map(
            (b) => `
  <a class="post-item" href="/blog/${b.slug}">
      <p class="post-title">${escHtml(b.title)}</p>
      <p class="post-excerpt">${excerpt(b.content)}</p>
      <div class="post-meta">
        <span>${formatDate(b.created_at)}</span>
      </div>
    </a>`,
        )
        .join("");
}

function renderPagination() {
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    const info = document.getElementById("pageInfo");

    prevBtn.disabled = currentPage <= 1;
    nextBtn.disabled = currentPage >= totalPages;
    info.textContent = `${currentPage} / ${totalPages}`;
}

function excerpt(html) {
    const div = document.createElement("div");
    div.innerHTML = html;
    const text = div.textContent || "";
    return escHtml(text.trim().slice(0, 160)) + (text.length > 160 ? "…" : "");
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

document.getElementById("prevBtn").addEventListener("click", () => {
    if (currentPage > 1) loadPage(currentPage - 1);
});

document.getElementById("nextBtn").addEventListener("click", () => {
    if (currentPage < totalPages) loadPage(currentPage + 1);
});

loadPage(1);
