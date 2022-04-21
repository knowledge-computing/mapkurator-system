import requests
import pandas as pd


class DavidRumsey:

    def __init__(self, api_key, csv_filename):
        self.api_key = api_key
        self.csv_filename = csv_filename

        self.df = pd.read_csv(self.csv_filename)
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
            transform_method: str
                Transformation method
                e.g., "affine", "polynomial", "tps"
            gcps: list
                All pairs of ground control points
                e.g., [{'location': [-118.269356489, 34.063140276], 'pixel': [5629, 5064]},{'location': , 'pixel': }, ... ]
        """

        # 404 ERROR on many maps
        # 1. GET /maps/external/{external_id}
        # baseurl = "https://api.oldmapsonline.org/1.0/maps/external/" + external_id
        # res = requests.get(baseurl, headers=self.headers)
        map_id = self.df[self.df['external_id']==external_id]['id']

        # 2. GET /maps/{id}/georeferences
        baseurl = "https://api.oldmapsonline.org/1.0/maps/" + map_id + "/georeferences"
        res = requests.get(baseurl, headers=self.headers)

        try:
            res.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return None

        data = res.json()
        if not data['items']:
            return None
        else:
            transform_method = data['items'][0]['transformation_method']
            gcps = data['items'][0]['gcps']
            return transform_method, gcps
