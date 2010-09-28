#!/usr/bin/python

import os, sys
from django.contrib.gis.utils import LayerMapping
from colonialismdb.common.models import BaseGeo, GeoPoint, GeoPolygon, geopoint_mapping, geopolygon_mapping


def run(colgeo_shp_pt, colgeo_shp_py, verbose=True):
    lm_pt = LayerMapping(GeoPoint, colgeo_shp_pt, geopoint_mapping, transform=False)
    lm_pt.save(strict=True, verbose=verbose)

    lm_py = LayerMapping(GeoPolygon, colgeo_shp_py, geopolygon_mapping, transform=False)
    lm_py.save(strict=True, verbose=verbose)

if __name__ == "__main__":
  colgeo_shp_pt = sys.argv[1] #os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/TM_WORLD_BORDERS-0.3.shp'))
  colgeo_shp_py = sys.argv[2]
  run(colgeo_shp_pt, colgeo_shp_py)
