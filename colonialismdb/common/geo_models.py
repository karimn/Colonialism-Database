# This is an auto-generated Django model module created by ogrinspect.
from django.contrib.gis.db import models

class BaseGeo(models.Model):
    ft_id = models.IntegerField(unique = True)
    point_x = models.FloatField()
    point_y = models.FloatField()

    srid = 4326

    objects = models.GeoManager()

class GeoPoint(BaseGeo):
    geom = models.PointField(srid=BaseGeo.srid)

class GeoPolygon(BaseGeo):
    shape_leng = models.FloatField()
    shape_area = models.FloatField()
    geom = models.PolygonField(srid=BaseGeo.srid)

# Auto-generated `LayerMapping` dictionary for GeoPoint model
geopoint_mapping = {
    'point_x' : 'POINT_X',
    'point_y' : 'POINT_Y',
    'ft_id' : 'FT_ID',
    'geom' : 'POINT',
}

# Auto-generated `LayerMapping` dictionary for GeoPolygon model
geopolygon_mapping = {
    'shape_leng' : 'SHAPE_Leng',
    'shape_area' : 'SHAPE_Area',
    'point_x' : 'POINT_X',
    'point_y' : 'POINT_Y',
    'ft_id' : 'FT_ID',
    'geom' : 'POLYGON',
}
