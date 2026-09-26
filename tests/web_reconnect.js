// Browser-free regression for an SSE proxy that responds 503 during an outage.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");

const elements = new Map();
const document = {
  getElementById(id) {
    if (!elements.has(id)) elements.set(id, {
      textContent: "", hidden: false, disabled: false,
      classList: {toggle() {}}, addEventListener() {}, reportValidity() {return true;}
    });
    return elements.get(id);
  },
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
const context = {
  document, EventSource, clearTimeout() {}, setTimeout(fn, ms) {retry = {fn, ms};},
  crypto: {randomUUID() {return "test-id";}},
  fetch: async () => {
    loads++;
    return {ok: true, json: async () => ({schema_version: 1, phase: "playing", revision: 2,
      game_type: "simple_score", players: [{name: "Player 1", total: 20, current_turn: [20]}], cameras: []})};
  }
};
const code = fs.readFileSync(path.join(__dirname, "../SW/Presentation/static/app.js"), "utf8");
vm.runInNewContext(code, context);

(async () => {
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(streams.length, 1);
  assert.equal(document.getElementById("score").textContent, 20);
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
  console.log("web reconnect OK");
})().catch((error) => {console.error(error); process.exitCode = 1;});
