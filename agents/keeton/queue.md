keeton · design queue
================

keeton (claude) makes the toy look: in the client (3D, three.js) and as vector images. the user lifted the 3D pause at 06:15: client work is allowed again.
the main goal today: 2 or 3 variants of the new design.
the generator: `assets/concepts/toy/screens/make.py`, one png per screen and palette. the look: [style.md](../style.md).

❎ open · ♻️ taken (with time) · ✅ done, waits for the user · ✖ dropped

each job makes 2 to 4 design variants. a variant changes the layout or the shapes, not only the palette.

the user, 2026-10-06 06:00:
- buttons: corners of 5 to 6 px, no shine on top. (`block()` in the generator)
- the diagram screens stand on an iso plane the player turns and zooms, like the user's star birds reference (`starbirds-graph-*`). market, comms and rigging work this way now.
- market idea 1 (blocks) is dropped. idea 2 (the flow) is the base.
- colours (06:05): mild, soft pastels. meadow (soft red on green) first, then lagoon (aqua + pink), postcard (blue + red), dusk (mild purple). candy and arcade are dropped: too much contrast. render meadow for every new screen; the others when time allows.
- colours (06:20): the user likes sam's art and its colours: use them. the `toybox` palette in make.py is sampled from sam's toy frames (indigo space, coral, amber, sea green, teal, cream). the client themes: meadow, toybox, lagoon (postcard when time allows).
- verdict (19:50): meadow and lagoon are remarkable, toybox (sam's colours) is nice. port, rigging and ships need more work.
- sam paints sprites for the diagrams (`toy-sprites-diagram`, in `assets/concepts/toy/sprites/`). the generator's `sprite()` uses them when they exist.

| job | state | what |
|-----|-------|------|
| toy-ui-kit | ✅ | the kit: palette, type, buttons, chips, tabs, tool bar, counters, a card, a toast, the compass, a slider, a toggle. 4 palettes. |
| toy-rigging | ✅ | the modules on the iso plane inside the ship's outline; the reactor feeds the rest; a slot opens its drawer with the preview. 4 palettes. |
| toy-market-ideas | ✅ | the flow on the iso plane: one good, who makes it, who wants it, price and years on each route. 4 palettes. (blocks: dropped) |
| toy-comms | ✅ | the ansible net on the iso plane: letters ride the links with their landing time; the letter card; the station channel. 4 palettes. |
| toy-icons-ui | ✅ | the new icon set, ui elements (the user asks for it): flat, bright, chunky vector icons in the toy look, svg, one stroke weight, rounded ends. places (port, market, hold, nav, rigging, comms), actions (buy, sell, travel, install, remove, send, settings, menu, close, back, turn left, turn right, zoom in, zoom out), status (credits, fuel, power, cargo, time, years, distance, alert). files in `assets/icons/toy/ui/`; a sheet of all in meadow, lagoon, postcard. the client kit uses them. done: 28 icons in `assets/icons/toy/ui/svg/` (colours as `--toy-*` vars, meadow fallback), `sheet-meadow|toybox|lagoon|postcard.png`, generator `make.py`. |
| client-toy-theme | ✅ | the toy look in the client, behind `?toy` (the old places stay as they are): kit tokens in css (the palettes of `make.py`, corners 6 px, a darker lip, no shine, a rounded sans), `&theme=meadow` (default), `toybox`, `lagoon`, `postcard`. the sky takes the palette's space colour. a material named `toy-red`, `toy-green`, `toy-butter`, `toy-milk`, `toy-dark` or `toy-glow` takes its colour from the theme. |
| client-toy-market | ✅ | the market as a 3D iso plane: a grid plane, tiles, flat routes with moving dots, a small world on each tile, chips from the kit. one good at a time, a goods picker; makers and buyers from the universe (`produces`, `consumes`). the orbit camera turns and zooms, always above the plane. the 3 themes. |
| client-toy-port | ✅ | the port as a small world: sam's `assets/exports/toy/station.glb` when it exists, else the `&globe` sketch with one kit and pipes between the facilities. ships leave a trail of round puffy bubbles when they burn. a click on a facility opens its place. the 3 themes. |
| client-toy-rigging | ✅ | rigging on the iso plane: module tiles inside the ship's outline, power routes from the reactor, a slot opens the drawer card with the server's preview. the 3 themes. |
| client-toy-comms | ✅ | comms on the iso plane: stations on tiles, letters ride the links with their landing time, the letter card. the 3 themes. |
| client-toy-nav | ✅ | the chart in 3D, no plane (the user, 2026-10-06): stars as fat toy balls, dotted arcs for routes, a system with dotted orbits and small worlds. a station opens the manifest card; the course runs in red dots from the ship to a pin. `src/places/atlas.ts`. |
| client-toy-hold | ✅ | the hold as a toy box: a cell per unit of capacity, a crate, barrel or tank per cell in the colour of its kind, the icon over each good. a good opens its card. `src/places/crates.ts`. |
| client-rigging-toy | ✅ | the priority (the user, 2026-10-07): the toy bay is the only rigging. delete the old rigging and its blueprint. the ship in the bay: the toy hull, large, in its outline, a line from each socket to its slot tile. every step in the toy look: the slot card, the preview, install, remove, rename. |
| client-fix-exhaust | ✅ | the bubbles are gone: find why. puffs stay where they are blown, so a moving ship leaves a tail. sam's puff sprites in place of plain balls. |
| client-fix-log | ✅ | the log text overlaps the station box; the empty log shows as a bar. hide it when empty. |
| client-fix-tray | ✅ | the grouped dock: the swell is off and the groups clip. |
| client-comms-toy | ✅ | the comms panel in the toy look: letters as toy cards, the composer, the channel. |
| client-select | ✅ | `kit-select`: a dropdown in the toy look, for the comms channel and the settings voice. |
| client-press | ✅ | every button: a pressed state (the lip sinks) and transitions, the top menu first. |
| client-screen-transitions | ✅ | a place change animates: the scene fades and eases in, the panels slide. |
| client-labels-hover | ✅ | labels show on hover of their object or label. here, the active and the selected stay on. |
| client-skins | ✅ | skins after sam's `toy-skins`: a skin maps roles to colours; police and military are skins. a picker in the ship card; the card sends `skin` with the name (the server ignores it until it knows skins); the browser keeps it. stations wear their skins. |
| client-orbit-view | ✅ | the orbital maneuver view, after sam's `toy-orbit-frames`: a toy planet, the moon, the ship on its orbit; the player drags a maneuver node, the new orbit draws dashed, the card shows Δv, burn time, apoapsis, periapsis. client only, it does nothing on the server. |
| client-port-lagrange | ✅ | the port shows its planet; the dry dock and the gas station at L1 to L3 between the station and the planet, after sam's `toy-stations-lagrange`. |
| client-new-ships | ✅ | sam's new ships and stations into the fleet as they land: sync, lengths in `HULLS`, the towed loads behind their tugs. |
| client-toy-themes | ⏸ | later, on the user's word: every palette as a theme in the settings card, saved like the voice. |
| toy-market-more | ✅ | 2 more market variants on the iso plane: all goods at once (each station tile shows its best buy and sell as small stacks); and the flow with the player's ship on a route, the trade card beside the ship. done: `market-all-*.png`, `market-ship-*.png` in meadow, toybox, lagoon. |
| toy-rigging-variants | ⏸ | 2 more rigging variants on the iso plane: the ship cut open, each module in its bay; and the modules as a tree from the reactor, the candidates for a slot fanned out beside it. |
| toy-nav-diagram | ⏸ | the route on the iso plane, for the manifest: stops as numbered tiles on a path, the ship on its tile, a manifest card (cargo, stops, time, cost of the wait). 2 variants. |
| toy-comms-variants | ⏸ | 2 more comms variants on the iso plane: a radial net round the player's station; letters as paper planes on the routes. |
| toy-ui-kit-shapes | ⏸ | 2 more kit variants, corners 5 to 6 px, no shine: flat blocks with a thick outline; and blocks with a deep lip, like toy bricks. |
| toy-review-sheet | ⏸ | the evening sheet for the user: contact sheets of every toy image (sam's and keeton's), grouped by subject, in `assets/concepts/toy/review/`, and `assets/concepts/toy/readme.md`: one line per image. |
