# THOR CITY v0.5.1 — Living City Visual Engine

Built from the verified v0.4 performance baseline.

## v0.5.1
- Preserves live Thor + Mac Mini telemetry and working InstancedMesh process picking.
- Keeps the ~400-building GPU-instanced performance architecture.
- Adds a custom procedural facade shader with illuminated windows without individual window meshes.
- Adds rooftop caps, brighter city blocks, asphalt roads, parks, sparse streetlights and animated data traffic.
- Lowers the default camera toward a SimCity-style city overview.
- RAM still controls height; process category controls architectural color; CPU boosts facade intensity.
- Search, pause, city overview, FPS and inspector remain live.

Start with `python run.py`. Set `THOR_CITY_MAC_URL` as before for Mac Mini telemetry.


## v0.5.1 hotfix
- Restores vivid GPU-instanced tower bodies after the v0.5 facade shader rendered too dark.
- Preserves working InstancedMesh picking / process inspector.
- Preserves roads, parks, streetlights, rooftop caps, and animated data traffic.
- Keeps the performance-first one-draw-call tower architecture.
