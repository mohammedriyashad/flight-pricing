// ================= CONFIG =================
const API = CONFIG.API_BASE_URL;

// ================= HELPERS =================
function $(id) {
  return document.getElementById(id);
}

function show(el) {
  el.classList.remove("hidden");
}

function hide(el) {
  el.classList.add("hidden");
}

// ================= SIGNUP FLOW =================

// STEP 1: Send OTP (Signup)
async function sendSignupOTP() {
  const email = $("email")?.value.trim();
  const password = $("password")?.value.trim();

  if (!email || !password) {
    alert("Email and password required");
    return;
  }

  try {
    const res = await fetch(`${API}/users/send-otp?email=${encodeURIComponent(email)}`, {
      method: "POST"
    });

    if (!res.ok) throw new Error("OTP send failed");

    show($("otpSection"));
    alert("OTP sent successfully (check backend console)");

  } catch (err) {
    alert("Failed to send OTP");
  }
}

// STEP 2: Verify OTP + Create Account
async function verifySignupOTP() {
  const email = $("email").value.trim();
  const password = $("password").value.trim();
  const otp = $("otp").value.trim();

  if (!otp) {
    alert("Enter OTP");
    return;
  }

  try {
    // Verify OTP
    const verify = await fetch(
      `${API}/users/verify-otp?email=${encodeURIComponent(email)}&otp=${otp}`,
      { method: "POST" }
    );

    const verifyData = await verify.json();
    if (!verify.ok || verifyData.error) {
      alert("OTP verification failed");
      return;
    }

    // Create user
    const signup = await fetch(`${API}/users/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: email.split("@")[0],
        email,
        password
      })
    });

    if (!signup.ok) {
      alert("User already exists");
      return;
    }

    localStorage.setItem("flyzen_user", JSON.stringify({ email }));
    window.location.href = "index.html";

  } catch (err) {
    alert("Signup failed");
  }
}

// ================= LOGIN FLOW =================

// STEP 1: Send OTP (Login)
async function sendLoginOTP() {
  const email = $("email")?.value.trim();

  if (!email) {
    alert("Email required");
    return;
  }

  try {
    const res = await fetch(`${API}/users/send-otp?email=${encodeURIComponent(email)}`, {
      method: "POST"
    });

    if (!res.ok) throw new Error();

    show($("otpSection"));
    alert("OTP sent successfully, please check your email");

  } catch {
    alert("Failed to send OTP");
  }
}

// STEP 2: Verify OTP (Login)
async function verifyLoginOTP() {
  const email = $("email").value.trim();
  const otp = $("otp").value.trim();

  if (!otp) {
    alert("Enter OTP");
    return;
  }

  try {
    const res = await fetch(
      `${API}/users/verify-otp?email=${encodeURIComponent(email)}&otp=${otp}`,
      { method: "POST" }
    );

    const data = await res.json();
    if (!res.ok || data.error) {
      alert("OTP verification failed");
      return;
    }

    localStorage.setItem("flyzen_user", JSON.stringify({ email }));
    window.location.href = "index.html";

  } catch {
    alert("Login failed");
  }
}