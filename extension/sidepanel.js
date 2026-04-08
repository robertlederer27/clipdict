const listEl = document.getElementById("list");
const emptyEl = document.getElementById("empty");
const WS_URL = "ws://localhost:52780/ws";
let socket = null;

function render(items) {
  listEl.innerHTML = "";
  const keys = Object.keys(items);

  if (keys.length === 0) {
    emptyEl.style.display = "block";
    return;
  }
  emptyEl.style.display = "none";

  for (const key of keys) {
    const value = items[key];
    const row = document.createElement("div");
    row.className = "row";

    const label = document.createElement("span");
    label.className = "label";
    label.textContent = key;

    const valueWrap = document.createElement("span");
    valueWrap.className = "value";

    if (isUrl(value)) {
      const a = document.createElement("a");
      a.href = value;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      a.textContent = value;
      a.className = "link";
      a.addEventListener("click", (e) => e.stopPropagation());
      valueWrap.appendChild(a);

      const copyBtn = document.createElement("button");
      copyBtn.className = "copy-btn";
      copyBtn.textContent = "COPY";
      copyBtn.title = "Copy";
      copyBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        copyValue(row, value);
      });
      valueWrap.appendChild(copyBtn);
    } else {
      valueWrap.textContent = value;
      row.addEventListener("click", () => copyValue(row, value));
      row.classList.add("clickable");
    }

    row.appendChild(label);
    row.appendChild(valueWrap);
    listEl.appendChild(row);
  }
}

function isUrl(str) {
  return typeof str === "string" && /^https?:\/\/\S+$/i.test(str);
}

async function copyValue(row, value) {
  await navigator.clipboard.writeText(value);
  row.classList.add("copied");
  setTimeout(() => row.classList.remove("copied"), 600);
}

function connect() {
  socket = new WebSocket(WS_URL);

  socket.addEventListener("message", (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "update") {
      render(data.items);
    }
  });

  socket.addEventListener("close", () => {
    setTimeout(connect, 3000);
  });

  socket.addEventListener("error", () => {
    socket.close();
  });
}

connect();
