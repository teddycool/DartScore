"use strict";

const byId = (id) => document.getElementById(id);
let state = null;
let online = false;
let busy = false;
let connection = null;
let generation = 0;
let retryTimer = null;

function render() {
  const ready = online && state !== null;
  const pending = state?.pending_throw;
  const pendingCount = state?.pending_throws?.length ?? (pending ? 1 : 0);
  byId("connection").textContent = ready ? "Engine connected" : "Engine disconnected · score may be stale";
  byId("connection").classList.toggle("online", ready);
  byId("score").textContent = state?.players?.[0]?.total ?? "—";
  byId("player").textContent = state?.players?.[0]?.name ?? "Player 1";
  byId("phase").textContent = state?.phase ?? "Loading";
  byId("game-type").textContent = state?.game_type === "simple_score" ? "Simple score" : "Waiting for game";
  const darts = state?.players?.[0]?.current_turn ?? [];
  const complete = darts.length === 3;
  byId("turn").replaceChildren(...Array.from({length: 3}, (_, index) => {
    const item = document.createElement("li");
    item.textContent = darts[index] ?? "—";
    item.classList.toggle("empty", index >= darts.length);
    item.setAttribute("aria-label", `Dart ${index + 1}: ${index < darts.length ? `${darts[index]} points` : "not thrown"}`);
    return item;
  }));
  const reviews = (state?.pending_throws ?? []).filter((item) => item.status === "uncertain").length;
  const queued = pendingCount - reviews;
  byId("round-status").textContent = complete ? "Round complete · remove the darts to continue" :
    `${darts.length} scored · ${reviews} to review${queued ? ` · ${queued} confirmed waiting` : ""} · ${3 - darts.length - pendingCount} remaining`;
  const cameras = state?.cameras ?? [];
  byId("camera-status").textContent = cameras.length ? cameras.map((c) => `${c.camera_id}: ${c.state}`).join(" · ") : "Cameras: not connected";
  byId("attention").hidden = !pending;
  if (pending) {
    byId("attention-title").textContent = pending.status === "confirmed" ? "Confirmed dart waiting" : "Uncertain throw";
    byId("candidate").textContent = pending.status === "confirmed" ?
      `Dart ${pending.throw_id} was detected as ${pending.points} points. Apply this saved score to finish the round.` :
      `${reviews} throw${reviews === 1 ? "" : "s"} to review. Next dart (${pending.throw_id}): proposed ${pending.points ?? "unknown"} points. Confirmed darts behind it will score automatically after review.`;
    byId("confirm").textContent = pending.status === "confirmed" ? "Apply confirmed score" : "Confirm proposed score";
    byId("evidence").textContent = pending.evidence_refs?.length ? `Evidence references: ${pending.evidence_refs.join(", ")}` : "No images available yet.";
  }
  byId("start").hidden = state?.phase !== "idle";
  byId("pause").hidden = state?.phase !== "playing";
  byId("resume").hidden = state?.phase !== "paused";
  byId("next-round").hidden = !complete || state?.phase === "idle";
  for (const button of document.querySelectorAll("button")) button.disabled = !ready || busy;
  byId("next-round").disabled ||= Boolean(pending) || state?.phase !== "playing";
  byId("confirm").disabled ||= pending?.points == null || state?.phase !== "playing";
  byId("correct-points").disabled = !ready || busy || state?.phase !== "playing";
  byId("engine-status").textContent = `Engine: ${state?.engine?.state ?? "unavailable"}. ${state?.engine?.reason ?? ""}`;
}

async function refresh() {
  const requestGeneration = ++generation;
  try {
    const response = await fetch("/api/v1/state", {cache: "no-store"});
    if (!response.ok) throw new Error("State unavailable");
    const next = await response.json();
    if (next.schema_version !== 1) throw new Error("Unsupported API version");
    if (requestGeneration !== generation) return;
    state = next;
    online = true;
    if (byId("notice").textContent === "State unavailable" || byId("notice").textContent === "Unsupported API version") byId("notice").textContent = "";
    render();
  } catch (error) {
    if (requestGeneration !== generation) return;
    online = false;
    byId("notice").textContent = error.message;
    render();
  }
}

async function command(type, payload = {}) {
  if (!online || !state || busy) return;
  busy = true;
  render();
  byId("notice").textContent = "Sending command…";
  const body = {schema_version: 1, request_id: crypto.randomUUID(),
                expected_revision: state.revision, type, payload};
  try {
    const response = await fetch("/api/v1/commands", {
      method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error?.message || `Command failed (${response.status})`);
    if (type === "correct_throw") byId("correct-points").value = "";
    byId("notice").textContent = `Accepted: ${type.replaceAll("_", " ")}.`;
  } catch (error) {
    byId("notice").textContent = `${error.message}. Reloading engine state.`;
  } finally {
    busy = false;
    await refresh();
  }
}

byId("start").addEventListener("click", () => command("start_game", {game_type: "simple_score"}));
byId("pause").addEventListener("click", () => command("pause_game"));
byId("resume").addEventListener("click", () => command("resume_game"));
byId("next-round").addEventListener("click", () => command("next_round"));
byId("confirm").addEventListener("click", () => command("confirm_throw", {throw_id: state.pending_throw.throw_id}));
byId("reject").addEventListener("click", () => command("reject_throw", {throw_id: state.pending_throw.throw_id}));
byId("correct-form").addEventListener("submit", (event) => {
  event.preventDefault();
  if (!byId("correct-points").reportValidity()) return;
  command("correct_throw", {throw_id: state.pending_throw.throw_id,
                            points: Number(byId("correct-points").value)});
});

function connectEvents() {
  clearTimeout(retryTimer);
  connection?.close();
  connection = new EventSource("/api/v1/events");
  connection.onopen = () => refresh();
  connection.onerror = () => {
    // The proxy returns 503 while the engine is down. Some browsers stop
    // retrying EventSource after that response, so explicitly open a new one.
    generation++;
    online = false;
    render();
    connection.close();
    retryTimer = setTimeout(connectEvents, 2000);
  };
  for (const kind of ["game_changed", "throw_scored", "throw_pending", "engine_status_changed"]) {
    connection.addEventListener(kind, () => refresh());
  }
}

render();
refresh();
connectEvents();
