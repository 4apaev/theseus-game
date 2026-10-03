screens brief
================================================

a brief for the second designer. read it once, then start. the design
decisions behind it live in [game.md](game.md), in "the flight",
"the fight", "when things go wrong" and "the look".


the split
------------------------------------------------

2 designers work in parallel. each one owns one half of the game.

| half | owner | screens |
|------|-------|---------|
| **docked** | first designer | port, hold, rigging, exchange, vignette |
| **underway** | **you** | chart, system, flight, encounter, adrift |

both halves share one UI kit (below). do not invent a second one. if
the kit is missing a part, add it to your page and name it, so the
other half can adopt it.


the game in 6 lines
------------------------------------------------

theseus is a multiplayer trade game between 10 real stars. a ship
carries cargo between 23 stations. a star crossing takes years of
galaxy time and fewer years of ship time, because the ship flies at
0.6c. prices drift with stock. fights happen only inside a system, in
simultaneous turns, and they are about detection and delta-v, not
broadsides. the premise: **the ship of theseus - you replace every
module. is it still the same ship?**


the look
------------------------------------------------

**painted miniatures, a 3D ship, live space.** your painted set in
`~/Work/theseus/assets/underway` is already in this style. the painted
preview shows the rest:
https://claude.ai/artifact/KSM5fYf1LMe7nY9g2nwn6c - ask the owner to
share it with you.

- **painted parts.** everything that stands still is a painted sprite
  or plate. cream, teal, mustard, olive and rust, warm orange lights,
  navy space.
- **the ship is 3D.** the Far Treasure is one modular 3D model: toon
  light, a grime map, a dark outline. it changes when a module is
  fitted. do not paint the player's ship into a plate - leave room for
  the model.
- **one light:** a warm key from the upper left, a cool rim from the
  right.
- **one camera:** a 3/4 view. the 3D ship matches an orthographic
  camera at 42° azimuth and 29° elevation.
- **live space.** the sky is a shader: the ether glows, the stars
  blink, planets turn. for a scene in space, paint the plate without
  its sky and planet, so the shader shows through. paint a planet flat,
  at 2:1.
- **flows, not panels.** the player acts on things in the scene. a card
  opens next to the thing, and the player confirms there. ₢ runs up in
  green and down in red.
- **no portraits.** robots, not faces.
- **browser first,** desktop later. no mobile.
- **tone:** hopeful, working class, a little cozy.

### references

the painted kit, in `~/Work/theseus/sketches`:

- `painted-parts-v1/` - 12 transparent sprites: platforms, planets,
  robots, ships, cargo, buildings. `index.html` is a small composer.
- `parts-2d/` - plates with a full and an empty version: cabin, dock,
  docking, a ship cutaway. the pairs do not line up pixel for pixel, so
  use the empty one as the plate and put props on top as sprites.
- the 3D chart: https://www.overvieweffekt.com/explore/time-dilation-map
  (MIT) - orbit, drop lines, a units switch.

the painted preview already sketches 2 of your screens, the chart and
adrift. take them as a start, not as the answer.

for the layout of your half:

- `client-views-2026-09-24/` - `02-concrete-navigation.png` and
  `05-clean-isometric-combat.png` are the closest to your half. take
  the layout, not the rendering.
- `ui-families-2026-09-24/` - rigging, exchange and flight-deck panels
  in 2 UI families.
- `brachistochrone-transfer-planning.png` - a study for the plan editor.

### the UI kit

| token | value | use |
|-------|-------|-----|
| paper | `#E8DFCB` | light panel ground |
| ink | `#2A2620` | text on paper |
| char | `#1C1A17` | dark panel ground |
| cream | `#E8DFCB` | text on char |
| muted | `#8A8173` | labels, secondary numbers |
| orange | `#E8612C` | the one action, the selection |
| teal | `#3FB6A8` | your own ship, plans, navigation |
| red | `#D9483B` | contacts, threat, damage |
| beam | `#F2B134` | the Icarus beam and its range |

- **type:** lowercase monospace for all UI text. numbers use tabular
  figures. SF Mono or IBM Plex Mono.
- **panels:** square corners, radius 2px at most, a 1px border. paper or
  char, never both in one panel.
- **the frame:** a bottom tab bar - `hold · exchange · rigging · chart ·
  comms` - with a readout above it, `12,840 ₢ · 38/80`, and an `esc`
  key bottom right. see the docked page.
