document.addEventListener("DOMContentLoaded", () => {
  const totalEl = document.getElementById("totalAmount");

  const flight = JSON.parse(localStorage.getItem("flyzen_selected_flight"));
  const seat = JSON.parse(localStorage.getItem("flyzen_seat"));
  const passengers = JSON.parse(localStorage.getItem("flyzen_passengers")) || [];

  const total =
    (flight?.price || 0) +
    (seat?.surcharge || 0) +
    passengers.length * 500;

  totalEl.textContent = `₹ ${total}`;
});

function payNow() {
  const btn = document.getElementById("payBtn");
  btn.innerText = "Processing...";
  btn.disabled = true;

  setTimeout(() => {
    const ticket = generateTicket();
    const booking = {
      pnr: ticket.pnr,
      origin: ticket.from,
      destination: ticket.to,
      flight_number: ticket.flight,
      airline: ticket.airline,
      seat: ticket.seat,
      passengers: ticket.passengers
    };
localStorage.setItem("flyzen_booking", JSON.stringify(booking));

    window.location.href = "ticket.html";
  }, 2000);
}

function generateTicket() {
  const flight = JSON.parse(localStorage.getItem("flyzen_selected_flight"));
  const seat = JSON.parse(localStorage.getItem("flyzen_seat"));
  const passengers = JSON.parse(localStorage.getItem("flyzen_passengers"));

  return {
    airline: flight.airline,
    flightNumber: flight.flight_number,
    from: flight.origin_code,
    to: flight.dest_code,
    departure: flight.departure_time,
    seat: seat.seat,
    passengers,
    pnr: "FZ" + Math.random().toString(36).substring(2, 8).toUpperCase(),
    bookedAt: new Date().toLocaleString(),
  };
}