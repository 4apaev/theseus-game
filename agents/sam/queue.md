sam · queue
================

❎ open · ♻️ taken (with time) · ✅ done, waits for review · ⛔ failed (reason in the job folder)

one job is 2 or 3 assets. the order is the order of need: the port of sol outpost comes first.

| id  | state | job                                                                                          | output                    |
|-----|-------|----------------------------------------------------------------------------------------------|---------------------------|
| k1  | ✅    | outpost kit (sol.outpost): clean the platform, structure and cargo parts of `sketches/painted-parts-v1`, add the ship pad and one back plate. | `assets/stations/outpost/` |
| p1  | ✅ | planets: earth, mars, venus. the outpost sky shows earth.                                    | `assets/planets/`         |
| k2  | ✅ | yards kit (sol.ganymede): gantry crane, hull cradle, module rack.                            | `assets/stations/yards/`  |
| p2  | ✅ | planets: jupiter, saturn, mercury.                                                           | `assets/planets/`         |
| k3  | ✅ | gate kit (sirius, ran, procyon, lalande gates): gate ring segment, beacon tower, customs booth. | `assets/stations/gate/` |
| k4  | ✅ | hub kit (mars hub, alpha exchange): market hall, container stack, cargo lift.               | `assets/stations/hub/`    |
| k5  | ✅ | lab kit (venus lab, solaris lab): dome lab, antenna array, tank farm.                       | `assets/stations/lab/`    |
| k6  | ✅ | dock kit (rama dock, bebop docks, qeng ho depot, barnards port): dry dock arm, fuel mast, warehouse. | `assets/stations/dock/` |
| k7  | ✅ | gas kit (titan ring, aegir drift): skimmer, hydrogen tanks, ring segment.                   | `assets/stations/gas/`    |
| k8  | ✅ | mine kit (mercury deep, ember station, technora corp): ore crusher, sun shield, conveyor.   | `assets/stations/mine/`   |
| k9  | ✅ | relay kit (wolf reach, rorschach watch, ross beacon, lacaille relay): relay mast, watch tower, hab can. | `assets/stations/relay/` |
| p3  | ✅ | planets: one for each of alpha centauri, barnards star, wolf.                               | `assets/planets/`         |
| p4  | ✅ | planets: one for each of sirius, ran, procyon.                                              | `assets/planets/`         |
| p5  | ✅ | planets: one for each of lalande, ross, lacaille.                                           | `assets/planets/`         |
| i1  | ✅ | exchange interior (outpost): the market hall inside. counter, goods racks, a cargo lift. spots: counter, lift. | `assets/places/exchange/outpost/` |
| s1  | ✅ | suns: G (sol, alpha centauri), K (ran), M (barnards, wolf, lalande, ross, lacaille). | `assets/suns/` |
| i2  | ✅ | rigging bay (outpost): a ship cradle under a gantry, module racks, a tool wall. the 3D ship stands on the cradle. spots: one per rack. | `assets/places/rigging/outpost/` |
| i3  | ✅ | comms office (outpost): the ansible console, a letter rack, a window to space. spots: console, rack. | `assets/places/comms/outpost/` |
| i4  | ✅ | the hold: the cargo bay inside the far treasure. a grid floor for the cargo cells, straps, the hatch. spots: hatch. | `assets/places/hold/far-treasure/` |
| s2  | ✅ | suns: A (sirius), F (procyon), a white dwarf (sirius b). | `assets/suns/` |
| m0  | ✅ | 3D, and a check of blender in the sandbox: one beam emitter dish, a part of the icarus array. | `assets/exports/painted/icarus/` |
| c1  | ✅ | icarus key art: the array at 0.05 au, close over the sun. huge in scale, a ship as small as a speck. 2 frames: wide and detail. | `assets/concepts/icarus/` |
| c2  | ✅ | the beam, look and feel: a ship on telematter inside the beam, and a ship at the beam edge as its drive falls back. 2 frames. | `assets/concepts/beam/` |
| f1  | ✅ | clean up: in every job folder, delete a readme that only says all is well, and make every path relative (`assets/...`). move `blender.crash.txt` and `build-error.txt` out of `assets/exports/`. a build script that writes an all-is-well readme stops doing it. | `assets/` |
| cr1 | ✅ | crew portraits, a test of the look: pilot, engineer, haggler, gunner. painted busts, 768 × 1024, the same light as the stations. the crew ages in ship time. | `assets/crew/` |
| sm1 | ✅ | station model, outpost (sol.outpost): a 3D model after the outpost kit. see "a station model". | `assets/exports/painted/stations/outpost.glb` |
| sm2 | ✅ | station model, yards (sol.ganymede): a 3D model after the yards kit. see "a station model". | `assets/exports/painted/stations/yards.glb` |
| sm3 | ✅ | station model, hub (sol.mars, alpha.exchange): a 3D model after the hub kit. see "a station model". | `assets/exports/painted/stations/hub.glb` |
| sm4 | ✅ | station model, lab (sol.venus, wolf.solaris): a 3D model after the lab kit. see "a station model". | `assets/exports/painted/stations/lab.glb` |
| sm5 | ✅ | station model, gate (the 4 gates): a 3D model after the gate kit. see "a station model". | `assets/exports/painted/stations/gate.glb` |
| sm6 | ✅ | station model, dock (rama, bebop, qeng ho, barnards port): a 3D model after the dock kit. see "a station model". | `assets/exports/painted/stations/dock.glb` |
| sm7 | ✅ | station model, gas (sol.titan, ran.aegir): a 3D model after the gas kit. see "a station model". | `assets/exports/painted/stations/gas.glb` |
| sm8 | ✅ | station model, mine (sol.mercury, ember, technora): a 3D model after the mine kit. see "a station model". | `assets/exports/painted/stations/mine.glb` |
| sm9 | ✅ | station model, relay (wolf reach, rorschach, ross, lacaille): a 3D model after the relay kit. see "a station model". | `assets/exports/painted/stations/relay.glb` |
| f2 | ❎    | clean up your tools: every path in `agents/sam/tools/` relative to the theseus folder, or found from the script's own place. no `/Users/...`. | `agents/sam/tools/` |
