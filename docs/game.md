🚀 The Game
================

interstellar arbitrage under time delay.

a player buys goods at one station, sends a ship through relativistic transit,
and sells somewhere else. the game is a moving ledger of delayed economic facts -
which is exactly why kafka and event sourcing feel necessary rather than decorative.

core idea: [The Theory of Interstellar Trade](The.Theory.of.Interstellar.Trade.pdf)
(Krugman, 1978) - see the [summary](The.Theory.of.Interstellar.Trade.md).


### core loop

1. register → starter ship (`far treasure`) + wallet (1000 credits)
2. check market prices at the station
3. buy cargo
4. travel - ship departs, waits out relativistic transit, arrives
5. sell cargo at the destination
6. profit? only if the price gap beats the capital cost of travel time

**profit depends on:**
- purchase price / sale price
- distance and ship velocity
- common-frame travel time
- capital cost of goods in transit - `capitalCost(principal, rate, years_abs)`

ship-frame time is flavor for the ui.
profit math uses common-frame time - that is the Krugman lesson:
opportunity cost accrues in the frame of the
trading planets, not in the cargo's private little chronicle.


### travel math

```
years_abs = distance_ly / velocity          common-frame years
years_rel = years_abs * sqrt(1 - v²)        ship-frame (proper) time
game_s    = years_abs * TIME_SCALE          real seconds at the keyboard
cost      = principal * (1 + rate)^years_abs
```

### constants

owned by `@theseus/domain` (`packages/domain/src/universe.js`), each `readEnv`-backed with
the default shown - single source of truth, no service re-reads these itself:

```js
const TIME_SCALE      = 20      // 1 common-frame year = 20 game seconds
const INTEREST_RATE   = 0.05    // per common-frame year
const STARTER_CREDITS = 1000

const STARTER_SHIP = {
    name    : 'far treasure',
    stid    : 'sol.outpost',
    velocity: 0.6,              // fraction of c
    capacity: 20,
}
```

### the known universe (phase 1)

```
              4.3 ly
  sol.outpost ────── alpha.exchange
      │ ore ↑           │ grain ↑
      │ grain ↓         │ spice ↓
      │                 │
      │                 │      │
      │ 6.0 ly          │ 5.9 ly
      └───── barnards.port ────┘
              spice ↑  ore ↓
```

produce/consume triangle - every station exports one good cheap (`↑ produces`)
and craves another (`↓ consumes`), so profitable routes exist in every direction.
lives in code: [`@theseus/domain` universe.js](../backend/packages/domain/readme.md).

goods: `ore` / `grain` / `spice` - each with `price_base` and `elasticity`;
prices float on supply & demand (`price(base, stock, target, elasticity)`),
stations quote a spread - ask above bid. no fixed state prices,
no commie game here.

routes at 0.6c: sol ↔ alpha `143s`, alpha ↔ barnards `197s`, sol ↔ barnards `200s`.


### phase 1 scope

**in**: register, starter ship, travel, station markets, buy/sell, live updates.

**out** (resist the scope goblin): combat, mining, refining, factories,
player-to-player markets, ship upgrades, npc fleets, complex auth,
multiple currencies.

steps + status live in [phase.1.md](../backend/docs/phase.1.md), current work in [progress.md](../backend/docs/progress.md).


ideas - phase 2+
--------------------------------

### solar sistem
shorter routes, much more populated.
every saturn/jupiter moon big enough needs a station

- neptun/uranus - big ports, starting point for interstellar travel
- mars - major hub
- ganimed - major hub
- titan - major hub
- mercury - ore mining
- venus - bio tech / research

**built ✔** - `sol.outpost` is the gateway, plus Mercury Deep, Venus Lab,
Mars Hub, Ganymede Yards and Titan Ring. an in-system route caps the ship
at 24 km/s, so a short hop still takes game time. see
[progress.md](../backend/docs/progress.md). more moons stay an idea.

