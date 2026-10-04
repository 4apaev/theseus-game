plan · sam and keet
================

goal: the painted client, port first, on a fixture.
the order comes from [architecture.client.md](../docs/architecture.client.md).


## who does what

| who  | lane            | writes                                   | reads |
|------|-----------------|------------------------------------------|-------|
| keet | client          | `frontend/`, `data/`                     | all   |
| sam  | art             | `assets/`, `agents/sam/` (the sandbox locks it) | all   |

- keet writes all code. the user reads all of it.
- sam makes the art and the models: station kits, planets. 2 or 3 assets a job, about one job in each 5 hour credit window.
- sam works a [queue](sam/queue.md). a cron job starts him each hour; a run that dies continues on the next start.
- the contract: sam exports to `assets/exports/` and writes a `kit.json` for each station kit. keet copies the exports to `frontend/public/` and turns `kit.json` into the client's station layout.
- only the user switches branches and commits.


## 0 · gate

the user reviews `docs/architecture.client.md`. step 1 starts after that.


## 1 · foundation

**keet: the skeleton**, with the wire audits and the fixtures it needs
- move the core unchanged to `src/core/`: client, session, events, transport, util, chart, orbit.
- add empty `world/`, `places/`, `kit/`, `effects/`, `content/`.
- add fixture mode: `?fixture=<name>` boots on a recorded session, with no gateway.
- the old screens stay until step 5.
- done when: `npm run check` is green and `?fixture=docked` boots.

**keet: the pipeline and the content format**, after the skeleton
- one sync script copies `assets/exports/` and the station kits to `frontend/public/`. it replaces the copy by hand.
- the station layout and the model catalogue, as json, read from sam's `kit.json` and the blender readmes.
- done when: the sync runs clean and the json files are in `public/content/`.

**sam, in parallel:** the outpost kit (k1) and the sol planets (p1).

**sync A:** the user reviews the skeleton and commits.


## 2 · the port

**keet:** `world/` (one renderer, the layer stack, the iso camera, the clock, the loader with the paint pass), then `places/port`.

then the port plates of that station, cut and placed. tune the paint pass (toon ramp, outline, grime) to match the sprites.

**sam, in parallel:** the yards kit (k2), the outer sol planets (p2), the gate kit (k3).

**sync B:** a screenshot of the port on the fixture. the user checks the look.


## 3 · exchange and hold

**keet:** the kit (card, tray, hold grid, ₢ counter, toasts), the exchange and the hold, drag a good into the hold, ghosts.

then the 20 goods icons in the catalogue, the module icons, the tray and the hold art.

**sam, in parallel:** the other station kits (k4–k9) and the planets of the other systems (p3–p5).

**sync C:** buy and sell on the fixture, then on the real gateway.


## 4 · later

rigging, chart, comms. then flight, encounter, adrift. then remove the old code.


## keet, between steps, on the user's word

rewrite "the look" in `docs/game.md` and `docs/screens.brief.md`. both still describe the ink look.


## open

- the server asks (cargo cell positions, tug, x y z per system, ship destination) need the server lane. nobody holds it.
- the cron job is not installed. it waits for the user's yes.
