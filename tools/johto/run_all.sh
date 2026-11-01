#!/bin/sh
# Full Johto regeneration in the required order (Phase 6).  usage: sh tools/johto/run_all.sh
set -e
cd "$(dirname "$0")"
python3 johto_convert.py
python3 interiors.py
python3 diglett_tunnel.py
python3 icepath.py
python3 gsc_cave.py silver tohjo dark mortar sprout burned tin dragon union slowpoke
python3 vrgate.py
python3 johto_gates.py
python3 johto_wild.py
python3 warp_audit.py
python3 check_edges.py
python3 cycling_west.py
python3 check_edges.py CyclingRoadWest Route16_Frlg ViridianCity_Frlg
