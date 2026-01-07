document.addEventListener("DOMContentLoaded", () => {
  const history = JSON.parse(localStorage.getItem("bookingHistory")) || [];
  historyBody.innerHTML = "";

  history.forEach((b, i) => {
    historyBody.innerHTML += `
      <tr>
        <td>${b.pnr}</td>
        <td>${b.flight_id}</td>
        <td>${b.seats}</td>
        <td>₹ ${b.amount}</td>
        <td>${b.status}</td>
        <td><button onclick="view(${i})">View</button></td>
      </tr>
    `;
  });
});

function view(i) {
  const history = JSON.parse(localStorage.getItem("bookingHistory"));
  localStorage.setItem("lastBooking", JSON.stringify(history[i]));
  location.href = "receipt.html";
}