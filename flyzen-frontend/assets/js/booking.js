const user = JSON.parse(localStorage.getItem("flyzen_user"));
const flight = JSON.parse(localStorage.getItem("flyzen_selected_flight"));
const seat = JSON.parse(localStorage.getItem("flyzen_seat"));

// LOGIN GATE
if (!user) {
  alert("Please login to continue booking");
  window.location.href = "login.html";
}

if (!flight || !seat) {
  alert("Booking data missing");
  window.location.href = "index.html";
}

// Autofill email
document.getElementById("email").value = user.email;

function proceedToPayment() {
  const bookingData = {
    flight_id: flight.flight_id,
    email: user.email,
    name: document.getElementById("name").value,
    age: document.getElementById("age").value,
    gender: document.getElementById("gender").value,
    seat: seat.seat,
    price: flight.price + seat.surcharge
  };

  if (!bookingData.name || !bookingData.age) {
    alert("Please fill all fields");
    return;
  }

  localStorage.setItem("flyzen_booking", JSON.stringify(bookingData));
  window.location.href = "payment.html";
}