- **currency:** `₢`.
- **the console:** the backtick key opens a command drawer. one line of
  it may show on a screen, as in `> go procyon.ember`.


your screens
------------------------------------------------

5 screens, 16:9. put the real game data in them (sources below). a
number that does not exist in the code yet - fuel, heat, range - is an
example: mark it so.

### 1. chart

the galaxy, in 3D. 10 stars at their catalogue positions, each with a
drop line to a plane, 17 star links, and the route. the player turns
and zooms the map.

- **the beam bubble:** the Icarus array at Sol powers the fast drive
  within 7 ly - Sol, Alpha Cen (4.32 ly), Barnard's (5.95 ly). Wolf 359
  (7.80 ly) is just outside. everything else is the frontier.
- **the plan editor:** a velocity-over-time graph with 3 handles - end
  of burn (the cruise speed), flip, start of brake. the readout changes
  while a handle moves: galaxy years, ship years, fuel, capital cost,
  heat, and **where the beam ends along the path**.

### 2. system

one system from above. the star, the stations on their real orbit
radii, the in-system links. a transfer is burn → coast at the 24 km/s
cap → brake. show the gravity well: the inner orbits cost the most.
Sol is the richest case - 6 stations, 0.387 to 9.537 AU.

### 3. flight

the ship is between stations.

- the target grows ahead, size in proportion to 1 / distance. it is
  the progress bar.
- the path blinks. the stars move in parallax. the ether glows in the
  void.
- at 0.6c, aberration pushes the stars toward the direction of flight,
  and Doppler turns them blue ahead and red behind. optional, and worth
  it.
- 2 clocks: galaxy time and ship time.
- **the escape moment:** a contact appears. the screen offers escape
  options as ghost trajectories, each with its fuel cost and its new
  ETA. no sharp turns - velocity carries over.

### 4. encounter

a fight, in-system, in simultaneous turns.

- own ship in teal. contacts in red, each with an uncertainty ellipse.
- **detection:** passive heat sees a burning drive. an active radar
  ping gives a precise track, and it tells everyone where you are.
- **orders per round:** burn (a vector, no sharp turns), fire the mass
  driver (slugs are cargo - show the count from the hold), dump junk
  (jettisoned cargo becomes a debris cloud), ping, run cold, hail.
- a round timer. **standing orders** for a player who is away: pay up
  to N% of the hold, run, or fight.
- a hit lands on a module: power, cruise, maneuver, cargo, utility.

### 5. adrift

the tank is empty and the ship has no destination. make it a flow, not
a panel:

- the ship tumbles, and shards orbit it.
- a buoy drifts in with a neon advert: "stuck? call us now!". a click
  on the buoy opens the offer, with the tug's price.
- the tug arrives, takes a line and tows the ship off screen.
- **payment in kind:** cargo first, then modules, at salvage price. the
  tug never takes the hull or a bare starter rig.
- an insured ship gets the tow free.


the data
------------------------------------------------

| what | where |
|------|-------|
| stars, stations, orbit radii, links | `packages/domain/src/universe/systems.js` |
| star positions (x, y, z in parsecs) | `data/hygdata_v42.csv` - Sol, and Gl 559A, 699, 406, 244A, 144, 280A, 411, 729, 887 |
| goods - price, volume, form, category | `packages/domain/src/universe/goods.js` |
| hull, slots, modules, the starter rig | `packages/domain/src/universe/modules.js` |
| travel time for one leg | `legTime()` in `packages/domain/src/universe/space.js` |
| the whole map, as the client reads it | `GET /api/universe` |

the starter ship: 5 light slots (power1, cruise1, maneuver1, cargo1,
utility1), hold 20, 0.60c, 0.002 m/s², power 4 of 8.


what to deliver
------------------------------------------------

- **one HTML page** with the 5 screens, drawn in code - SVG, canvas,
  Three.js - at 16:9. the final art comes from an image model later.
  the mock-ups show layout, layers and the painted style.
- under each screen, 3-5 lines: what the player can touch, what data
  it reads, what the server must add.
- publish it as an artifact and send the owner the link.
- earlier pages, for context only: the 5 concepts at
  https://claude.ai/artifact/EmyMXsJJfCEFQLCf1sws1x and the bridge at
  https://claude.ai/artifact/74cq1RBHcuAt6HovWo55zZ, and the ink
  version of the docked half at
  https://claude.ai/artifact/42WJPMTc5XeE114qjNR2Dz. the look changed
  since - the amber shell is now only the console drawer, and ink gave
  way to paint.
