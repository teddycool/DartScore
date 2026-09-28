// Browser-free regression for an SSE proxy that responds 503 during an outage.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");

const elements = new Map();
function element() {
  return {textContent: "", hidden: false, disabled: false,
    classList: {toggle() {}}, addEventListener() {}, setAttribute() {},
    replaceChildren(...children) {this.children = children;}, reportValidity() {return true;}};
}
const document = {
  getElementById(id) {
    if (!elements.has(id)) elements.set(id, element());
    return elements.get(id);
  },
  createElement() {return element();},
  querySelectorAll() {return [];}
};
const streams = [];
class EventSource {
  constructor(url) {this.url = url; this.closed = false; streams.push(this);}
  close() {this.closed = true;}
  addEventListener() {}
}
let retry;
let loads = 0;
let darts = [20];
let pendingDarts = [];
const context = {
  document, EventSource, clearTimeout() {}, setTimeout(fn, ms) {retry = {fn, ms};},
  crypto: {randomUUID() {return "test-id";}},
  fetch: async () => {
    loads++;
    return {ok: true, json: async () => ({schema_version: 1, phase: "playing", revision: 2,
      game_type: "simple_score", players: [{name: "Player 1", total: 20, current_turn: darts}],
      pending_throw: pendingDarts[0] ?? null, pending_throws: pendingDarts, cameras: []})};
  }
};
const code = fs.readFileSync(path.join(__dirname, "../SW/Presentation/static/app.js"), "utf8");
vm.runInNewContext(code, context);

(async () => {
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(streams.length, 1);
  assert.equal(document.getElementById("score").textContent, 20);
  assert.deepEqual(Array.from(document.getElementById("turn").children, (item) => item.textContent), ["#1  20", "#2  —", "#3  —"]);
  assert.equal(document.getElementById("next-round").hidden, true);
  streams[0].onerror(); // A 503 may permanently close the browser's EventSource.
  assert.equal(streams[0].closed, true);
  assert.equal(document.getElementById("connection").textContent, "Engine disconnected · score may be stale");
  assert.equal(retry.ms, 2000);
  retry.fn();
  assert.equal(streams.length, 2);
  streams[1].onopen();
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(loads, 2);
  assert.equal(document.getElementById("connection").textContent, "Engine connected");
  pendingDarts = [{throw_id: "second", status: "uncertain", points: 15},
    {throw_id: "third", status: "confirmed", points: 25}];
  streams[1].onopen();
  await new Promise((resolve) => setImmediate(resolve));
  assert.deepEqual(Array.from(document.getElementById("turn").children, (item) => item.textContent),
    ["#1  20", "#2  ?", "#3  25?"]);
  assert.equal(document.getElementById("round-status").textContent,
    "Dart #2 needs your attention · 1 confirmed waiting");
  assert.equal(document.getElementById("attention-title").textContent, "Uncertain throw · Dart #2");
  darts = [20, 0, 25];
  pendingDarts = [];
  streams[1].onopen();
  await new Promise((resolve) => setImmediate(resolve));
  assert.deepEqual(Array.from(document.getElementById("turn").children, (item) => item.textContent),
    ["#1  20", "#2  0", "#3  25"]);
  assert.equal(document.getElementById("next-round").hidden, false);
  console.log("web reconnect OK");
})().catch((error) => {console.error(error); process.exitCode = 1;});
