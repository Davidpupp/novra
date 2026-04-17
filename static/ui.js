(function () {
  const root = document.body;
  const revealables = document.querySelectorAll(".reveal, .reveal-card");
  const topbar = document.querySelector(".topbar");
  const cards = document.querySelectorAll(".card");

  // Custom Cursor Tracking
  function setupCustomCursor() {
    const cursor = document.querySelector("body::before");
    const cursorDot = document.querySelector("body::after");
    
    if (!window.matchMedia("(pointer: fine)").matches) return;
    
    document.addEventListener("mousemove", (e) => {
      if (cursor) {
        cursor.style.left = e.clientX + "px";
        cursor.style.top = e.clientY + "px";
      }
      if (cursorDot) {
        cursorDot.style.left = e.clientX + "px";
        cursorDot.style.top = e.clientY + "px";
      }
    });

    // Mouse tracking for card glow effect
    cards.forEach(card => {
      card.addEventListener("mousemove", (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        card.style.setProperty("--mouse-x", x + "px");
        card.style.setProperty("--mouse-y", y + "px");
      });
    });
  }

  function updateScrollBackground() {
    const scrollable = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    const progress = Math.min(1, window.scrollY / scrollable);
    root.style.setProperty("--scroll-progress", progress.toFixed(3));
  }

  function updateHeaderScroll() {
    if (!topbar) return;
    if (window.scrollY > 50) {
      topbar.classList.add("scrolled");
    } else {
      topbar.classList.remove("scrolled");
    }
  }

  function setupReveal() {
    if (!revealables.length) return;
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("in-view");
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -50px 0px" }
    );
    revealables.forEach((el) => observer.observe(el));
  }

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });

  // Wishlist toggle function
  window.toggleWishlist = function(btn) {
    btn.classList.toggle("active");
    btn.innerHTML = btn.classList.contains("active") ? "♥" : "♡";
  };

  window.addEventListener("scroll", updateScrollBackground, { passive: true });
  window.addEventListener("scroll", updateHeaderScroll, { passive: true });
  updateScrollBackground();
  updateHeaderScroll();
  setupReveal();
  setupCustomCursor();

  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("/sw.js").catch(() => {});
    });
  }
})();
