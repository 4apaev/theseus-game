theseus
================

an interstellar trade game, after Krugman's
[The Theory of Interstellar Trade](docs/The.Theory.of.Interstellar.Trade.md).
the server is Kafka and event sourcing. the client shows 3D stations and ships in a painted look.

the full rules are in [CLAUDE.md](CLAUDE.md). read it first. the rules below are the short form.


## rules

- write every reply, comment and commit message in ASD-STE100: short sentences, active voice, no filler.
- never commit. "stage" means `git add` only. i commit.
- never write to `backend/`. it is a separate repo with its own owner.
- never commit `sketches/`. 
- never run `git clean -x` here.


## agents

more agents work here at the same time. each one owns one lane, and changes files of that lane only.
the [board](agents/board.md) shows the lanes, their owners and their state.
keeton (claude) owns the client code. sam (codex) owns the art; his rules are in [agents/AGENTS.md](agents/AGENTS.md).


## layout

- `assets/` - art, blender sources, renders. git LFS tracks the binaries.
- `docs/` - game design and client architecture, shared by all repos.
- `data/` - the HYG star catalogue.
- `frontend/` - the client, a separate repo: vite, lit, three.js, typescript.
- `backend/` - the server, a separate repo. read only.


## docs

- [game design](docs/game.md) - the rules, the economy, "the look"
- [client architecture](docs/architecture.client.md) - layers, the loop, the world, with diagrams
- [screens brief](docs/screens.brief.md) - what each screen shows
- [client style guide](frontend/docs/guide.md) - html, css and type rules
- [client transport](frontend/docs/transport.md) - how the client talks to the gateway
- [backend progress](backend/docs/progress.md) - server steps and decisions, read only
