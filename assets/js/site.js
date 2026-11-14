(() => {
  const header = document.querySelector("[data-header]");
  const hero = document.querySelector("[data-hero]");

  // Header turns solid once the hero photograph has scrolled away beneath it.
  if (header && hero && "IntersectionObserver" in window) {
    const headerH = () => header.offsetHeight;
    let io;
    const watch = () => {
      io?.disconnect();
      io = new IntersectionObserver(
        ([entry]) => header.classList.toggle("is-solid", !entry.isIntersecting),
        { rootMargin: `-${headerH() + 1}px 0px 0px 0px`, threshold: 0 }
      );
      const sentinel = hero.querySelector(".hero__body");
      io.observe(sentinel || hero);
    };
    watch();
    window.addEventListener("resize", () => { clearTimeout(watch.t); watch.t = setTimeout(watch, 150); });
  }

  // Mobile navigation.
  const toggle = document.querySelector("[data-nav-toggle]");
  const menu = document.querySelector("[data-nav-menu]");
  if (toggle && menu) {
    const label = toggle.querySelector(".site-nav__toggle-label");
    const setOpen = (open) => {
      toggle.setAttribute("aria-expanded", String(open));
      menu.classList.toggle("is-open", open);
      header.classList.toggle("is-open", open);
      if (label) label.textContent = open ? "Close" : "Menu";
    };
    toggle.addEventListener("click", () => setOpen(toggle.getAttribute("aria-expanded") !== "true"));
    menu.addEventListener("click", (e) => { if (e.target.closest("a")) setOpen(false); });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
        setOpen(false);
        toggle.focus();
      }
    });
    window.matchMedia("(min-width: 1101px)").addEventListener("change", (e) => { if (e.matches) setOpen(false); });
  }

  // Consultation form: nothing leaves the page, because there is no firm to send it to.
  const form = document.querySelector("[data-form]");
  const status = document.querySelector("[data-form-status]");
  if (form && status) {
    const field = (n) => form.elements.namedItem(n);
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      form.classList.add("was-validated");

      if (!form.checkValidity()) {
        const missing = [];
        if (!field("name").value.trim()) missing.push("your name");
        if (!field("email").validity.valid) missing.push(field("email").value ? "a valid email address" : "your email");
        if (!field("matter").value.trim()) missing.push("a short description of your matter");
        if (!field("ack").checked) missing.push("the acknowledgement");
        status.dataset.state = "error";
        status.textContent = `Your inquiry wasn't sent. Still needed: ${missing.join(", ").replace(/, ([^,]*)$/, " and $1")}.`;
        form.querySelector(":invalid")?.focus();
        return;
      }

      const first = field("name").value.trim().split(/\s+/)[0];
      status.dataset.state = "sent";
      status.innerHTML = "";
      const strong = document.createElement("strong");
      strong.textContent = `Thank you, ${first}. Your inquiry was not sent.`;
      status.append(
        strong,
        " Dewey, Cheatem & Howe is not a real law firm, so nothing left this page and nothing was stored. ",
        "If you need legal help, contact a licensed attorney or your local bar association’s referral service. ",
        "On the bright side, this is the only consultation in the firm’s history that was genuinely free."
      );
    });
  }
})();
