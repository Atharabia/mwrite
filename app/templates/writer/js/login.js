const form = document.getElementById("loginForm");
const errorMsg = document.getElementById("errorMsg");
const submitBtn = document.getElementById("submitBtn");

function showError(msg) {
  errorMsg.textContent = msg;
  errorMsg.classList.add("visible");
}

function clearError() {
  errorMsg.classList.remove("visible");
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  clearError();

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  if (!email || !password) {
    showError("Please fill in all fields.");
    return;
  }

  submitBtn.disabled = true;
  submitBtn.textContent = "Signing in…";

  try {
    const res = await fetch("/api/writer/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json();

    if (data.status === "SUCCESS") {
      window.location.href = "/writer";
    } else {
      showError("Invalid email or password.");
    }
  } catch {
    showError("Something went wrong. Please try again.");
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Sign in";
  }
});
