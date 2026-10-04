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
| ❎ | server  | -                | backend · wip           | `backend/`                                            |

`design` finished. the user archives it. the art direction is in [AGENTS.md](AGENTS.md), "the look".


## ✅ client · keeton

- status: plan step 1 done, waits for the user (sync A). `npm run check` is green. nothing staged.
  - the core is in `src/core/`, the catalogue in `src/content/catalogue.ts`. the moved bodies are unchanged; 4 client methods are `protected` now.
  - fixture mode: `?fixture=docked|transit|full`. `scripts/fixtures.js` builds the fixtures from the backend domain.
  - `npm run sync` copies the art of `assets/` into `public/`. `-n` shows the changes only. it ran once for the port: `public/art/` holds sam's art before your review, untracked.
  - wire audit: no gap. the client names no unknown event, and each REST call has a gateway route.
- step 2, beside the old app: `shell.html?fixture=docked`. the user chose 3D stations (2026-10-04).
  - the port is 3D: an orbit camera round the station; a 360° sky (ether, stars, the system's sun, a huge planet far off) turns with the camera and never moves.
  - every station shows the old `lem-station.glb` with the paint pass, until sam's painted station models land.
  - the planet: sol stations their own world (earth, jupiter for ganymede…), other systems sam's map. the sun: the spectral class.
- next: station models with sam, the port's hotspots and the kit (cards).
- asks: -


## ✅ assets · sam

- status: all 34 jobs ✅. new: cr1 crew portraits and sm1–sm9 station models wait for the user.
- 3D: `kick.py` runs the scripts sam lists in `sam/builds.txt` in blender, under `blender.sb` (writes only in `assets/`, no network), then starts sam once more. the runner, the profile and the rules sit in `agents/`, out of sam's reach. user approved 2026-10-04.
- keeton copies `assets/exports/` and the kits into `frontend/public/`.


## ❎ server · -

- status: free.


## brief for a new session

paste this, fill the angle brackets:

    you work in the <lane> lane: <repo> on <branch>.
    read CLAUDE.md and agents/board.md first, then take the lane on the board.
    task: <one goal, one sentence>.
    done when: <test, screenshot or doc that shows it>.
    out of scope: <what to leave alone>.
