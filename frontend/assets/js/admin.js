document.addEventListener("DOMContentLoaded", async () => {
  const user = JSON.parse(localStorage.getItem("authUser"));
  if (!user || user.role !== "admin") return location.href = "index.html";

  const bookings = await api("/bookings");
  bookings.forEach(b => {
    adminBookings.innerHTML += `
      <tr>
        <td>${b.pnr}</td>
        <td>${b.user_email}</td>
        <td>${b.flight_id}</td>
        <td>${b.seats}</td>
        <td>${b.status}</td>
      </tr>
    `;
  });
});