document.addEventListener("DOMContentLoaded", () => {
  const priceRange = document.querySelector("#price-range");
  if (priceRange) {
    const priceOptions = {
      buy: [
        ["", "Any budget"],
        ["under-100000", "Under $100,000"],
        ["100000-300000", "$100,000 - $300,000"],
        ["over-300000", "$300,000+"],
      ],
      rent: [
        ["", "Any budget"],
        ["under-1000", "Under $1,000 / month"],
        ["1000-2500", "$1,000 - $2,500 / month"],
        ["over-2500", "$2,500+ / month"],
      ],
    };

    document.querySelectorAll('input[name="intent"]').forEach((input) => {
      input.addEventListener("change", () => {
        priceRange.replaceChildren(
          ...priceOptions[input.value].map(
            ([value, label]) => new Option(label, value),
          ),
        );
      });
    });
  }

  const menuToggle = document.querySelector("#menu-toggle");
  if (menuToggle) {
    const siteDrawer = document.querySelector("#site-drawer");
    const drawerBackdrop = document.querySelector("#drawer-backdrop");
    const drawerClose = document.querySelector("#drawer-close");

    function openDrawer() {
      siteDrawer.inert = false;
      siteDrawer.setAttribute("aria-hidden", "false");
      siteDrawer.classList.add("is-open");
      drawerBackdrop.hidden = false;
      menuToggle.setAttribute("aria-expanded", "true");
      document.body.classList.add("drawer-open");
      drawerClose.focus();
    }

    function closeDrawer() {
      siteDrawer.classList.remove("is-open");
      siteDrawer.setAttribute("aria-hidden", "true");
      siteDrawer.inert = true;
      drawerBackdrop.hidden = true;
      menuToggle.setAttribute("aria-expanded", "false");
      document.body.classList.remove("drawer-open");
      menuToggle.focus();
    }

    menuToggle.addEventListener("click", openDrawer);
    drawerClose.addEventListener("click", closeDrawer);
    drawerBackdrop.addEventListener("click", closeDrawer);
    siteDrawer.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", closeDrawer);
    });

    document.addEventListener("keydown", (event) => {
      if (!siteDrawer.classList.contains("is-open")) return;
      if (event.key === "Escape") closeDrawer();
      if (event.key === "Tab") {
        const focusable = siteDrawer.querySelectorAll(
          "a[href], button:not([disabled])",
        );
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    });
  }

  const likeButton = document.querySelector('[data-action="like"]');
  if (likeButton) {
    const likeForm = likeButton.closest("form");
    const likeIcon = likeButton.querySelector("i");
    const likeLabel = likeButton.querySelector("span");
    const likeFeedback = document.querySelector("#like-feedback");

    if (likeForm) {
      likeForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        likeButton.disabled = true;

        try {
          const response = await fetch(likeForm.action || window.location.href, {
            method: "POST",
            body: new FormData(likeForm),
            headers: { "X-Requested-With": "XMLHttpRequest" },
          });
          const contentType = response.headers.get("content-type") || "";
          if (!contentType.includes("application/json")) {
            throw new Error("Could not update like. Refresh the page and try again.");
          }
          const result = await response.json();
          if (!response.ok)
            throw new Error(
              result.message || "Could not update like. Please try again.",
            );

          likeButton.classList.toggle("is-active", result.liked);
          likeButton.setAttribute("aria-pressed", String(result.liked));
          likeIcon.classList.toggle("bi-heart-fill", result.liked);
          likeIcon.classList.toggle("bi-heart", !result.liked);
          likeLabel.textContent = result.liked
            ? likeButton.dataset.activeLabel
            : likeButton.dataset.defaultLabel;
          likeFeedback.textContent = result.message;
        } catch (error) {
          likeFeedback.textContent = error.message;
        } finally {
          likeButton.disabled = false;
        }
      });
    }
  }
});
