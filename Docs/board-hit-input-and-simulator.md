# Board-hit input and simulator

This is the input seam between a future camera resolver and `GameService`.
The Python contract lives in `SW/DartScoreEngine/Input/contract.py`. It does
not import OpenCV, Pygame, GPIO, HTTP, or camera code. The simulator feeds
this same coordinator without hardware; it does not calculate game scores.

## Candidate contract

`BoardHitCandidate` contains:

| Field | Meaning |
| --- | --- |
| `throw_id` | Stable, non-empty ID for one physical throw; two camera observations must already be resolved to this one ID. |
| `captured_at` | Timezone-aware capture timestamp. |
| `source` | Producer name, such as `simulator` or a future resolver. |
| `status` | `confirmed` or `uncertain`. |
| `points` | Achievable single-dart points, or `None` for an uncertain hit with no proposal. The first version is points-only. |
| `camera_ids` | Camera IDs contributing to the candidate, if any. |
| `evidence_refs` | Opaque image/evidence references, if any; never image bytes. |

`InputCoordinator.submit()` returns `scored`, `pending`, or `ignored`. Only a
confirmed accepted hit enters `GameService.record_hit`. An uncertain candidate
does not alter the game total. One pending review is supported at a time; new
throw IDs are ignored while it is pending to preserve throw order. `resolve()`
confirms the proposed points, corrects them with achievable single-dart points,
or rejects a false detection. An accepted miss at zero points is distinct from
rejecting a false detection. A repeated identical candidate/resolution returns
the original result; reuse of an ID with conflicting content is rejected.

While paused, new candidates are ignored and their IDs cannot be scored after
resume. A pending hit from before Pause can be resolved after Resume, but not
during Pause. The camera capture pipeline must establish a fresh frame baseline
on Resume; the simulator does not model image frames.

Camera health is a separate `ready | degraded | unavailable` value. A health
change does not mutate `GameService` or its revision. This PR does not define
whether degraded capture is sufficient to produce a confirmed hit.

## Run the simulator

From the repository root, with Python 3.10 or later:

```
python3 SW/simulate_game.py Testdata/Simulations/basic_game.jsonl
python3 -m unittest discover -s tests -v
```

The script is JSON Lines: one object per line. Supported actions are `start`,
`hit`, `uncertain`, `confirm`, `correct`, `reject`, `pause`, `resume`,
`clear_board`, and `camera`. A hit has `throw_id` and `points`; an uncertain hit
may omit `points`. A correction has `throw_id` and `points`. A camera status
action has `camera_id` and `state`. The simulator emits one JSON object after
each action with its result, game snapshot, pending IDs, and camera health.
For reproducible scripts it assigns deterministic UTC timestamps based on line
number. The example ends with a total of 80 and camera 1 unavailable.

The CLI is a developer diagnostic, not the HTTP API. It uses the one-player
`simple_score` game. Pending candidates, accepted IDs, and camera health are
**in memory only**; a process restart loses them. Persistence, durable IDs,
operator request IDs, API events, evidence image storage, and 301/501 rules are
separate next steps. The legacy Pygame loop remains on its existing direct
`GameService` path for now; migrating it through this coordinator is also a
later integration step.
