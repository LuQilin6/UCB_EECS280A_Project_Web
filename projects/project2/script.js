// Project 2 page script — scoped to this page only.
// 1) Click any result image to open it full size (Esc or click to close).
// 2) If an image file is missing, show a dashed placeholder instead of a broken icon.
(function () {
  "use strict";

  var box = document.getElementById("lightbox");
  var boxImg = box.querySelector("img");
  var boxCap = box.querySelector("p");

  function close() {
    box.classList.remove("open");
    boxImg.removeAttribute("src");
  }

  document.querySelectorAll(".shot img").forEach(function (img) {
    var shot = img.closest(".shot");

    function markMissing() { shot.classList.add("missing"); }
    img.addEventListener("error", markMissing);
    if (img.complete && img.naturalWidth === 0 && img.getAttribute("src")) markMissing();

    img.addEventListener("click", function () {
      var cap = shot.querySelector("figcaption");
      boxImg.src = img.currentSrc || img.src;
      boxImg.alt = img.alt;
      boxCap.textContent = cap ? cap.textContent : img.alt;
      box.classList.add("open");
    });
  });

  box.addEventListener("click", close);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") close();
  });
})();
