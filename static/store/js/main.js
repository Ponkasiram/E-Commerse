// Small client-side enhancement: confirm before submitting a product removal.
document.querySelectorAll('form[action*="/cart/remove/"]').forEach((form) => {
  form.addEventListener("submit", (event) => {
    if (!window.confirm("Remove this item from your cart?")) event.preventDefault();
  });
});
