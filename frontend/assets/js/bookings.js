window.confirmBooking = async function () {
  const user = JSON.parse(localStorage.getItem("authUser"));
  const flight = JSON.parse(localStorage.getItem("selectedFlightData"));
  const seats = Number(document.getElementById("seats").value);

  if (!user || !flight || seats <= 0) {
    alert("Invalid booking data");
    return;
  }

  document.getElementById("loader").style.display = "flex";

  try {
    const res = await fetch("http://127.0.0.1:8000/book", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_email: user.email,
        flight_id: flight.flight_id,
        seats: seats
      })
    });

    const data = await res.json();
    document.getElementById("loader").style.display = "none";

    if (!res.ok) {
      alert(data.detail || "Booking failed");
      return;
    }

    const bookingRecord = {
      pnr: data.pnr || ("SB" + Math.random().toString(36).substring(2, 8).toUpperCase()),
      flight_id: flight.flight_id,
      seats: seats,
      amount: flight.price * seats,
      status: "CONFIRMED"
    };

    localStorage.setItem("lastBooking", JSON.stringify(bookingRecord));

    const history = JSON.parse(localStorage.getItem("bookingHistory")) || [];
    history.push(bookingRecord);
    localStorage.setItem("bookingHistory", JSON.stringify(history));

    // ✅ NAVIGATION (THIS WAS NOT HAPPENING BEFORE)
    window.location.href = "receipt.html";

  } catch (err) {
    document.getElementById("loader").style.display = "none";
    console.error(err);
    alert("Server error");
  }
};