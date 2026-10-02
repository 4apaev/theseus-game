# model sources

editable blender sources and their build scripts live here. the client
serves the exported `.glb` files from `../../frontend/public/models/`.
the reference board is `../../sketches/`, the model renders are in
`renders/`.

```text
blender/
    stations/
        lem/lem-station.blend                       the observatory outpost
        many-hands/port-of-many-hands.blend         the system gateway
    parts/reactor-mk02.blend                        a module study, not shipped
    civil/          liner, prison-barge, sunday-catch, transport, wandering-ward, yacht
    industrial/     freighter, tanker, terraforming-ark, tug
    military/       battleship, corvette, frigate
    research/       survey, vessels
    fleet-expansion/manifest.json                   mesh counts of the fleet build
    painted/        the painted fleet: far treasure, modules, npc ships, robots, containers
    hangar/         the hangar fleet: 14 ships and 2 police robots after ../hangar
    scripts/        the build scripts. paintkit.py is the shared kit of the painted look
    renders/        model previews
```

the civil, industrial, military and research folders hold the older
ship studies. the [painted fleet](painted/readme.md) and the
[hangar fleet](hangar/readme.md) are in the current look.

## stations

2 station models, one runtime contract, built by
`scripts/build-lem-assets.py` and `scripts/build-port-of-many-hands.py`
on the shared `scripts/stationkit.py`:

- [lem station](stations/lem/readme.md): the observatory outpost.
- [port of many hands](stations/many-hands/readme.md): the system gateway.

the client's `src/render/lem-station.ts` maps a station id to a model and loads its
glb in the port view.

## export convention

- export each hull as `frontend/public/models/<category>/<hull>.glb`.
- keep a consistent scale, origin, and forward direction across models:
  blender z up, bow +x; glb y up, bow +x. roots sit at the ship spine.
- keep selectable assemblies separate and name them `cargo`, `drive`, and
  `comms`. the loader maps `comms` to the `ansible` module id.
- use named empty objects for attachment sockets.
- keep preview lights and cameras out of the game asset export.

## ship studies

[the ship studies](ship-studies.md) describe the hull sources, their
palettes, exports and preview renders, and how to reproduce them with
`scripts/build-ship-studies.py`, `scripts/build-wandering-ward.py`,
`scripts/build-fleet-classes.py` and `scripts/build-fleet-expansion.py`.
the client's `src/model.ts` lists the hulls the catalog previews.
