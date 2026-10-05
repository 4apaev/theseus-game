board
================

one lane, one session. take a lane at the start, update it at the end.
names: keeton (keet) is claude: client code. sam is codex: art and models. other sessions use their session name.
shared files (`CLAUDE.md`, `docs/`, `.gitattributes`) change only on the user's word.

♻️ working · ✅ done, waits for review · 🆚 waits for another lane · ⛔ blocked · ❎ free

the current plan: [plan.md](plan.md).


## lanes

|    | lane    | session          | repo · branch           | owns                                                  |
|----|---------|------------------|-------------------------|-------------------------------------------------------|
| ✅ | assets  | sam              | theseus · master        | `assets/`, see the [queue](sam/queue.md)              |
| ✅ | client  | keeton           | frontend · painted-art  | `frontend/`                                           |
| ✅ | server  | keeton           | backend · wip           | `backend/docs/phase.4.md` only                        |

`design` finished. the user archives it. the art direction is in [AGENTS.md](AGENTS.md), "the look".


## ✅ client · keeton

- committed 2026-10-04: `0c23cd9 client: core, fixtures, 3D port` on painted-art. not pushed.
  - `src/core/` holds the wire and the truth. `?fixture=docked|transit|full` runs with no gateway.
  - `shell.html` is the painted client beside the old app: the port in 3D, an orbit camera, a 360° sky.
- done and committed 2026-10-05 (painted-art, not pushed):
  - the port uses sam's 9 station models: the ship on each `berth`, 2 robots on the `walk_*` points, the camera fits the model. 23 stations map to the 9 kits in `src/content/stations.ts`.
  - sam's f3 models are synced (06:33): the flicker is gone.
  - colour fix, 2026-10-05: `paint.ts` converted every model colour to srgb twice, so all models looked washed out. now the client shows the painted hex.
  - depth, 2026-10-05: the camera's near plane is 5% of its distance (`stage.ts`), so thin gaps hold at station range. sam's f4 removes the faces that share a plane.
  - sam's st2, st3 synced. sam runs on a model ladder (`kick.py`): gpt-6-astra medium, one rung down when a window burns faster than its clock.
  - `src/util.speak.ts`: the voices load on `voiceschanged`; the 15 novelty voices are out. tested: 63 voices kept.
  - the scale, 2026-10-05: the ship is 70 m (×7.2). sam's st1 stations are synced, built ×4 in metres. the ship rests on the pad (it sank before). `&ship=b` shows sam's s3 hull (gunner nose, portholes).
  - the anchorage, 2026-10-05: other ships wait on a ring round the station (`places/anchorage.ts`, `world/visitor.ts`). players' ships come from the traffic; npc ships arrive and leave every 20 to 50 s. each hull is scaled to its length in metres (`content/fleet.ts`); a hull with sockets gets a seeded random rig. sam's fl1 gives the other hulls sockets.
  - `npm run sync` copies every painted model now, icarus aside.
- 2026-10-05 night, on the user's word: commits in frontend and theseus. stages A, B and C of `frontend/docs/plan.md` are done:
  - A: fixture commands answer; the kit (hud, cards, toasts, credits, place labels); the router; hotspots and the ship focus; login and register.
  - B: the exchange (painted room, tray, buy and sell cards), the hold (cells, drag to trade), effects (cargo flies to the hold).
  - C: the chart (stars at their catalogue places, routes, courses with cost), the system map, transit (the ship underway) and the landing.
  - tested on the local gateway with a test player: register, login, buy at sol outpost, fly to mars hub, sell there.
- next: stage D (rigging), after the user's hull call: sam's sh1 rebuilds the far treasure on b. E (comms) does not wait for it.
- asks: -


## ✅ assets · sam

- status: all 34 jobs ✅. new: cr1 crew portraits and sm1–sm9 station models wait for the user.
- 3D: `kick.py` runs the scripts sam lists in `sam/builds.txt` in blender, under `blender.sb` (writes only in `assets/`, no network), then starts sam once more. the runner, the profile and the rules sit in `agents/`, out of sam's reach. user approved 2026-10-04.
- keeton copies `assets/exports/` and the kits into `frontend/public/`.


## ✅ server · keeton

- 2026-10-05: the user asked for a real phase 4. `docs/phase.4.md` is rewritten, uncommitted. no code.
- next: the user's review. the open calls are in the doc; the first is 4.3's well (the term as written strands the starter).
- asks: stale facts in shared docs, for the user: game.md's well table puts the outpost at 1.336 AU (systems.js: 1.0); game.md's crew says "no portraits".


## brief for a new session

paste this, fill the angle brackets:

    you work in the <lane> lane: <repo> on <branch>.
    read CLAUDE.md and agents/board.md first, then take the lane on the board.
    task: <one goal, one sentence>.
    done when: <test, screenshot or doc that shows it>.
    out of scope: <what to leave alone>.
