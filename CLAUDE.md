Project Memory
================

Instructions here apply to theseus: this repo and the code repos inside it.


## Report Style


report in : [ASD-STE100 simplified technical english](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf)

- short sentences
- active voice - write "turn the switch", not "the switch must be turned"
- one idea per sentence
- use one word for one idea. do not use two words for the same thing
- no filler
- instructions max 20 words per step.

beside general conversations, use this reporting style
for code comments and commit messages.

## Commits

never commit by your self, i'll ask to prepare commits eventualy.
"stage" means `git add` only. "prepare a commit" means stage and draft the message, then stop.
commit only when i say the word "commit".


## Layout

this repo holds the shared art and docs.
each code repo has its own git and its own rules.

- `assets/` - art, blender sources, renders. git LFS tracks the binaries, see `.gitattributes`.
- `docs/` - game design, shared by the backend and the frontend.
- `backend/` - [4apaev/theseus-backend](https://github.com/4apaev/theseus-backend), rules in [backend](backend/.claude/CLAUDE.md).
- `frontend/` - [4apaev/theseus-front](https://github.com/4apaev/theseus-front), rules in [frontend](frontend/.claude/CLAUDE.md).
- `sketches/` - reference art, mostly downloaded. never commit it.

`.gitignore` excludes `backend/`, `frontend/` and `sketches/`.
never run `git clean -x` here: it deletes the code repos.

docs that follow the code (`progress.md`, `phase.*.md`, `tech.debt.md`) stay in their code repo.


## Code style

Avoid snake case names (a_b), prefer camelCase.
The code should be compact and laconic, but above all consistent.
Avoid functions with options style object arguments.
Keep functions short, shold be no more than 30 line length.
Ideal is less than 10 lines.

For more complex task preffer classes.

Check what utilities/helpers are already imported or excisting in the project
or as a dependensie before introducing new patterns.
use `garage/utils`, `garage/sync` when possible.

### Comments style

if one liner, use single line coments `//`
if multi line, use coment block `/**/`
don't mess with this style!

## Docs

- [game](docs/game.md) - the design, "the look" included
- [screens brief](docs/screens.brief.md) and its [screens](docs/screens.html)
- [client architecture](docs/architecture.client.md)
- [client style guide](frontend/docs/guide.md)
- [backend progress](backend/docs/progress.md)
- [The Theory of Interstellar Trade](docs/The.Theory.of.Interstellar.Trade.md)
