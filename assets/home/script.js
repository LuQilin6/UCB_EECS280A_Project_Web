// Home page background — animated perspective grid + drifting "data" nodes.
// Scoped to index.html only; not shared with /projects/* pages.
(function () {
  "use strict";

  var canvas = document.getElementById("grid-bg");
  if (!canvas) return;
  var ctx = canvas.getContext("2d");

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var width, height, dpr;
  var nodes = [];
  var NODE_COUNT = 46;

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = width + "px";
    canvas.style.height = height + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function makeNodes() {
    nodes = [];
    for (var i = 0; i < NODE_COUNT; i++) {
      nodes.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.18,
        vy: (Math.random() - 0.5) * 0.18,
        r: 1 + Math.random() * 1.6
      });
    }
  }

  function step() {
    ctx.clearRect(0, 0, width, height);

    // faint base grid
    var gap = 42;
    ctx.strokeStyle = "rgba(75, 247, 233, 0.045)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (var x = 0; x < width; x += gap) {
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
    }
    for (var y = 0; y < height; y += gap) {
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
    }
    ctx.stroke();

    // radial vignette glow near top
    var grad = ctx.createRadialGradient(width * 0.5, -60, 40, width * 0.5, -60, width * 0.7);
    grad.addColorStop(0, "rgba(75, 247, 233, 0.08)");
    grad.addColorStop(1, "rgba(75, 247, 233, 0)");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, width, height);

    // nodes + connecting lines
    for (var i = 0; i < nodes.length; i++) {
      var n = nodes[i];
      if (!reduceMotion) {
        n.x += n.vx;
        n.y += n.vy;
        if (n.x < 0 || n.x > width) n.vx *= -1;
        if (n.y < 0 || n.y > height) n.vy *= -1;
      }
      for (var j = i + 1; j < nodes.length; j++) {
        var m = nodes[j];
        var dx = n.x - m.x, dy = n.y - m.y;
        var dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 130) {
          ctx.strokeStyle = "rgba(89, 255, 143, " + (0.08 * (1 - dist / 130)) + ")";
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(n.x, n.y);
          ctx.lineTo(m.x, m.y);
          ctx.stroke();
        }
      }
    }
    for (var k = 0; k < nodes.length; k++) {
      var p = nodes[k];
      ctx.fillStyle = "rgba(75, 247, 233, 0.55)";
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fill();
    }

    if (!reduceMotion) requestAnimationFrame(step);
  }

  window.addEventListener("resize", function () {
    resize();
    makeNodes();
    if (reduceMotion) step();
  });

  resize();
  makeNodes();
  step();
})();
