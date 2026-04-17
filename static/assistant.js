(function () {
  const toggle = document.getElementById("ai-toggle");
  const panel = document.getElementById("ai-panel");
  const close = document.getElementById("ai-close");
  const form = document.getElementById("ai-form");
  const input = document.getElementById("ai-input");
  const messages = document.getElementById("ai-messages");

  if (!toggle || !panel || !form || !input || !messages || !close) {
    return;
  }

  function addMessage(text, cls) {
    const p = document.createElement("p");
    p.className = cls;
    p.textContent = text;
    messages.appendChild(p);
    messages.scrollTop = messages.scrollHeight;
  }

  function addSuggestions(items) {
    if (!Array.isArray(items) || !items.length) return;
    const box = document.createElement("div");
    box.className = "ai-suggestions";
    items.forEach((item) => {
      const a = document.createElement("a");
      a.href = `/produto/${item.slug}`;
      a.className = "chip";
      a.textContent = `${item.name} - R$ ${Number(item.price).toFixed(2).replace(".", ",")}`;
      box.appendChild(a);
    });
    messages.appendChild(box);
    messages.scrollTop = messages.scrollHeight;
  }

  toggle.addEventListener("click", () => panel.classList.toggle("hidden"));
  close.addEventListener("click", () => panel.classList.add("hidden"));

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if (!message) return;
    addMessage(message, "ai-user");
    input.value = "";

    try {
      const response = await fetch("/api/ai-assistant", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });
      const data = await response.json();
      addMessage(data.answer || "Nao consegui responder agora. Tente novamente.", "ai-bot");
      addSuggestions(data.products || []);
    } catch (_error) {
      addMessage("Serviço de IA indisponivel no momento.", "ai-bot");
    }
  });
})();
