(function () {
  const BlockEmbed = Quill.import("blots/block/embed");

  class HtmlEmbedBlot extends BlockEmbed {
    static create(value) {
      const node = super.create();
      node.setAttribute("contenteditable", "false");
      node.dataset.html = encodeURIComponent(value?.html || "");

      const label = document.createElement("div");
      label.className = "html-embed-label";
      label.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>
        </svg>
        <span>HTML embed</span>
      `;

      const actions = document.createElement("div");
      actions.className = "html-embed-actions";
      actions.innerHTML = `
        <button type="button" class="html-embed-edit">Edit</button>
        <button type="button" class="html-embed-remove">Remove</button>
      `;

      node.append(label, actions);
      return node;
    }

    static value(node) {
      return { html: decodeURIComponent(node.dataset.html || "") };
    }
  }

  HtmlEmbedBlot.blotName = "html-embed";
  HtmlEmbedBlot.tagName = "div";
  HtmlEmbedBlot.className = "html-embed-block";

  Quill.register(HtmlEmbedBlot);

  const icons = Quill.import("ui/icons");
  icons["html-embed"] = `
    <svg viewBox="0 0 24 24">
      <polyline class="ql-stroke" points="16 18 22 12 16 6"/><polyline class="ql-stroke" points="8 6 2 12 8 18"/>
    </svg>
  `;

  function buildModal() {
    const overlay = document.createElement("div");
    overlay.className = "html-embed-modal-overlay";
    overlay.innerHTML = `
      <div class="html-embed-modal">
        <h2>HTML embed</h2>
        <textarea class="html-embed-textarea" spellcheck="false" placeholder="&lt;div id=&quot;chart&quot;&gt;&lt;/div&gt;
&lt;style&gt; ... &lt;/style&gt;
&lt;script&gt; ... &lt;/script&gt;"></textarea>
        <div class="html-embed-modal-actions">
          <button type="button" class="btn-ghost html-embed-cancel">Cancel</button>
          <button type="button" class="btn-primary html-embed-save">Insert</button>
        </div>
      </div>
    `;
    document.body.appendChild(overlay);
    return overlay;
  }

  window.MwriteHtmlEmbed = {
    init(quill) {
      const overlay = buildModal();
      const textarea = overlay.querySelector(".html-embed-textarea");
      const saveBtn = overlay.querySelector(".html-embed-save");
      const cancelBtn = overlay.querySelector(".html-embed-cancel");

      let editIndex = null;

      function open(initialHtml, index) {
        textarea.value = initialHtml || "";
        editIndex = index ?? null;
        overlay.classList.add("open");
        textarea.focus();
      }

      function close() {
        overlay.classList.remove("open");
        editIndex = null;
      }

      saveBtn.addEventListener("click", () => {
        const html = textarea.value;
        if (!html.trim()) {
          close();
          return;
        }

        if (editIndex !== null) {
          quill.deleteText(editIndex, 1, "user");
          quill.insertEmbed(editIndex, "html-embed", { html }, "user");
          quill.setSelection(editIndex + 1, 0, "user");
        } else {
          const range = quill.getSelection(true) || { index: quill.getLength() };
          quill.insertEmbed(range.index, "html-embed", { html }, "user");
          quill.setSelection(range.index + 1, 0, "user");
        }
        close();
      });

      cancelBtn.addEventListener("click", close);
      overlay.addEventListener("click", (e) => {
        if (e.target === overlay) close();
      });

      quill.root.addEventListener("click", (e) => {
        const editBtn = e.target.closest(".html-embed-edit");
        const removeBtn = e.target.closest(".html-embed-remove");
        if (!editBtn && !removeBtn) return;

        const node = e.target.closest(".html-embed-block");
        const blot = Quill.find(node);
        if (!blot) return;
        const index = quill.getIndex(blot);

        if (editBtn) {
          open(decodeURIComponent(node.dataset.html || ""), index);
        } else {
          quill.deleteText(index, 1, "user");
        }
      });

      return {
        openForInsert() {
          open("", null);
        },
      };
    },

    serializeHtml(editorHtml) {
      const wrapper = document.createElement("div");
      wrapper.innerHTML = editorHtml;
      wrapper.querySelectorAll(".html-embed-block").forEach((node) => {
        const src = decodeURIComponent(node.dataset.html || "");
        const iframe = document.createElement("iframe");
        iframe.className = "post-html-embed";
        iframe.setAttribute("sandbox", "allow-scripts");
        iframe.setAttribute("loading", "lazy");
        iframe.setAttribute("frameborder", "0");
        iframe.setAttribute("srcdoc", src);
        node.replaceWith(iframe);
      });
      return wrapper.innerHTML;
    },
  };
})();
