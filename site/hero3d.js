/* Live 3D hero — a small SKYLINE-flavored scene proving the store's games
   run right in the browser. Lazy-loaded after page load; hides itself if
   WebGL is unavailable or the visitor prefers reduced motion. */
(function () {
  var host = document.getElementById("hero3d-card");
  if (!host) return;
  if (window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches) {
    host.style.display = "none";
    return;
  }
  var probe = document.createElement("canvas");
  var gl = probe.getContext("webgl") || probe.getContext("experimental-webgl");
  if (!gl) { host.style.display = "none"; return; }

  function start() {
    var s = document.createElement("script");
    s.src = "play5/three.min.js";
    s.onload = init;
    s.onerror = function () { host.style.display = "none"; };
    document.head.appendChild(s);
  }

  function init() {
    var canvas = document.getElementById("hero3d");
    var W = host.clientWidth, H = host.clientHeight;
    var renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: false });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
    renderer.setSize(W, H, false);

    var scene = new THREE.Scene();
    scene.background = new THREE.Color(0x2b3358);
    scene.fog = new THREE.Fog(0x2b3358, 26, 74);

    var cam = new THREE.PerspectiveCamera(52, W / H, 0.1, 120);
    cam.position.set(0, 5.5, 24);

    scene.add(new THREE.AmbientLight(0x8890c0, 0.9));
    var sun = new THREE.DirectionalLight(0xffc890, 1.0);
    sun.position.set(-14, 18, 8);
    scene.add(sun);

    // fog sea
    var sea = new THREE.Mesh(
      new THREE.PlaneGeometry(220, 220),
      new THREE.MeshBasicMaterial({ color: 0x39406b, transparent: true, opacity: 0.9 }));
    sea.rotation.x = -Math.PI / 2;
    sea.position.y = -6;
    scene.add(sea);

    // floating islands: rocky cone + grass cap + a tiny house or trees
    var islands = [];
    function island(x, y, z, sc) {
      var g = new THREE.Group();
      var rock = new THREE.Mesh(
        new THREE.ConeGeometry(2.4, 4.2, 6),
        new THREE.MeshLambertMaterial({ color: 0x5d5a72 }));
      rock.rotation.x = Math.PI;
      rock.position.y = -2.1;
      g.add(rock);
      var cap = new THREE.Mesh(
        new THREE.CylinderGeometry(2.42, 2.1, 0.7, 6),
        new THREE.MeshLambertMaterial({ color: 0x4c8f5d }));
      g.add(cap);
      var lampPost = new THREE.Mesh(
        new THREE.CylinderGeometry(0.06, 0.06, 1.4, 5),
        new THREE.MeshLambertMaterial({ color: 0x3a3550 }));
      lampPost.position.set(0.9, 1.05, 0);
      g.add(lampPost);
      var lamp = new THREE.Mesh(
        new THREE.SphereGeometry(0.24, 10, 10),
        new THREE.MeshBasicMaterial({ color: 0xffd27a }));
      lamp.position.set(0.9, 1.85, 0);
      g.add(lamp);
      g.position.set(x, y, z);
      g.scale.setScalar(sc);
      g.userData = { y0: y, ph: Math.random() * Math.PI * 2 };
      scene.add(g);
      islands.push(g);
      return g;
    }
    island(-9, 1.5, -6, 1.15);
    island(0, 3.2, -16, 1.5);
    island(9.5, 0.8, -4, 0.95);
    island(4, 4.6, -28, 2.0);
    island(-15, 3.4, -20, 1.3);
    island(-5.5, 2.0, -11, 1.0);

    // low moon
    var moon = new THREE.Mesh(
      new THREE.SphereGeometry(3.2, 16, 16),
      new THREE.MeshBasicMaterial({ color: 0xf7ecc8, fog: false }));
    moon.position.set(-16, 13, -60);
    scene.add(moon);

    // the lantern spirit, swinging on a rope from the tall island
    var anchor = new THREE.Vector3(0, 7.6, -16);
    var spirit = new THREE.Group();
    var body = new THREE.Mesh(
      new THREE.SphereGeometry(0.55, 12, 12),
      new THREE.MeshLambertMaterial({ color: 0xffe9c9, emissive: 0x665522 }));
    spirit.add(body);
    var glowM = new THREE.MeshBasicMaterial({ color: 0xffd27a, transparent: true, opacity: 0.35 });
    var glow = new THREE.Mesh(new THREE.SphereGeometry(0.95, 12, 12), glowM);
    spirit.add(glow);
    scene.add(spirit);
    var ropeGeo = new THREE.BufferGeometry().setFromPoints([anchor, anchor]);
    var rope = new THREE.Line(ropeGeo,
      new THREE.LineBasicMaterial({ color: 0xffe0a0, transparent: true, opacity: 0.7 }));
    scene.add(rope);

    var px = 0, py = 0;
    host.addEventListener("pointermove", function (e) {
      var r = host.getBoundingClientRect();
      px = (e.clientX - r.left) / r.width - 0.5;
      py = (e.clientY - r.top) / r.height - 0.5;
    });

    var t0 = performance.now(), running = true;
    document.addEventListener("visibilitychange", function () {
      running = !document.hidden;
      if (running) { t0 = performance.now() - t * 1000; tick(); }
    });

    window.addEventListener("resize", function () {
      W = host.clientWidth; H = host.clientHeight;
      cam.aspect = W / H;
      cam.updateProjectionMatrix();
      renderer.setSize(W, H, false);
    });

    var t = 0;
    function tick() {
      if (!running) return;
      requestAnimationFrame(tick);
      t = (performance.now() - t0) / 1000;

      islands.forEach(function (g) {
        g.position.y = g.userData.y0 + Math.sin(t * 0.5 + g.userData.ph) * 0.35;
        g.rotation.y = Math.sin(t * 0.1 + g.userData.ph) * 0.08;
      });

      // pendulum swing under the anchor
      var ang = Math.sin(t * 0.9) * 0.85;
      var L = 6.5;
      spirit.position.set(
        anchor.x + Math.sin(ang) * L,
        anchor.y - Math.cos(ang) * L,
        anchor.z + Math.sin(t * 0.45) * 1.2);
      glow.scale.setScalar(1 + Math.sin(t * 2.2) * 0.08);
      rope.geometry.setFromPoints([anchor, spirit.position]);

      cam.position.x += ((px * 3) - cam.position.x) * 0.04;
      cam.position.y += ((5.5 - py * 2) - cam.position.y) * 0.04;
      cam.lookAt(0, 2.5, -14);
      renderer.render(scene, cam);
    }
    tick();
  }

  if (document.readyState === "complete") start();
  else window.addEventListener("load", start);
})();
