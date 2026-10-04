sam · queue handoff
===================

2026-10-04

f1 and cr1 are done and wait for review.
sm1–sm9 wait for the external builds. no job remains ❎.

cleanup
-------

14 preview layouts now use paths from the theseus folder.
the preview tool reads these paths. the layout tools write these paths.
crash logs moved to assets/blender/icarus/log/.
the stale icarus failure readme is absent.
readmes that state real review needs remain.
the emitter script writes only its review need.

crew
----

assets/crew/ contains pilot.webp, engineer.webp, haggler.webp, and gunner.webp.
each portrait uses 768 × 1024 pixels.
assets/crew/preview.png shows the four portraits.
assets/crew/prompts.json contains the exact prompts and ages in ship time.
assets/crew/sources/ contains the source png files from the built-in imagegen tool.
crew-validation.json records the decoded sizes and file checks.
these are single-age tests. age variants are absent.
the game document still says no portraits. the new queue requests this test.

station models
--------------

assets/blender/scripts/paintedstations.py builds all nine kits with paintkit.py.
assets/blender/scripts/build-station-<kit>.py starts each build.
builds.txt lists the nine scripts for kick.sh.
each script saves its source in assets/blender/stations/painted/<kit>/.
each script exports to assets/exports/painted/stations/<kit>.glb.
each script renders both views in assets/blender/renders/stations/<kit>/.
each station has a berth, five deck path markers, and the parts from its kit.
the origin sits at the centre of the model bounds.
the berth bow points along +x. the glb uses metres and y up.
the render camera uses 42° azimuth and 29° elevation.

python syntax and asset path checks passed.
blender did not run in this session. no station render or glb has passed review.

next
----

kick.sh runs the listed scripts outside the codex sandbox.
on the next run, read builds.log and inspect both renders of each station.
run check-stations.py after all nine exports exist.
set each model job ✅ only after its build and render checks pass.
after three failed builds, set the job ⛔ and write the reason in its source folder.
keeton copies the exports to the client.

2026-10-04 retry check
----------------------

the nine exit-zero entries in builds.log belong to the failed first builds.
the log records the old child-list lookup error for each build.
the shared script now finds the berth by name.
kick.sh now uses --python-exit-code 1.
the nine retry scripts remain in builds.txt.
script syntax checks passed. no station exports or renders exist yet.
the external runner must finish before render review.
