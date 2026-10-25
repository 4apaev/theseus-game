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
| ♻️ | assets  | sam              | theseus · master        | `assets/`, see the [queue](sam/queue.md). model: gpt-6-astra medium, pinned (`log/pin`) while the week is under 90% (the user, 2026-10-07) |
| ✅ | client  | keeton           | frontend · painted-art  | `frontend/`: F2 to G3 done: `71eba71`, master = painted-art. not pushed |
| ✅ | server  | keeton           | backend · wip           | `backend/docs/phase.4.md` only                        |

`design` finished. the user archives it. the art direction is in [AGENTS.md](AGENTS.md), "the look".


## ✅ client · keeton

- 2026-10-26: committed `71eba71 client: toy only, F2 to G3`; master fast-forwarded to painted-art. not pushed.
- 2026-10-25, the user's word: finish the client, the toy look as the only view, merge to master, the old client only as a tag.
  - tags (local, not pushed): `client-1` the panel client (as before), `client-2` = `0f6b643`, the painted look beside the toy look.
  - G1, G2: `index.html` boots the shell; the toy look is the only look (`?toy` gone, `?theme=` stays). the old app, the painted look and the old `public/` art are deleted.
  - F3: `npm run sync` compresses the toy models (meshopt, quantized): 23 MB to 6.3 MB; a load line on the top edge; memory flat after 20 place changes.
  - F2: `src/sound.ts`, web audio, no files: buy, sell, install, remove, depart, arrive, letters, a bed per place. settings: "sounds".
  - F4: playwright, `npm run screens`, in `npm run check`: 7 places and transit against `test/screens/`, the memory check.
  - checked: `npm run check` passes (lint, 45 tests, build, 9 screen tests); a boot on the gateway shows the login with no errors.
  - left on disk, untracked: `frontend/prototype/` (47 files, 27 MB, never in git). the user decides.
  - next: on "commit": commit on painted-art, fast-forward master to it. push only on the user's word.
  - the hidden browser pane draws no frames: its screenshots show a stale, dim frame. use `npm run screens` to see the client.
- 2026-10-25, committed: frontend `0f6b643 client: the toy look` (pushed), theseus `7e87e0c assets: the toy look` (not pushed). the full star catalogue `data/hygdata_v42.csv` was gone from disk with no record why: restored.
- 2026-10-25, the user's review of the toy look: 5 layout faults fixed.
  - the top bar under 56rem: the places take a row of their own; the feed and toasts move down.
  - the tray: a list fades at an edge with more tiles past it (`data-more`).
  - rigging: the camera frames the whole hull under the top bar.
  - the trade card: "at most 0" gives its reason (the hold is full, not enough credits, none aboard).
  - `kit-select` in a card: the card's menu rules skip the select, so its list is vertical again.
  - the camera: a place that sets its view stops a flight still under way; the stage learns of an arrival before the place enters. before, the port's arrival flight carried rigging's camera off to the port's distance.
- 2026-10-07 night, the user's list (painted-art): see [keeton's queue](keeton/queue.md).
  - done: the toy bay is the only rigging (old rigging and blueprint deleted), the ship floats over its diagram; bubble exhaust with sam's puff sprites and a tail; the feed and toasts under the top line; the dock swell stays under the pointer; comms panel in the toy look; `kit-select`; pressed and hover states, toggles; place transitions; labels on hover (here and selected stay); skins (police, military, 10 more; a picker in the ship card, `skin` rides on rename); each station kind wears a skin; the orbit view (`#orbit`, client only); a toy planet beyond the port.
  - sam's night (all 15 jobs ✅, 07:47) is in the client: his skins, 10 new ships (towing ships pull their loads), the station kinds (market, mine, lab, relay, ship yard, gas skimmer), each in a skin after its render; the dry dock and gas station between the station and its planet; his planets in the port; his planet and moon in the orbit view.
  - not in the client yet: Icarus (no such station in the universe), the weapon modules (no weapon slots), the crew portraits (no crew screen).
  - sam is pinned to gpt-6-astra medium (`log/pin`) while the week is under 90%.

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
- 2026-10-05 night, on the user's word: commits in frontend and theseus. stages A to E and F1 of `frontend/docs/plan.md` are done:
  - A: fixture commands answer; the kit (hud, cards, toasts, credits, place labels); the router; hotspots and the ship focus; login and register.
  - B: the exchange (painted room, tray, buy and sell cards), the hold (cells, drag to trade), effects (cargo flies to the hold).
  - C: the chart (stars at their catalogue places, routes, courses with cost), the system map, transit (the ship underway) and the landing.
  - D: rigging (slots, preview, install, remove, rename), the traffic list. E: comms (channel, letters), the feed line and the console. F1: settings.
  - tested on the local gateway: register, login, buy at sol outpost, fly to mars hub, sell there, a letter from a second player.
