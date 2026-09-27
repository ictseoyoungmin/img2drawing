# Independent simple-subject drawing task

You are a fresh, independent worker for this one drawing. Read only the current deployable img2drawing skill and public API needed to complete the request below. Do not inspect prior dogfood outputs, reviews, sessions, pilot runs, or another class's inputs. Do not use image generation for the drawing, raster painting, pixel paste, tracing, SVG/canvas authoring, or raster repair. Author the result through the current img2drawing public runtime.

Input reference: `../simple-subjects/references/plant.png`
Reference SHA-256: `98d376c8fdb5037c9e15d45b7e7c10c2360d0de4dc11b3bbb8015062975f2a5a`

## Ordinary drawing request

Please make a faithful graphite drawing of the plant, four leaves, stems, pot, and cast shadow using img2drawing. Preserve the main silhouette and visible object relationships. Finish a coherent, simple study without adding unrelated context.

## Deliverables

Save the complete canonical session from action 0 through latest, final PNG rendered from that session, action-0-through-latest GIF exported by the runtime (normally `every_n=4`), replay manifest, and run metadata in `runs/simple-subjects/`. Set `PYTHONPATH=skills/img2drawing/src` for all runtime commands. Record the session ID, package and renderer identity, reference hash, worker configuration/model as exposed in your context, export-verifier result, and hashes. Do not reconstruct session history from final coordinates. Do not edit package source.
