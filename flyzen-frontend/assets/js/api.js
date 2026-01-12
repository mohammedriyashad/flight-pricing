// assets/js/api.js
async function api(endpoint, method = "GET", body = null) {
  const options = {
    method,
    headers: { "Content-Type": "application/json" }
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const res = await fetch(`${CONFIG.API_BASE_URL}${endpoint}`, options);

  if (!res.ok) {
    const err = await res.text();
    throw new Error(err);
  }

  return res.json();
}