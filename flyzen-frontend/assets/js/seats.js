// ==============================
// FlyZen Seat Selection
// ==============================

// DOM
const businessContainer = document.getElementById("businessSeats");
const economyContainer = document.getElementById("economySeats");

const baseFareEl = document.getElementById("baseFare");
const seatFareEl = document.getElementById("seatFare");
const totalFareEl = document.getElementById("totalFare");

// Data
const flight = JSON.parse(localStorage.getItem("flyzen_selected_flight"));
const WINDOW_SURGE = 500;
const BUSINESS_SURGE = 2000;

let selectedSeat = null;
let seatSurcharge = 0;

// Validation
if (!flight) {
  alert("No flight selected");
  window.location.href = "index.html";
}

// Initial prices
baseFareEl.textContent = `₹ ${flight.price}`;
seatFareEl.textContent = "₹ 0";
updateTotal();

// Layout config
const cols = ["A", "B", "C", "AISLE", "D", "E", "F"];
const businessRows = [1, 2];
const economyRows = [3,4,5,6,7,8,9,10];

// Create rows
function createRow(rowNum, isBusiness) {
  const row = document.createElement("div");
  row.className = "flex justify-center gap-2 mb-3";

  cols.forEach(col => {
    if (col === "AISLE") {
      const aisle = document.createElement("div");
      aisle.className = "w-6";
      row.appendChild(aisle);
      return;
    }

    const seatId = `${rowNum}${col}`;
    const isWindow = col === "A" || col === "F";

    let surcharge = 0;
    if (isWindow) surcharge += WINDOW_SURGE;
    if (isBusiness) surcharge += BUSINESS_SURGE;

    const seat = document.createElement("button");
    seat.textContent = seatId;

    seat.className = `
      h-10 w-10 rounded-md text-xs font-semibold
      ${isBusiness ? "bg-indigo-600" : "bg-seat"}
      ${isWindow ? "border border-window" : ""}
      hover:bg-neon hover:text-black
      transition
    `;

    seat.onclick = () => selectSeat(seat, seatId, surcharge);
    row.appendChild(seat);
  });

  return row;
}

// Generate seats
businessRows.forEach(r => businessContainer.appendChild(createRow(r, true)));
economyRows.forEach(r => economyContainer.appendChild(createRow(r, false)));

// Seat select
function selectSeat(btn, seatId, surcharge) {
  document.querySelectorAll("button").forEach(b => {
    b.classList.remove("bg-neon", "text-black");
  });

  btn.classList.add("bg-neon", "text-black");

  selectedSeat = seatId;
  seatSurcharge = surcharge;

  seatFareEl.textContent = `₹ ${seatSurcharge}`;
  updateTotal();
}

// Total
function updateTotal() {
  totalFareEl.textContent = `₹ ${flight.price + seatSurcharge}`;
}

// Continue
function proceedToBooking() {
  if (!selectedSeat) {
    alert("Please select a seat");
    return;
  }

  localStorage.setItem(
    "flyzen_seat",
    JSON.stringify({ seat: selectedSeat, surcharge: seatSurcharge })
  );

  window.location.href = "passenger.html";

}