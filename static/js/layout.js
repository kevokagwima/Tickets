const account = document.querySelector(".account-info");
const bookings = document.querySelector(".bookings");

account.addEventListener("click", () => {
  bookings.classList.toggle("show-bookings");
});
