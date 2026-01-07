document.addEventListener("DOMContentLoaded", () => {
  const b = JSON.parse(localStorage.getItem("lastBooking"));
  if (!b) return;

  receiptDetails.innerHTML = `
    <p><b>PNR:</b> ${b.pnr}</p>
    <p><b>Flight:</b> ${b.flight_id}</p>
    <p><b>Seats:</b> ${b.seats}</p>
    <p><b>Status:</b> ${b.status}</p>
  `;
});