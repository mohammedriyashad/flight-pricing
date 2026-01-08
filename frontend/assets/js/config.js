// assets/js/config.js

const BASE_URL =
  window.location.hostname === "localhost"
    ? "http://127.0.0.1:8000"
    : "https://skybook-backend-v04m.onrender.com";

console.log("🌐 Backend URL:", BASE_URL);