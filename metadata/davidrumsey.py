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
        Get ground control points via Oldmapsonline API.
        Args:
            external_id: str
        Returns:
            gcps: list

            All pairs of ground control points
            e.g., [{'location': , 'pixel': },{'location': , 'pixel': }, ... ]
        """


        return
