let passengers = [];

function addPassenger() {
  const name = document.getElementById("fullName").value.trim();
  const age = document.getElementById("age").value;
  const gender = document.getElementById("gender").value;

  if (!name || !age) {
    alert("Enter passenger name and age");
    return;
  }

  passengers.push({ name, age, gender });
  renderPassengers();

  document.getElementById("fullName").value = "";
  document.getElementById("age").value = "";
}

function renderPassengers() {
  const list = document.getElementById("passengerList");
  list.innerHTML = "";

  passengers.forEach((p, i) => {
    list.innerHTML += `
      <div class="flex justify-between bg-bg px-4 py-2 rounded">
        <span>${i + 1}. ${p.name} (${p.gender}, ${p.age})</span>
        <button onclick="removePassenger(${i})" class="text-red-400">
          Remove
        </button>
      </div>
    `;
  });
}

function removePassenger(index) {
  passengers.splice(index, 1);
  renderPassengers();
}

function proceedToPayment() {
  if (passengers.length === 0) {
    alert("Add at least one passenger");
    return;
  }

  localStorage.setItem("flyzen_passengers", JSON.stringify(passengers));
  window.location.href = "payment.html";
}