### consume/produce
station can consume/produce more then one good,
not only goods, but also services like:
- repair
- security/policing
- tech
- work force
- etc..., needs more thinking.

### station types
- trade post
- research lab
- military base
- population center
- prison barge
- agriculture
- etc...

### more economy

scheduled - see [phase.2.md](../backend/docs/phase.2.md) step 2.1.

### universe growth
`Universe.path(from, to)` dijkstra routing - scheduled, see
[phase.2.md](../backend/docs/phase.2.md) step 2.4. the stations are built. the routing is
not.


game balance
------------------------------------------------
theseus right now doesn't fell like a game, more like a simulation, (which is ok i guess).

in order to feel like a real game it need a good balance.
after most of the mechanics are implemented, the balance phase should be planed.

**scheduled** - see [phase.4.md](../backend/docs/phase.4.md) step 4.11. the sim measures
it, and an agent player gates it: the dice never haul cargo on purpose,
so every run today measures the dice and not the game.


ideas
------------------------------------------------

the game is kinda boring right now.
it needs some cool elements for player experience.

### map of the universe

navigation as a map with ship travel animation.

1. player clicks on the destination
2. travel info shown
3. confirms travel
5. travel animation starts.
6. when waiting for travle to finish, display options:
    - at least a progress bar | spining logo | load animation
    - random quotes from SIFI books/tv/movies in meantime?
    - random events occurs, like pirates, good/bad aliens encounters?
    - accidents - meteorite strike, random engine problems
    - interest graph for cargo goods
    - station stock exchange graph
    - other ideas?

### port operations

cargo load / unload animations / repairs

### ΔV mechanics

