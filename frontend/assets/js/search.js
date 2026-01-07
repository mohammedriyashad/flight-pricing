function normalizeCityName(input) {
  if (!input) return "";

  const map = {
    delhi: "DEL",
    mumbai: "BOM",
    bengaluru: "BLR",
    chennai: "MAA",
    kolkata: "CCU",
    hyderabad: "HYD",
    pune: "PNQ",
    ahmedabad: "AMD",
    jaipur: "JAI",
    goa: "GOI"
  };
  const key = input.trim().toLowerCase();
  return map[key] || input.trim().toUpperCase();
}

async function loadFlights() {
  const from = normalizeCityName(document.getElementById("from").value.trim());
  const to = normalizeCityName(document.getElementById("to").value.trim());

  const container = document.getElementById("flights");
  container.innerHTML = "<p>Loading flights...</p>";

  try {
    let url = "http://127.0.0.1:8000/flights?";

    if (from) url += `origin=${encodeURIComponent(from)}&`;
    if (to) url += `destination=${encodeURIComponent(to)}&`;

    const res = await fetch(url);
    const flights = await res.json();

    if (!res.ok || flights.length === 0) {
      container.innerHTML = "<p>No flights found</p>";
      return;
    }

    container.innerHTML = "";

    flights.forEach(f => {
      const card = document.createElement("div");
      card.className = "flight-card";

      card.innerHTML = `
        <div class="flight-header">
          <h3>${f.origin_city} (${f.origin_code}) → ${f.dest_city} (${f.dest_code})</h3>
          <span>${f.airline} · ${f.flight_number}</span>
        </div>

        <div class="flight-info">
          🕒 ${f.departure_time}<br/>
          💺 Seats Left: ${f.available_seats}
        </div>

        <div class="flight-footer">
          <strong>₹ ${f.price}</strong>
          <button class="book-btn">Book</button>
        </div>
      `;

      card.querySelector("button").onclick = () => {
        localStorage.setItem("selectedFlightData", JSON.stringify(f));
        window.location.href = "booking.html";
      };

      container.appendChild(card);
    });

  } catch (err) {
    console.error(err);
    container.innerHTML = "<p>Error loading flights</p>";
  }
}