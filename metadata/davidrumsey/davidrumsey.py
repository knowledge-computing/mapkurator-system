import requests

class DavidRumsey():
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            'Authorization': self.api_key,
            'Content-Type': 'application/json',
            'charset': 'utf-8'
            }

    def get_ground_control_points(self, external_id):
        """
        Get ground control points of map image via Oldmapsonline API.
        Args:
            external_id: str
        Returns:
            gcps: list

            All pairs of ground control points
            e.g., [{'location': [-118.269356489, 34.063140276], 'pixel': [5629, 5064]},{'location': , 'pixel': }, ... ]
        """

        # 404 ERROR on many maps
        # 1. GET /maps/external/{external_id}
        # baseurl = "https://api.oldmapsonline.org/1.0/maps/external/" + external_id
        # res = requests.get(baseurl, headers=self.headers)

        # 2. GET /maps/{id}/georeferences
        # baseurl = "https://api.oldmapsonline.org/1.0/maps/" + map_id + "/georeferences"
        # res = requests.get(baseurl, headers=self.headers)

        

        return
