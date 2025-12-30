# Copyright (c) 2023, Qunatbit and contributors
# For license information, please see license.txt
import frappe
import requests
import json
from frappe.model.document import Document

class EmployeeLocation(Document):
	def validate(self):
		self.calculate_distance()

	def set_map_location(self, coordinates=None):
		location_list = coordinates
		if location_list is None:
			location_list = [[lng, lat] for lng, lat in self._get_point_list()]

		if not location_list:
			self.my_location = None
			return

		map_json = {
			"type": "FeatureCollection",
			"features": [
				{
					"type": "Feature",
					"properties": {},
					"geometry": {
						"type": "LineString",
						"coordinates": location_list,
					},
				},
				{
					"type": "Feature",
					"properties": {},
					"geometry": {
						"type": "Point",
						"coordinates": location_list[0],
					},
				},
			],
		}

		self.my_location = json.dumps(map_json)

	@frappe.whitelist()
	def calculate_distance(self):
		points = self._get_point_list()
		get_length = len(points)
		if get_length == 1:
			self.set_map_location()
			return

		if get_length >= 2:
			start_lng, start_lat = points[-2]
			end_lng, end_lat = points[-1]
			api_key = '1cfcdeaf26352898f9975a577da9fd30'
			headers = {'accept': 'application/json'}
			distance_km = self._get_distance_km_from_route_coords(
				api_key, start_lng, start_lat, end_lng, end_lat, headers
			)
			if distance_km is None:
				distance_km = self._get_distance_km_from_matrix_coords(
					api_key, start_lng, start_lat, end_lng, end_lat, headers
				)

			if distance_km is not None:
				self.distance = (self.distance or 0) + float(distance_km)

			route_coordinates = self._build_route_coordinates(api_key, headers, points)
			if route_coordinates:
				self.set_map_location(route_coordinates)
			else:
				self.set_map_location()

	def _get_distance_km_from_route_coords(
		self, api_key, start_lng, start_lat, end_lng, end_lat, headers
	):
		route = self._get_route(api_key, start_lng, start_lat, end_lng, end_lat, headers)
		if not route:
			return None

		distance_meters = route.get("distance")
		if distance_meters is None:
			return None

		return float(distance_meters) / 1000.0

	def _get_route(self, api_key, start_lng, start_lat, end_lng, end_lat, headers):
		url = (
			f"https://apis.mappls.com/advancedmaps/v1/{api_key}/route_adv/driving/"
			f"{start_lng},{start_lat};"
			f"{end_lng},{end_lat}"
		)
		params = {
			"geometries": "polyline",
			"overview": "full",
		}
		response = requests.get(url, headers=headers, params=params, timeout=10)
		if response.status_code != 200:
			return None

		response_data = response.json()
		if response_data.get("routes"):
			return response_data["routes"][0]
		if response_data.get("route"):
			return response_data["route"]

		return None

	def _get_distance_km_from_matrix_coords(
		self, api_key, start_lng, start_lat, end_lng, end_lat, headers
	):
		url = (
			f"https://apis.mappls.com/advancedmaps/v1/{api_key}/distance_matrix/driving/"
			f"{start_lng},{start_lat};"
			f"{end_lng},{end_lat}?rtype=0&region=IND"
		)
		response = requests.get(url, headers=headers, timeout=10)
		if response.status_code != 200:
			return None

		response_data = response.json()
		distances = response_data.get("results", {}).get("distances")
		if not distances or not distances[0]:
			return None

		return float(distances[0][1]) / 1000.0

	def _build_route_coordinates(self, api_key, headers, points):
		if len(points) < 2:
			return None

		route_coordinates = []
		for index in range(len(points) - 1):
			start_lng, start_lat = points[index]
			end_lng, end_lat = points[index + 1]
			segment_coordinates = self._get_route_coordinates(
				api_key, start_lng, start_lat, end_lng, end_lat, headers
			)
			if not segment_coordinates:
				segment_coordinates = [
					[start_lng, start_lat],
					[end_lng, end_lat],
				]

			if route_coordinates and segment_coordinates:
				if route_coordinates[-1] == segment_coordinates[0]:
					route_coordinates.extend(segment_coordinates[1:])
				else:
					route_coordinates.extend(segment_coordinates)
			else:
				route_coordinates.extend(segment_coordinates)

		return route_coordinates

	def _get_route_coordinates(self, api_key, start_lng, start_lat, end_lng, end_lat, headers):
		route = self._get_route(api_key, start_lng, start_lat, end_lng, end_lat, headers)
		if not route:
			return None

		geometry = route.get("geometry")
		if isinstance(geometry, dict):
			coordinates = geometry.get("coordinates")
			if coordinates:
				return coordinates
		if isinstance(geometry, list):
			return geometry

		polyline_value = geometry
		if not polyline_value:
			polyline_value = route.get("polyline")
		if isinstance(polyline_value, dict):
			polyline_value = polyline_value.get("points")

		if isinstance(polyline_value, str) and polyline_value:
			decoded = self._decode_polyline(polyline_value)
			return [[lng, lat] for lat, lng in decoded]

		return None

	def _decode_polyline(self, polyline_str):
		index = 0
		lat = 0
		lng = 0
		coordinates = []

		while index < len(polyline_str):
			shift = 0
			result = 0
			while True:
				b = ord(polyline_str[index]) - 63
				index += 1
				result |= (b & 0x1f) << shift
				shift += 5
				if b < 0x20:
					break
			delta_lat = ~(result >> 1) if (result & 1) else (result >> 1)
			lat += delta_lat

			shift = 0
			result = 0
			while True:
				b = ord(polyline_str[index]) - 63
				index += 1
				result |= (b & 0x1f) << shift
				shift += 5
				if b < 0x20:
					break
			delta_lng = ~(result >> 1) if (result & 1) else (result >> 1)
			lng += delta_lng

			coordinates.append((lat / 1e5, lng / 1e5))

		return coordinates

	def _get_point_list(self):
		points = []
		for location in self.location_table or []:
			lng = self._to_float(location.longitude)
			lat = self._to_float(location.latitude)
			if lng is None or lat is None:
				continue
			points.append((lng, lat))
		return points

	def _to_float(self, value):
		if value is None:
			return None
		if isinstance(value, (int, float)):
			return float(value)
		if isinstance(value, str):
			value = value.strip()
			if not value:
				return None
			try:
				return float(value)
			except ValueError:
				return None
		return None
				
