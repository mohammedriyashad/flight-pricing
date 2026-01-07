

/* =========================
   SIGNUP
========================= */
async function signup() {
  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();

  if (!name || !email || !password) {
    alert("All fields are required");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/users/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password })
    });

    const data = await res.json();

    if (!res.ok) {
      alert(data.detail || "Signup failed");
      return;
    }

    alert("Signup successful! Please login.");
    window.location.href = "login.html";

  } catch (err) {
    console.error(err);
    alert("Server error during signup");
  }
}

/* =========================
   LOGIN
========================= */
async function login() {
  // ✅ CORRECT ELEMENT ACCESS
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();
  const role = document.getElementById("role").value;
  const msg = document.getElementById("msg");

  msg.innerText = "";

  if (!email || !password) {
    msg.innerText = "Email & password required";
    msg.style.color = "red";
    return;
  }

  /* 🔐 ADMIN LOGIN (frontend demo) */
  if (role === "admin") {
    if (email === "admin@skybook.com" && password === "admin123") {
      localStorage.setItem(
        "authUser",
        JSON.stringify({ email, role: "admin" })
      );
      window.location.href = "admin.html";
    } else {
      msg.innerText = "Invalid admin credentials";
      msg.style.color = "red";
    }
    return;
  }

  /* 👤 USER LOGIN (backend) */
  try {
    const res = await fetch(`${API_BASE}/users/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (!res.ok) {
      msg.innerText = data.detail || "Login failed";
      msg.style.color = "red";
      return;
    }

    // ✅ SINGLE SOURCE OF TRUTH
    localStorage.setItem(
      "authUser",
      JSON.stringify({
        email: data.email,
        name: data.name,
        role: "user"
      })
    );

    // ✅ THIS WILL NOW WORK
    window.location.href = "index.html";

  } catch (err) {
    console.error(err);
    msg.innerText = "Server error during login";
    msg.style.color = "red";
  }
}

/* =========================
   LOGOUT
========================= */
function logout() {
  localStorage.removeItem("authUser");
  window.location.href = "login.html";
}