- the anchorage docks ships on a station's pads (`berth_b`… with a size) before the ring: ready for sam's dk1 outpost.
- 2026-10-06, uncommitted: the sky is near black navy with 20000 tinted stars, the fog only a faint milky way (`world/sky.ts`); stars scale with the pixel ratio. police-patrol and police-inspector join the npc hulls. the rigging bay is a blueprint sheet (`world/blueprint.ts`), no painted plate: the user found the workshop out of scale. the camera orbits the ship from above the sheet (`stage.tilt`).
- 2026-10-06, uncommitted: `&globe` shows the station as a small world, after star birds (`world/globe.ts`): a low-poly rock, facilities from the cc0 kits in `assets/kits/` (kaykit, kenney, quaternius), our ship on the top pad, visitors on 2 side pads. a click on a facility opens its place. `npm run sync` copies the kits.
- 2026-10-06: the user's references for the look are in `sketches/direction-2026-10-06/`; stage K of the plan holds them. the globe is a sketch: the parts of 3 kits do not match yet.
- 2026-10-06, new priority: the toy look; 3D and client work allowed again (06:15). goal: 2 or 3 variants of the new design. keeton's queue (`agents/keeton/queue.md`): client-toy-theme, -market, -port, -rigging, -comms behind `?toy` and `&theme=meadow|lagoon|postcard`, then diagram images (`assets/concepts/toy/screens/make.py`). scheduled runs at 07, 09, 11, 13, 15; review sheets and a notification at 12:00 and 16:00 (`assets/concepts/toy/review/`). stage K and the globe sketch feed client-toy-port.
- 2026-10-06 19:40, uncommitted: `?toy` in the client (`&theme=meadow|toybox|lagoon|postcard`): the toy kit css, the market on a 3D iso plane (`places/market.ts`, `world/plane.ts`, `core/market.ts`) with sam's sprites and icons, the port with sam's toy station and ships, bubble exhaust (`world/puffs.ts`), the trade card shared with the exchange (`places/trade.ts`). 20:10: rigging (`places/bay.ts`) and comms (`places/net.ts`) on the plane too. the scheduled runs stalled on a permission prompt; both stopped.
- toy images, 19:57 (scheduled run): 28 ui icons in `assets/icons/toy/ui/svg/` (colours as `--toy-*` vars), sheets `sheet-*.png`; market variants `market-all-*`, `market-ship-*` in `assets/concepts/toy/screens/`. the rigging bay (`places/bay.ts`) belongs to the live session.
- next: the user reviews `shell.html`. then F2 to F4, then G (index.html boots the shell, the old code goes).
- asks: F2 needs sound files, F3 adds gltf-transform (dev dependency), F4 adds playwright: the user's call. 2 local test players exist in the dev db: keet-a5-test, keet-e1-test.


## ✅ assets · sam

- 2026-10-26: the user approves `toy-sky-reset`: the models must look very close to the frames. queued ✳️ toy-3d-sky-reset. the client switches to the new sky models when they land (keeton).
- 2026-10-26, the user's review, relayed by keeton: the crew goes with the little robots; 4 ships miss (liner, courier, raider, police cutter); the planets of `toy-sky-rich` drift to realism: a style reset. new jobs ✳️: toy-crew-robots, toy-ships-redo, toy-sky-reset. `style.md`: the crew block (robots, an anchor sheet) and the sky block (a detail budget, a check beside 2 approved icons).
- 2026-10-26: the queue's new legend (✳️ open, ❎ dropped) is in `kick.py`, `brief/collect.py` and `AGENTS.md` too. before, kick started sam only on ❎.
- status: all 34 jobs ✅. new: cr1 crew portraits and sm1–sm9 station models wait for the user.
- 2026-10-06: the user found the art drifting to glossy photoreal. AGENTS.md "the style lock": the painted-parts-v1 anchor, low-poly, matte, triangle budgets, furniture painted into plates. `agents/style.md` holds the locked prompt blocks (sam reads, never writes). no new 3D until the style is settled. queued cr5 (4 portraits, a test), pl1 (3 outpost places); lp1 (far treasure low-poly), pl2 (holds), cr6 (the other portraits), cn2 (crew flow) wait ⏸ for the user's approval of the tests. f4, dk1, st4, fl1, cc1 stay ⛔.
- 2026-10-06, new priority: the toy look (toy-like, grotesque, playful, colourful; the feel of star birds, not a copy). images only. `agents/style.md` holds the toy block. queued: toy-station, toy-ship-cargo, -military, -industrial, -research, toy-nav-manifest, toy-orbit-maneuver, toy-combat. older jobs moved to `sam/done.md`. job ids are readable names now.
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
