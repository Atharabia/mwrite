window.MwriteToolbarTooltips = (function () {
  const TITLES = {
    ".ql-header": "Text style",
    ".ql-bold": "Bold",
    ".ql-italic": "Italic",
    ".ql-underline": "Underline",
    ".ql-strike": "Strikethrough",
    ".ql-blockquote": "Quote",
    ".ql-code-block": "Code block",
    ".ql-list[value=ordered]": "Numbered list",
    ".ql-list[value=bullet]": "Bulleted list",
    ".ql-link": "Insert link",
    ".ql-image": "Insert image",
    ".ql-html-embed": "HTML embed",
    ".ql-clean": "Clear formatting",
  };

  function init(quill) {
    const container = quill.getModule("toolbar").container;
    for (const [selector, title] of Object.entries(TITLES)) {
      container.querySelectorAll(selector).forEach((el) => {
        el.setAttribute("title", title);
        el.setAttribute("aria-label", title);
      });
    }
  }

  return { init };
})();
