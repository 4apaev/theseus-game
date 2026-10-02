# hangar fleet

14 ships and 2 police robots after the hangar paintings in
`../../hangar/ships` and `../../hangar/robots`.
`../scripts/build-hangar.py` builds them all on the shared kit
`../scripts/paintkit.py`.

| model | after | triangles | length |
| --- | --- | --- | --- |
| police-light | `ships/police-light.png` | 17,948 | 10.0 |
| police-heavy | `ships/police-heavy.png` | 23,136 | 13.1 |
| freighter | `ships/freighter.png` | 22,844 | 18.0 |
| tanker | `ships/tanker.png` | 23,980 | 18.5 |
| transport | `ships/transport.png` | 16,184 | 13.1 |
| liner | `ships/liner.png` | 25,564 | 17.3 |
| colony | `ships/colony.png` | 30,556 | 18.3 |
| research | `ships/research.png` | 11,984 | 14.0 |
| yacht | `ships/yacht.png` | 11,312 | 10.5 |
| tug | `ships/tug.png` | 15,488 | 8.7 |
| prison | `ships/prison.png` | 23,424 | 17.4 |
| corvette | `ships/corvette.png` | 7,068 | 13.8 |
| frigate | `ships/frigate.png` | 24,760 | 17.4 |
| battleship | `ships/battleship.png` | 30,268 | 21.4 |
| police-patrol | `robots/police-patrol.png` | 6,412 | 1.4 high |
| police-inspector | `robots/police-inspection.png` | 5,728 | 1.5 high |

the unit is the height of a shipping box, as in the painted fleet. the
lengths between the classes are a first choice, not a rule.

the exports are in `../../../frontend/public/models/painted/hangar/`, the
sources here as `.blend`, the previews in `../renders/hangar`.
`hangar.json` has the triangle count and the file size of each model.

## the forms

the paintings repeat a small set of forms. each is one function:

- `cab`: a faceted cab. octagon sections along x make the straight part,
  a steep windscreen and a short nose. glass wraps the brow.
- `segment` and `run`: hull blocks with 45° corners, tiled with plates,
  a dark joint in each gap.
- `pod`: an engine pod with bands, dark caps, a lamp and a drive exit.
- `tank`, `hoop`, `garden`, `dish`, `truss`, `crane`, `stall`, `house`:
  the tanks, the habitat rings, the greenhouses, the dishes, the lattice
  spines, the robot arms, the market stalls and the deck houses.

## for the client

the rules of the painted fleet apply: one mesh per material per
assembly, flat colour only, the client adds the toon light, the outline
and the grime.

- the assemblies: `hull`, `drive`, and per ship `cargo`, `claw`,
  `armament`, `habitat`, `instruments`, `deck` or `decks`. a crane is an
  assembly of its own.
- a lamp that blinks: a name with `lightbar`, `tip`, `beacon`, `nav` or
  `eye`. a police bar has `lightbar sky` and `lightbar amber` blocks. the
  client blinks them in turn.
- the radar dish of police-heavy turns: its arm has the extra `spin`.
- an empty with the extra `plume` marks each drive exit.
- a robot faces +x. its joints are `head`, `arm_l`, `arm_r`, `leg_l`
  and `leg_r`. the eyes glow.

## the colours

the kit palette, and: police blue `#2D5296`, dark blue `#213B6B`,
signal red `#B0473A`, maroon `#7A2F35`, sage `#66744E`, leaf `#4F7D3B`,
armour orange `#C2512F`.

## reproduce

```sh
blender --background --python scripts/build-hangar.py -- --output /tmp/hangar
```

add `--only <model>` to build one model, and `--no-render` to skip the
previews. the set builds in about 25 s. then copy the `.blend` files and
`hangar.json` here, the `.glb` files to the client, the `.png` files to
`../renders/hangar`.
