import polyline

from shapely import LineString
from shapely.ops import transform
from shapely import frechet_distance as shapely_frechet_distance

from pyproj import Transformer

from geopy.distance import geodesic


class similitud_services:

    def __init__(self):
        self.transformer = Transformer.from_crs(
            "EPSG:4326",
            "EPSG:3857",
            always_xy=True
        )

    def polyline_to_linestring(self, polyline_str):
        coords = polyline.decode(polyline_str)

        return LineString([
            (lng, lat)
            for lat, lng in coords
        ])

    def project_to_meters(self, line):
        return transform(
            self.transformer.transform,
            line
        )

    def calculate_frechet_distance(
        self,
        polyline1,
        polyline2
    ):

        line1 = self.polyline_to_linestring(polyline1)
        line2 = self.polyline_to_linestring(polyline2)

        line1 = self.project_to_meters(line1)
        line2 = self.project_to_meters(line2)

        return shapely_frechet_distance(
            line1,
            line2
        )

    def get_endpoints(self, polyline_str):

        coords = polyline.decode(polyline_str)

        return (
            coords[0],
            coords[-1]
        )

    def endpoint_distance(self, polyline1, polyline2):

        origen1, destino1 = self.get_endpoints(polyline1)
        origen2, destino2 = self.get_endpoints(polyline2)

        return {
            "origen": geodesic(
                origen1,
                origen2
            ).meters,

            "destino": geodesic(
                destino1,
                destino2
            ).meters
        }

    def similarity_score(
        self,
        frechet,
        origen,
        destino
    ):

        score = 100

        score -= min(frechet / 20, 40)
        score -= min(origen / 50, 30)
        score -= min(destino / 50, 30)

        return max(round(score, 2), 0)

    def compare_routes(
        self,
        polyline1,
        polyline2
    ):

        frechet = self.calculate_frechet_distance(
            polyline1,
            polyline2
        )

        endpoints = self.endpoint_distance(
            polyline1,
            polyline2
        )

        score = self.similarity_score(
            frechet,
            endpoints["origen"],
            endpoints["destino"]
        )

        return {
            "score": score,
            "frechet": round(frechet, 2),
            "origen": round(endpoints["origen"], 2),
            "destino": round(endpoints["destino"], 2)
        }