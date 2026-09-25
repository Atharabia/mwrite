(function () {
  const LANGUAGES = [
    { key: "plain", label: "Plain" },
    { key: "bash", label: "Bash" },
    { key: "c", label: "C" },
    { key: "cpp", label: "C++" },
    { key: "cs", label: "C#" },
    { key: "css", label: "CSS" },
    { key: "diff", label: "Diff" },
    { key: "go", label: "Go" },
    { key: "graphql", label: "GraphQL" },
    { key: "ini", label: "INI/TOML" },
    { key: "java", label: "Java" },
    { key: "javascript", label: "JavaScript" },
    { key: "json", label: "JSON" },
    { key: "kotlin", label: "Kotlin" },
    { key: "less", label: "Less" },
    { key: "lua", label: "Lua" },
    { key: "makefile", label: "Makefile" },
    { key: "markdown", label: "Markdown" },
    { key: "objectivec", label: "Objective-C" },
    { key: "perl", label: "Perl" },
    { key: "php", label: "PHP" },
    { key: "php-template", label: "PHP Template" },
    { key: "python", label: "Python" },
    { key: "python-repl", label: "Python REPL" },
    { key: "r", label: "R" },
    { key: "ruby", label: "Ruby" },
    { key: "rust", label: "Rust" },
    { key: "scss", label: "SCSS" },
    { key: "shell", label: "Shell Session" },
    { key: "sql", label: "SQL" },
    { key: "swift", label: "Swift" },
    { key: "typescript", label: "TypeScript" },
    { key: "vbnet", label: "VB.NET" },
    { key: "wasm", label: "WebAssembly" },
    { key: "xml", label: "HTML/XML" },
    { key: "yaml", label: "YAML" },
  ];

  window.MwriteCodeBlock = {
    LANGUAGES,

    serializeHtml(editorHtml) {
      const wrapper = document.createElement("div");
      wrapper.innerHTML = editorHtml;

      wrapper.querySelectorAll(".ql-code-block-container").forEach((container) => {
        const language = container.getAttribute("data-language") || "plain";

        const lines = Array.from(container.querySelectorAll(".ql-code-block")).map((line) => {
          const clone = line.cloneNode(true);
          clone.querySelectorAll("br").forEach((br) => br.remove());
          return clone.innerHTML;
        });

        const pre = document.createElement("pre");
        pre.className = "hljs";
        pre.setAttribute("data-language", language);

        const code = document.createElement("code");
        code.className = `language-${language}`;
        code.innerHTML = lines.join("\n");

        pre.appendChild(code);
        container.replaceWith(pre);
      });

      return wrapper.innerHTML;
    },
  };
})();
