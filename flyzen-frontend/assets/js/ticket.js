document.addEventListener("DOMContentLoaded", () => {
  const flight = JSON.parse(localStorage.getItem("flyzen_selected_flight"));
  const passengers = JSON.parse(localStorage.getItem("flyzen_passengers")) || [];

  const pnr = "FZ" + Math.floor(100000 + Math.random() * 900000);

  document.getElementById("pnr").innerText = pnr;
  document.getElementById("from").innerText = flight.origin_code;
  document.getElementById("to").innerText = flight.dest_code;
  document.getElementById("flight").innerText = flight.flight_number;
  document.getElementById("airline").innerText = flight.airline;

  const container = document.getElementById("passengers");

  passengers.forEach((p, i) => {
    container.innerHTML += `
      <div class="flex justify-between bg-bg px-4 py-3 rounded-lg">
        <div>
          <p class="font-semibold">${p.name}</p>
          <p class="text-xs text-gray-400">Passenger ${i + 1}</p>
        </div>
        <div class="text-right">
          <p>${p.gender}</p>
          <p>${p.age} yrs</p>
        </div>
      </div>
    `;
  });
});