[relativistic travel calculator](https://www.overvieweffekt.com/tools/relativistic-travel-calculator)

[brachistochrone rocket calculator](https://www.overvieweffekt.com/tools/brachistochrone-rocket-calculator) - how fast could you travel between planets with continuous acceleration and deceleration? ("expanse" like)


[3d interstellar-map playground](https://www.overvieweffekt.com/tools/interstellar-map)

[3d interstellar-map github](https://github.com/kevinsutjijadi/interstellarmap)

[astronexus](https://www.astronexus.com/projects/index)


add real ΔV calculus to the game.
let player decide about accelerate + blaming + mass of fuel and mass of the ship + cargo

1. introduce `cargo` `weight` field
2. introduce `fuel` entity with `mass`, `type`, etc...

let player decide about:
- acceleration / blaming,  duration / power
- fuel / mass calculation

**the brachistochrone trajectory model - scheduled**, see
[phase.3.md](../backend/docs/phase.3.md) step 3.5, in-system travel only. the fuller
vision here - player-controlled burns, fuel mass, cargo weight - stays
an idea, not scheduled (see phase.3.md's "explicitly out"). the player-controlled
burns are now designed, in "the flight" below.

### the gravity well

`legTime()` knows distance, speed and acceleration. it does not know
that a star pulls. so the inner system is the cheapest place on the
map today. Sol Outpost to a station at 0.05 AU is a 1.29 AU hop, which
is shorter than Mars to Ganymede. physically it is the most expensive
address in the game.

one term repairs this. effective acceleration becomes `a - GM/r²`.

solar gravity against the starter ship, which pushes 0.002 m/s²:

| orbit | solar g | against the starter |
|-------|---------|---------------------|
| 0.05 AU | 2.37 m/s² | 1185x |
| 0.2 AU | 0.148 | 74x |
| 0.387 AU, Mercury | 0.0396 | 20x |
| 1.336 AU, the Outpost | 0.0033 | 1.7x |
| 5.2 AU, Ganymede | 0.00022 | 0.1x |

the radius where the star pulls as hard as the ship pushes:

| acceleration | holds station down to |
|--------------|-----------------------|
| 0.002, starter | 1.72 AU |
| 0.006, with maneuver.mk2 | 0.99 AU |
| 0.02 | 0.54 AU |
| 0.10 | 0.24 AU |

so the starter ship cannot reach Mercury under its own thrust. it gets
there today only because the arithmetic ignores the well.

**what the term buys**: the inner system gates on the drive, not on the
wallet. a new maneuver tier opens a place, and not a number on a panel.
an Icarus station at 0.05 AU asks for about 2.4 m/s², which is 3 tiers
past anything the game ships. `path()` also gains a new answer - a leg
that is impossible for this ship, rather than merely slow. the
`no route to destination` rejection already carries it.

**the caution**: every in-system leg changes, because Sol's own
stations sit between 0.387 and 9.5 AU. Mercury and Venus turn hard for
a starter ship, and the early game moves to the outer system. that is
either the best part of the idea or a balance fault. the sim answers it
first - run the dice players with the term on, and read the rejection
mix.


### fuel

the fuller ΔV vision above wants fuel with mass. 4 shapes carry it, and
they are not the same feature. pick the payload first:

1. **range** - some places need a plan. only this one changes the map.
2. **a hold tradeoff** - carry cargo, or carry fuel.
3. **stranding** - a ship that cannot pay to leave. the most
   interesting state in the list, and a rage quit with no rescue rule.

| shape | what it costs to build |
|-------|------------------------|
| **a good** with `volume`, sold everywhere | almost nothing. cargo, trades, drift and capacity already carry it, and the market prices it by scarcity. it takes hold space, so payload 2 arrives free |
| **a ship stat** with a refuel command | its own price rule, its own panel, and it reuses nothing |
| **tiers** - reaction mass everywhere, antimatter from Icarus | this is the shape that makes Icarus matter. module tiers become a fuel unlock |
| **none** - the well and the clock are the cost | zero new parts |

**spend fuel per ΔV, not per distance.** an in-system leg is a
brachistochrone burn, and `legTime()` already computes it, so the ΔV
falls out. an interstellar leg holds one speed, so it costs one boost
and one brake. a climb out of a well costs the extra above.

the ships cruise at 0.6c. the true rocket equation at that speed asks
for a mass ratio in the thousands, so full fidelity breaks the setting.
**fuel as mass** - a full tank accelerates slower - closes the loop with
the well, and it also makes every route recursive, because `path()`
must then solve for the fuel it carries. leave it out of the first
version.


### fees and taxes

the game already charges a tax, and nobody named it. `spread(px, 0.1)`
sells to the player at +10% of spot, and buys from the player at -10%.
a round trip costs **22.2% of spot** before anything else.

so a trade pays only when the destination beats the origin by more than
22%. the price curve reaches that easily - a stock ratio of 1.5 gives
ore a 1.63x price. profitable arbitrage exists. the dice players never
found it, because they buy and sell at the same station.

**a flat fee is a number someone invents. a derived fee is a
consequence of the map.**

| fee | derived from | what it makes true |
|-----|--------------|--------------------|
| docking | orbit radius, `GM/r²` | a deep well port costs energy to hold. Icarus becomes the dearest dock, for a physical reason |
| handling | cargo volume moved | bulk ore costs more to shift than spice. `volume` sits on every good, and nothing prices it |
| sales tax | the station's produces or consumes map | a consumer station subsidises a good. a producer taxes the export |

all 3 read data that exists. none asks for a new number per station.

fees repair the Icarus price without a single change to `legTime()`.
the gravity well stays the better idea, because it gates on the ship
and not on the wallet. the 2 stack: hard to reach, and dear on arrival.

**the caution**: every sim run so far ends with the players in the red
and the stations ahead - station profit +1645 against players at -936.
fees deepen a hole that is already too deep. the report's
`player_profit` and `station_profit` are the same subtraction from both
sides, so they are the gauge.


### the order

1. the gravity well. one term, no new subsystem, and it gates the map.
2. an agent player that hauls cargo on purpose, so the real margin
   becomes measurable. see [sim.md](../backend/docs/sim.md).
3. fees, set to what that margin carries.
4. the hauling classes - a hull declares which `form` it carries. the
   forms are already on every good.
5. fuel - decided: fuel is the cost of a burn. see "the flight".


### the flight and fight decisions

the topics, and where each one lands. none of it is scheduled yet.

| topic | decision | section |
|-------|----------|---------|
| npc opponents | npc first. pvp needs both players online | the fight |
| course change mid flight | yes, and it costs fuel dearly | the flight |
| interstellar controls | few: cruise speed, flip, brake | the flight |
| in-system controls | more: destination, profile, waypoints | the flight |
| fight or flight | escape options as ghost paths, with fuel and eta | the flight |
| the cost of a burn | fuel | the flight |
| drive tiers | hydrogen anywhere, the icarus beam within 7 ly | the beam |
| combat | in-system only, simultaneous turns | the fight |
| detection | heat is passive, radar is active | the fight |
| junk mining | weapons are cargo | the fight |
| losing | insurance, respawn at home or the nearest station | when things go wrong |
| adrift | the tug | when things go wrong |
| offline | standing orders | when things go wrong |
| fog of war | v1 by system, v2 by sensor range | fog of war |
| crew | traits that help a trade or a fight | crew |
| time dilation | the crew ages with you, the ports do not | the story |
| story | the ship of theseus | the story |
| the look | painted miniatures, a 3D ship, live space | the look |

the first build steps under all of it: coordinates on the wire, a
trajectory model in `packages/domain`, and a domain package that runs
in the browser. today `universe/index.js` imports `readEnv`, and
`@theseus/config` calls `process.loadEnvFile()` at import. the browser
has no `process`.


### the flight

**the server owns the plan. both sides compute the position.** a flight
plan is a list of phases: burn, coast, flip, brake. each burn has a
direction, a thrust and a duration. the position at time `t` is a pure
function of the plan, in `packages/domain`. the client and the server
run the same function, so no position crosses the wire. the server gets
an event only when a plan changes.

- **the client** plans, previews and animates.
- **the server** checks the plan against the drive and the fuel, stores
  it, resolves arrivals, and decides who sees whom.

**velocity carries over.** no sharp turn, no sudden stop. a stop takes
`v / a` seconds, and the preview shows it.

**controls:**
- **interstellar - few.** a velocity-over-time graph with 3 handles:
  end of burn (the cruise speed), flip, start of brake. the readout
  changes while a handle moves: galaxy years, ship years, fuel, capital
  cost, heat.
- **in-system - more.** destination, profile, waypoints. the burn →
  coast at 24 km/s → brake model of step 3.5 is the base.

**a course change mid flight.** a player sees a trap and must escape. a
course change is a new plan from the current position and velocity -
one event, `ship.course.changed`. it costs fuel, and physics sets the
price: a turn of θ at speed v needs `Δv = 2v·sin(θ/2)`.

| where | move | Δv |
|-------|------|----|
| in-system, at 24 km/s | stop | 24 km/s |
| | turn 90° | 34 km/s |
| | reverse | 48 km/s |
| interstellar, at 0.6c | divert 10° | 0.10c |
| | turn 90° | 0.85c, more than a whole leg |

in-system, an escape is dear but possible. interstellar, an escape is
an abort: flip early, skip the brake and fly through, or divert to a
star near the line.

**fight or flight.** a contact appears. the chart shows escape options
as ghost trajectories, each with its fuel cost and its new eta. the
ghost turns solid when the server accepts it. the escape burn is hot,
so the trap sees it.

**the cost of a burn is fuel.** slush hydrogen is already a good. fuel
grows with Δv by the rocket equation, with an exhaust velocity tuned so
a normal trip costs a normal amount. a dodge on top then costs dearly,
with no special rule. the true rocket equation at 0.6c breaks the
setting - the beam below is the reason in the fiction. the tuning goes
to [phase.4.md](../backend/docs/phase.4.md) step 4.11.

**what the model needs:**
1. coordinates - star x, y, z from the HYG file, and a station orbit
   angle beside its radius
2. vector burns
3. fuel in the hold, spent per Δv
4. a new ship state, `adrift` - velocity, and no destination


### the beam

the fast drive is the telematter drive - see "telematter drive" below.
hydrogen in the tank becomes antimatter, assembled from information the
icarus array beams from sol.

| tier | needs | works |
|------|-------|-------|
| reaction mass | hydrogen | anywhere, slow |
| telematter | hydrogen and the beam | inside the beam. 3.2g sustained, 7.9g to maneuver |

- **the beam travels at light speed.** a ship 5 ly out gets the beam 5
  years after icarus sends it. the player books the beam before the
  flight, so a telematter plan is committed. a course change leaves the
  beam, and the drive falls back to reaction mass.
- **range 5-7 ly.** at 7 ly the beam covers sol, alpha cen (4.32 ly)
  and barnard's (5.95 ly). wolf 359 (7.80 ly) is just outside. the rest
  is the frontier.
- **the range is checked along the path,** not at the destination.
  alpha → sirius leaves the beam partway, and the preview shows where.
- **players build more arrays together.** an array at sirius adds
  procyon (5.26 ly). an array at wolf 359 adds lalande (4.06 ly).
- **the beam cannot be attacked.** it is light and quantum information,
  so debris and slugs pass through it. only the array is a target, deep
  in sol's well at 0.05 AU.
- **the array defends itself** with its own beam. no police ships, no
  npc simulation, and a physical reason. an attack voids the attacker's
  insurance.

at 3.2g a ship reaches 0.6c in about 0.18 years and 0.055 ly, so a beam
leg is almost pure cruise.


### the fight

**in-system only.** an intercept at 0.6c is a lottery. fights happen
near stations and gates, and on in-system transfers.

**simultaneous turns (wego).** both sides plot their orders. the server
resolves the round and emits events. the client plays the events back.
the fight uses the flight's trajectory model: a fight is short-range
flight planning plus firing solutions.

**detection first:**
- passive heat sees a burning drive
- an active radar ping gives a precise track, and it tells everyone
  where you are
- a contact shows as an uncertainty ellipse
- running cold hides a ship, and a cold ship cannot maneuver

**weapons are cargo:**
- mass driver slugs are a good. they take hold space from profit.
- a bucket of bolts is jettisoned cargo. chinesium scrap in a crossing
  orbit becomes a debris cloud. the cloud stays as a hazard for
  everyone, and as salvage - junk mining.
- close combat is rare, because a velocity match costs Δv. most fights
  end when one side burns away, one side pays, or a slug gets lucky.

**a hit lands on a module** - power, cruise, maneuver, cargo, utility.
a hit on the hold spills goods.

**opponents: npc first.** time dilation makes 2 players rare in one
place at one time. pvp needs both players online.

**a hail** can be an ink dialogue: bluff, pay, run.

#### jettison - planned, not built

the player cannot drop cargo today. the plan, owned by market-service:

- command `cargo.jettison.requested` `{ pid, sid, gid, quantity }`,
  event `cargo.jettisoned` `{ pid, sid, gid, quantity, stid }`. a
  refusal uses `cargo.operation.rejected`.
- `POST /api/ship/:sid/cargo/jettison` `{ gid, quantity }` → 202.
- docked and in transit. v1 destroys the cargo. in transit `stid` is
  null: `sid` and the event time place the debris later, from the
  flight plan.
- open: jettison while docked - allow it, with a disposal fee later?
  and delete the unused `cargo.load.requested` and
  `cargo.unload.requested` contracts?


### when things go wrong

**losing:** insurance, and a respawn at home or at the nearest station.

**adrift:** the tank is empty and the ship has no destination.
- call the tug. it tows the ship to the nearest station, for ₢.
- no ₢: the tug takes payment in kind - cargo first, then modules, at
  salvage price.
- the tug never takes the hull or a bare starter rig, so no player is
  stuck for good.
- an insured ship gets the tow free.
- other players can bring fuel. that is a job.

**offline:** a flight takes real minutes, and the player may sleep.
standing orders cover it:
- pay (up to N% of the hold), run (up to X fuel), or fight
- in a round, a side that does not commit in time plays its standing
  order. this also covers a player who is online but away.
- v1: an offline ship meets npc encounters only

open: the standing-order defaults.


### fog of war

- **v1, no coordinates:** you see the ships in your own system - docked
  there, on a leg inside it, or on a leg to or from it. the feed
  already filters station chat by who is docked, and this is the same
  filter one level up. it also fixes `traffic`, which returns every
  ship ever (see [tech.debt.md](../backend/docs/tech.debt.md)).
- **v2, with coordinates:** sensor ranges, heat, radar.


### the story

no plot. a premise and systemic vignettes.

- **the ship of theseus.** you replace every module. is it still the
  same ship? after enough tows and insurance claims, not one original
  part is left - and the log still says *far treasure*.
- **time dilation.** the crew ages slower than every port. ansible
  letters come from people who age faster.
- **systemic vignettes** fire from game state, in ink (`inkjs`). you
  come back to ember station after 30 galaxy years. orla has retired,
  and her daughter runs the dock. ink only needs variables such as the
  years since the last visit.


### the look

the painted preview shows it all:
https://claude.ai/artifact/KSM5fYf1LMe7nY9g2nwn6c.

- **painted miniatures.** everything that stands still is a painted
  sprite or plate: platforms, buildings, crates, robots. cream, teal,
  mustard, olive and rust, warm orange lights, navy space. the kit is
  `~/Work/theseus/sketches/painted-parts-v1`.
- **the ship is 3D and modular.** a toon ramp, a grime map and a dark
  outline, lit like the sprites. each of the 5 slots has its own mount,
  and the ship changes when a module is fitted or stripped. the same
  model docks, flies, tumbles when adrift and is towed.
- **one light:** a warm key from the upper left, a cool rim from the
  right, on the sprites and on the ship.
- **one camera:** the sprites are 3/4 views. the ship sits on them
  through an orthographic camera at 42° azimuth and 29° elevation.
- **live space.** a shader draws the ether and the stars, and each star
  blinks on its own clock. a planet is a flat 2:1 map on a shader disc:
  the surface turns under a fixed light, day line and rim. clouds are a
  second map that turns faster.
- **flows, not panels.** the player acts on things in the scene - a
  building, the ship, a buoy, a star. a card opens next to the thing,
  and the player confirms there. panels stay only for the hold grid and
  the ship's numbers.
- **₢ moves.** the number runs up or down, green for money in, red for
  money out.
- **ui:** lowercase mono, paper cards and glass chips on the sky,
  orange for the action, teal for your own ship and plans, red for
  threat. no portraits: robots, not faces.
- **the hold is a grid,** diablo 2 style. volume maps to a shape - 1,
  2, 4, 6, 8 → 1×1, 2×1, 2×2, 3×2, 4×2. hull capacity sets the grid:
  the starter's 20 is 5×4. special cells show the hauling classes: tank
  cells for liquids, frost cells for chilled goods, life-support cells
  for live goods.
- **goods and modules are icons.** drag a good into the hold: its
  footprint shows green or red, and on drop a card shows the quantity
  and the total. drag a module onto a hull slot to fit it, drag the slot
  out to strip it. the module-exchange saga does both today.
- **the chart is 3D.** the stars at their catalogue positions, drop
  lines to a plane, the Icarus beam as a sphere. a switch redraws the
  map in ship years.
- **flight:** the target grows ahead as the progress bar, size in
  proportion to 1 / distance. a blinking path, star parallax, the ether
  glowing in the void. at 0.6c, aberration and Doppler show the speed.
- **the console** stays, as a drawer on the backtick key.

open: who owns the hold layout. the server should auto-pack on load and
store the cell of each stack - otherwise the client can show a hold the
server thinks has room. and stacks: one cell per stack, with a limit.

open: one scale for all art. a crate is the unit, one crate per hold
cell?

the screens: [screens.brief.md](screens.brief.md).


### orbital mechanics

let player ability to mess with orbital mechanics (kerbal space program).
in other words give user ship control,
maybe even develop some piloting skills (RPG)

#### system map
for travels inside specific star system
show interactive map with orbits.
let user play with orbital mechanics, gravity assist (KSP style).

some time mechanics needed in flight. slow `TIME_SCALSE`
so user can react to ship maneuvers & adjust ship course

1. ship burn calcs + gravity
2. ship orbit changes as a result

consider real 3d view of the system ([three.js](https://threejs.org/editor/))
needs some thinking...


### stations

station can consume / produce more then one good.
not only goods, but also services
like repair, security / policing, tech, work force etc.

**station types**:
- trade posts
- research labs/outposts
- military bases
- population centers

### player 2 player communications & ship transponders

some kind of `ansible` device that enables faster then light speed coms.
but still with delay, no instant / immediate message transfer.
btw, player should be able to see other players at least in same station

- ship traffic visible, publishing travel manifests - done ✔, see
  [phase.2.md](../backend/docs/phase.2.md) steps 2.3 and 2.4. switching off a ship's
  transponder stays open, see [permissions.md](../backend/docs/permissions.md).
- the `ansible` device itself - scheduled, see [phase.3.md](../backend/docs/phase.3.md)
  step 3.4
- player should be able to trade with other players - still an idea, not
  scheduled (phase 1 explicitly kept player-to-player markets out)

### ships name generator
every new ship gets a random name
[culture](https://en.wikipedia.org/wiki/Culture_series) style ship names
or like item nameing in diablo
or random words, up to 3,4 words for a name

**done ✔** - see [phase.3.md](../backend/docs/phase.3.md) step 3.1. [progress.md](../backend/docs/progress.md).


### crew


head hunt for best crew (nps)
pilots, engineers, etc...
each crew member should have traits.
crew effectiveness = member traits compatibility.

**decided:** traits on a few seats - haggler (a better spread), gunner
(a better hit chance), engineer (less fuel per burn). the crew ages in
ship time, not galaxy time, so they are the only people who age with
you. wages are a money sink. the vignette voices can be the crew. no
portraits.


### weapons

missiles.
railguns.
mass drivers.
lasers only for short range if any.
a spiled bucket of bolts in ship route may be fatal.

see "the fight" above: weapons are cargo, and the fight is in-system,
in simultaneous turns.


### propulsion


[fictional-but-realistic-spacecraft](https://www.secretprojects.co.uk/threads/fictional-but-realistic-spacecraft.10219/page-8)


[solar sail](https://www.nasa.gov/general/nasa-next-generation-solar-sail-boom-technology-ready-for-launch/)


#### telematter drive

the decisions - light speed, 5-7 ly, the beam cannot be attacked - are
in "the beam" above.
[actual theseus](https://www.rifters.com/blindsight/theseus.htm).

requires a dedicated propulsion station!

is propelled by an line-of-sight (LOS) antimatter-teleportation drive.

🫢 math drive 🧮


technical concepts:

1. the power source: telematter beam unlike traditional sci-fi ships
  theseus carries almost no on-board fuel.

2. the icarus array: a massive, solar-powered antimatter manufacturing facility
  orbiting close to the sol produces the required antimatter.

3. quantum teleportation: instead of shooting a physical
  stream of fuel across space, the icarus array beams tight-focus
  quantum information to theseus.

4. on-board assembly: a receiver on the ship uses this stream of information
  to instantly transmute or "assemble" local, mundane matter stored in its tanks directly into antimatter particles, generating fuel on demand.

5. performance capabilities because it does not suffer from the logistical weight
  restrictions of carrying its own fuel, theseus operates on an entirely different scale of performance:

6. unlimited range: the ship has functionally unlimited range, provided it remains within the line-of-sight broadcast range of the icarus array.

7. extreme acceleration: it can handle a sustained burn of 3.2g and execute maneuvering burns up to 7.9g, giving it blistering speed for its deep-space intercept mission.


8. hull configuration & shieldingthe mechanics of this drive drastically dictate the ship's physical appearance and operations. the engine assembly is gargantuan compared to the living quarters. the powerful magnetic fields generated by its antimatter containment systems are actively repurposed as a shield, insulating the transhuman crew from harmful cosmic radiation during transit. additionally, a bussard ramjet mechanism is utilized to sweep up interstellar hydrogen to feed its manufacturing systems.




### ship types & modules

capacity and velocity changes now belong to a physical module and
rig system, not permanent stat purchases. packaged modules are
market goods which can be bought, transported and resold; installation
checks hull slots, rates, power and whether the work may happen
in transit or requires port. the mechanics are designed in
[modules.md](../backend/docs/modules.md) and scheduled as [phase 3](../backend/docs/phase.3.md) step 3.3.

full ship classes and buying new hulls remain later work. phase 3 gives
the existing starter ship a hull profile so compatibility rules are
real rather than a collection of special-case ship names.

introduce ship classes / types / kinds

- freighter, tanker and other cargo ships
- research ship
- military, like: cruiser, frigate, corvette, etc
- exploration, research ship
- privateer, which suggests existents of states, empires and such. (somebody should give you a license to be a pirate after all)
- if there is a pirate, then - prison barge is a necessity
- repair ship
- passenger ship, a taxi, an interstellar uber). jokes aside, orbital taxi can be a thing

#### the hauling classes

one does not move liquid hydrogen in a container hold. every good now
declares a `form`, and the form says what the hold must be:

| form | the hold | goods today |
|------|----------|-------------|
| `dry` | a plain bulk hold, what every ship has | ore, grain, chips, titanium |
| `liquid` | a tanker - sealed tanks, pumps, no free surface | water, polymer, liquor, reagents |
| `gas` | cryogenic tanks, boil-off while it sits | slush hydrogen |
| `chilled` | a reefer - power for the whole voyage | vat protein |
| `live` | life support, and it dies if the power does | gene stock |

**nothing reads `form` today.** the field is in the seed and on the
wire, and every hold takes every good. this section is the mechanic it
waits for.

the shape, when it lands: a hull declares which forms it carries, or a
cargo module does. `cargo.mk1` is a dry hold. a tank module makes a
ship a tanker and gives up dry space for it. then `cargo.buy` refuses a
good the ship cannot hold, the same way `previewRig` already refuses a
module that does not fit its slot.

3 things follow, and they are the reason to do it:

1. **a ship becomes a choice.** a dry hauler and a tanker fly the same
   map and trade different goods. today every ship trades everything.
2. **the expensive goods get a gate.** reagents and liquor pay well
   because a tanker costs something. a margin nobody can reach is not
   a margin.
3. **live cargo carries risk.** power fails, and the cargo dies. that
   is the first cargo that can be lost without a pirate.

it pairs with the ship classes above - a tanker is a hull that carries
`liquid` and `gas`, and the list stops being flavour.

**the cost:** every good needs a form (done), every hull needs a list
of forms it takes, and the market has to tell a player why a buy was
refused. the refusal path already exists - `cargo.operation.rejected`
carries reasons.

do it after the gravity well and the agent player. the well makes the
map cost something; this makes the hold cost something. both are one
term against existing data, and neither needs a new service.


### exploration

give player the ability to establish new station/colony/base
form alliances and fractions

### notable sifi refs

- blindsight
- planetes (manga + tv series)
- Lem
- serenity
- cowboy bebop
- rama (Clarck)
- bobverse
- fire upon the deep
- keng ho


### ship's personal traits / characteristic

slightly randomize ship's traits
velocity, acceleration, etc


### repairs

wear comes from use, the ship wears with time.
player should invest in repairs, and care.

ships's characteristics decay with `wear`.

ship gains new trait - `wear`
degraids with time + combat damage