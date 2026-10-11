"""Hand-built OSM input checks direction, clipping and exclusion semantics."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('scaling', Path(__file__).parents[1]/'run_sofala_scaling.py')
scaling = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scaling)


def test_osm_direction_clip_and_oracles():
    nodes = [{'type':'node','id':i,'lat':0,'lon':i/100} for i in range(1,5)]
    ways = [
        {'type':'way','id':1,'nodes':[1,2],'tags':{'highway':'residential','oneway':'-1'}},
        {'type':'way','id':2,'nodes':[2,3],'tags':{'highway':'residential','junction':'roundabout'}},
        {'type':'way','id':3,'nodes':[1,3],'tags':{'highway':'residential','access':'private'}},
        {'type':'way','id':4,'nodes':[1,3],'tags':{'highway':'residential','oneway:conditional':'yes @ (Mo)'}},
        {'type':'way','id':5,'nodes':[3,4],'tags':{'highway':'residential'}},
        {'type':'way','id':6,'nodes':[1,3],'tags':{'highway':'motorway','oneway':'no'}},
    ]
    ids, arcs, _, skipped = scaling.graph_from_osm({'elements':nodes+ways},
        {'bbox_south_west_north_east':[-1,0,1,.035],'highways':['residential','motorway']})
    assert ids == [1,2,3]
    assert [a[:2] for a in arcs] == [(2,1),(2,3),(1,3),(3,1)]
    assert skipped == {'access':1,'unsupported_oneway':1,'bbox_segments':1}
    assert all(a[2] > 1000 for a in arcs)
    assert scaling.self_check() == 108
