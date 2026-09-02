// Project 0 page script — scoped to this page only.
// Small touch: reset a polaroid's tilt while its caption is being edited,
// so typing a real caption in isn't fighting the scrapbook rotation.
(function () {
  "use strict";

  document.querySelectorAll(".polaroid input, .gif-slot input").forEach(function (input) {
    var card = input.closest("figure");
    if (!card) return;
    input.addEventListener("focus", function () { card.style.transform = "rotate(0deg)"; });
    input.addEventListener("blur", function () { card.style.transform = ""; });
  });
})();
