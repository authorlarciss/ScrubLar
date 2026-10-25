"""Inline HTML for the ScrubLar web UI.

Single page: upload form, preview with highlight, download buttons.
No templating engine — one string, no dependencies.
"""

from __future__ import annotations

__all__ = ["INDEX_HTML"]

INDEX_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>ScrubLar — обезличивание документов</title>
<style>
  body { font-family: system-ui, -apple-system, sans-serif; max-width: 960px;
         margin: 2rem auto; padding: 0 1rem; color: #222; }
  h1 { font-size: 1.4rem; }
  .disclaimer { background: #fff3cd; padding: 0.75rem; border-radius: 4px;
                font-size: 0.9rem; border-left: 4px solid #d39e00; }
  form { margin: 1.5rem 0; padding: 1rem; border: 1px dashed #ccc;
         border-radius: 4px; }
  input[type=file] { margin-right: 0.5rem; }
  button { padding: 0.4rem 0.9rem; cursor: pointer; }
  .summary { margin-top: 1.5rem; padding: 0.75rem; background: #e8f4ff;
             border-radius: 4px; }
  .preview { margin-top: 1rem; padding: 1rem; background: #f8f8f8;
             border-radius: 4px; white-space: pre-wrap; word-wrap: break-word;
             max-height: 400px; overflow-y: auto; font-family: monospace;
             font-size: 0.9rem; }
  mark { background: #ffd966; padding: 0 2px; border-radius: 2px; }
  .entity-list { margin-top: 1rem; }
  .entity-list table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
  .entity-list th, .entity-list td { padding: 0.35rem 0.5rem;
                                     border-bottom: 1px solid #eee;
                                     text-align: left; }
  .actions { margin-top: 1rem; display: flex; gap: 0.5rem; }
  .error { color: #b00020; margin-top: 1rem; }
</style>
</head>
<body>
<h1>ScrubLar — обезличивание документов перед отправкой в LLM</h1>
<p class="disclaimer">
  <strong>Дисклеймер.</strong> ScrubLar снижает риск утечки персональных данных,
  но не гарантирует полную защиту. Ответственность за соблюдение 152-ФЗ
  остаётся на пользователе. Обработка происходит локально, файлы не
  отправляются на сторонние серверы.
</p>

<form id="upload-form">
  <input type="file" id="file" accept=".docx,.txt" required>
  <button type="submit">Обезличить</button>
</form>

<div id="result" hidden>
  <div class="summary" id="summary"></div>
  <div class="actions">
    <button id="download-masked">Скачать очищенный</button>
    <button id="download-report">Скачать отчёт (JSON)</button>
  </div>
  <h2 style="font-size:1.1rem;margin-top:1.5rem;">Превью с подсветкой</h2>
  <div class="preview" id="preview"></div>
  <div class="entity-list">
    <h2 style="font-size:1.1rem;">Найденные ПДн</h2>
    <table>
      <thead><tr><th>Тип</th><th>Значение</th><th>Позиция</th></tr></thead>
      <tbody id="entity-rows"></tbody>
    </table>
  </div>
</div>

<div id="error" class="error" hidden></div>

<script>
const form = document.getElementById("upload-form");
const fileInput = document.getElementById("file");
const resultBox = document.getElementById("result");
const errorBox = document.getElementById("error");
let lastData = null;

form.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  errorBox.hidden = true;
  const f = fileInput.files[0];
  if (!f) return;
  const fd = new FormData();
  fd.append("file", f);
  try {
    const resp = await fetch("/mask", { method: "POST", body: fd });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: resp.statusText }));
      throw new Error(err.detail || "Ошибка сервера");
    }
    lastData = await resp.json();
    renderResult(lastData);
  } catch (e) {
    errorBox.textContent = "Ошибка: " + e.message;
    errorBox.hidden = false;
    resultBox.hidden = true;
  }
});

function renderResult(data) {
  const count = data.entities.length;
  document.getElementById("summary").textContent =
    "Обработано: " + data.original_filename +
    " — найдено ПДн: " + count + " — длина текста: " + data.text_length + " символов";

  const preview = document.getElementById("preview");
  preview.innerHTML = "";
  const text = data.original_text;
  const sorted = [...data.entities].sort((a, b) => a.start - b.start);
  let cursor = 0;
  for (const e of sorted) {
    if (e.start > cursor) {
      preview.appendChild(document.createTextNode(text.slice(cursor, e.start)));
    }
    const mark = document.createElement("mark");
    mark.textContent = text.slice(e.start, e.end);
    mark.title = e.kind;
    preview.appendChild(mark);
    cursor = e.end;
  }
  if (cursor < text.length) {
    preview.appendChild(document.createTextNode(text.slice(cursor)));
  }

  const tbody = document.getElementById("entity-rows");
  tbody.innerHTML = "";
  for (const e of sorted) {
    const tr = document.createElement("tr");
    tr.innerHTML = "<td>" + escapeHtml(e.kind) + "</td>" +
                   "<td>" + escapeHtml(e.value) + "</td>" +
                   "<td>" + e.start + "–" + e.end + "</td>";
    tbody.appendChild(tr);
  }

  resultBox.hidden = false;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[c]);
}

function downloadBlob(name, content, mime) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

document.getElementById("download-masked").addEventListener("click", () => {
  if (!lastData) return;
  const base = lastData.original_filename.replace(/\\.[^.]+$/, "");
  downloadBlob(base + ".masked.txt", lastData.masked_text, "text/plain;charset=utf-8");
});

document.getElementById("download-report").addEventListener("click", () => {
  if (!lastData) return;
  const base = lastData.original_filename.replace(/\\.[^.]+$/, "");
  const report = {
    original_filename: lastData.original_filename,
    text_length: lastData.text_length,
    entity_count: lastData.entities.length,
    entities: lastData.entities,
  };
  downloadBlob(base + ".report.json",
               JSON.stringify(report, null, 2),
               "application/json;charset=utf-8");
});
</script>
</body>
</html>
"""
