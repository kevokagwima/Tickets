const btn = document.querySelector(".btn");
const inputs = document.querySelectorAll(".name");

btn.addEventListener("click", () => {
  let allInputsFilled = true;

  inputs.forEach((input) => {
    if (!input.value) {
      allInputsFilled = false;
    }
  });

  if (allInputsFilled) {
    btn.classList.toggle("btn--loading");
    btn.disabled = true;
    btn.form.submit();
  }
});
