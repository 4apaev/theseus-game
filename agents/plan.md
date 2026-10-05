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


## the steps

the client steps, A to H, are in [frontend/docs/plan.md](../frontend/docs/plan.md).
done before it: the skeleton, fixture mode, the sync script, `world/` and the port.
sam's jobs for each stage are at the end of that file.


## keet, between steps, on the user's word

rewrite "the look" in `docs/game.md` and `docs/screens.brief.md`. both still describe the ink look.


## open

- the server asks (cargo cell positions, tug, ship destination) are in `backend/docs/phase.4.md` or still open. x y z per system: the client reads them from `data/` (step C1).
