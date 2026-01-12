document.addEventListener("DOMContentLoaded", loadFlights);

async function loadFlights() {
  const container = document.getElementById("flightResults");

  if (!container) {
    console.error("flightResults div not found");
    return;
  }

  const search = JSON.parse(localStorage.getItem("flyzen_search"));
  if (!search) {
    container.innerHTML = "<p>No search data found</p>";
    return;
  }

  container.innerHTML = "<p class='text-gray-400'>Loading flights...</p>";

  try {
    const res = await fetch(`${CONFIG.API_BASE_URL}/flights`);
    const flights = await res.json();

    console.log("ALL FLIGHTS:", flights);

    const filtered = flights.filter(f =>
      f.origin_code.toLowerCase() === search.origin.toLowerCase() &&
      f.dest_code.toLowerCase() === search.destination.toLowerCase()
    );

    console.log("FILTERED:", filtered);

    if (filtered.length === 0) {
      container.innerHTML = "<p>No flights found</p>";
      return;
    }

    container.innerHTML = "";

    filtered.forEach(f => {
      const card = document.createElement("div");
      card.className =
        "bg-card p-6 rounded-xl flex justify-between items-center";

      card.innerHTML = `
        <div>
          <h3 class="text-neon font-semibold">
            ${f.origin_code} → ${f.dest_code}
          </h3>
          <p class="text-gray-400">${f.airline} • ${f.flight_number}</p>
          <p class="text-gray-400 text-sm">${f.departure_time}</p>
        </div>

        <div class="text-right">
          <p class="text-xl font-bold">₹ ${f.price}</p>
          <button class="mt-2 bg-neon text-black px-4 py-2 rounded-lg">
            Select
          </button>
        </div>
      `;

      card.querySelector("button").onclick = () => {
        localStorage.setItem("flyzen_selected_flight", JSON.stringify(f));
        window.location.href = "seats.html";
      };

      container.appendChild(card);
    });

  } catch (err) {
    console.error(err);
    container.innerHTML = "<p class='text-red-400'>Error loading flights</p>";
  }
}