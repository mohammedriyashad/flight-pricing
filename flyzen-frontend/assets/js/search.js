function searchFlights() {
  const origin = document.getElementById("from").value.trim();
  const destination = document.getElementById("to").value.trim();

  if (!origin || !destination) {
    alert("Please enter both origin and destination");
    return;
  }

  // Save search params
  localStorage.setItem("flyzen_search", JSON.stringify({
    origin,
    destination
  }));

  // Redirect to results page
  window.location.href = "flights.html";
}