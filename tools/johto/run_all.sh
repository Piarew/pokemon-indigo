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
python3 warp_audit.py CyclingRoadWest CyclingRoadWestGate_1F CyclingRoadWestGate_2F
python3 mtmoon_cavein.py
python3 warp_audit.py MtMoon_B1F_Frlg
python3 sea_route.py
python3 check_edges.py SeaRouteVioletWest SeaRouteVioletCentral SeaRouteVioletEast Route32 Route27 Route21_South_Frlg CinnabarIsland_Frlg
python3 warp_audit.py SeaRouteVioletWest SeaRouteVioletCentral SeaRouteVioletEast
python3 check_edges.py Route40 Route41 OlivineCity CianwoodCity
python3 warp_audit.py Route40 Route41 CianwoodCity
python3 gap_audit.py --strict --report out/gap_report.md > /dev/null && echo "gap audit: PASS (report tools/johto/out/gap_report.md)"
python3 seafoam_block.py
python3 warp_audit.py SeafoamIslands_1F_Frlg SeafoamIslands_B1F_Frlg SeafoamIslands_B2F_Frlg SeafoamIslands_B3F_Frlg SeafoamIslands_B4F_Frlg
