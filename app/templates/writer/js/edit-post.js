const blog = JSON.parse(document.getElementById("blogData").textContent);

document.getElementById("titleInput").value = blog.title;

const quill = new Quill("#editor", {
  theme: "snow",
  placeholder: "Write something…",
  modules: {
    toolbar: {
      container: [
        [{ header: [1, 2, 3, false] }],
        ["bold", "italic", "underline", "strike"],
        ["blockquote", "code-block"],
        [{ list: "ordered" }, { list: "bullet" }],
        ["link", "image"],
        ["clean"],
      ],
      handlers: {
        image() {
          const url = prompt("Image URL:");
          if (url) {
            const range = quill.getSelection(true);
            quill.insertEmbed(range.index, "image", url);
            quill.setSelection(range.index + 1);
          }
        },
      },
    },
  },
});

async function uploadImage(dataUrl) {
  const res = await fetch("/api/writer/upload-image", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ data_url: dataUrl }),
  });
  const data = await res.json();
  if (data.status !== "SUCCESS") throw new Error("Upload failed");
  return data.data.url;
}

quill.on("text-change", async (_delta, _old, source) => {
  if (source !== "user") return;

  const ops = quill.getContents().ops;
  const pending = [];
  let index = 0;

  for (const op of ops) {
    if (op.insert?.image?.startsWith?.("data:")) {
      pending.push({ index, dataUrl: op.insert.image });
    }
    index += typeof op.insert === "string" ? op.insert.length : 1;
  }

  if (!pending.length) return;

  const results = await Promise.allSettled(pending.map(p => uploadImage(p.dataUrl)));

  for (let i = pending.length - 1; i >= 0; i--) {
    const result = results[i];
    if (result.status === "fulfilled") {
      quill.updateContents([
        { retain: pending[i].index },
        { delete: 1 },
        { insert: { image: result.value } },
      ], "api");
    } else {
      quill.updateContents([{ retain: pending[i].index }, { delete: 1 }], "api");
    }
  }
});

if (blog.content_delta) {
  try {
    quill.setContents(JSON.parse(blog.content_delta));
  } catch {
    quill.clipboard.dangerouslyPasteHTML(blog.content_html || "");
  }
}

const toggleBtn = document.getElementById("toggleStatusBtn");

function syncToggleBtn(status) {
  toggleBtn.textContent = status === "published" ? "Unpublish" : "Publish";
}

syncToggleBtn(blog.status);

async function patch(fields) {
  const res = await fetch(`/api/writer/update-blog/${blog.id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(fields),
  });
  return res.json();
}

async function save() {
  const title = document.getElementById("titleInput").value.trim();
  if (!title) {
    showStatus("Add a title first.", "error");
    return;
  }

  const delta = JSON.stringify(quill.getContents());
  const html  = document.querySelector(".ql-editor").innerHTML;
  const text  = quill.getText().trim();

  document.getElementById("saveBtn").disabled = true;
  showStatus("Saving…", "");

  const data = await patch({ title, content_delta: delta, content_html: html, content_text: text }).catch(() => null);

  if (data?.status === "SUCCESS") {
    showStatus("Saved.", "success");
  } else {
    showStatus("Something went wrong.", "error");
  }

  document.getElementById("saveBtn").disabled = false;
}

async function toggleStatus() {
  const newStatus = blog.status === "published" ? "draft" : "published";
  toggleBtn.disabled = true;
  showStatus("Updating…", "");

  const data = await patch({ status: newStatus }).catch(() => null);

  if (data?.status === "SUCCESS") {
    blog.status = newStatus;
    syncToggleBtn(newStatus);
    showStatus(newStatus === "published" ? "Published." : "Unpublished.", "success");
  } else {
    showStatus("Something went wrong.", "error");
  }

  toggleBtn.disabled = false;
}

function showStatus(msg, type) {
  const el = document.getElementById("saveStatus");
  el.textContent = msg;
  el.className = "save-status" + (type ? " " + type : "");
}

document.getElementById("saveBtn").addEventListener("click", save);
toggleBtn.addEventListener("click", toggleStatus);

document.getElementById("logoutBtn")?.addEventListener("click", async () => {
  await fetch("/api/writer/logout", { method: "POST" });
  window.location.replace("/writer/login");
});
