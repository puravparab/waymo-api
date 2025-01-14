from typing import Optional
import logging
from .driver import AppiumDriverManager
from interactions.actions import WaymoActions
from interactions.info import TripInfoExtractor
from .models import TripInfo
from .exceptions import WaymoClientError

from utils.logger import get_logger
logger = get_logger(__name__)

class WaymoClient:
	def __init__(self, device_name: str = 'emulator-5554', timeout: int = 5):
		self.driver_manager = AppiumDriverManager(device_name, timeout)
		self.waymo_actions = None
		self.trip_info_extractor = None

	def __enter__(self):
		self.driver_manager.connect()
		self.waymo_actions = WaymoActions(self.driver_manager.driver, self.driver_manager.wait)
		self.trip_info_extractor = TripInfoExtractor(self.driver_manager.driver, self.driver_manager.wait)
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.driver_manager.quit()

	def get_trip_info(self, pickup: str, dropoff: str) -> TripInfo:
		try:
			# Enter dropoff location in the app homepage
			self.waymo_actions.enter_dropoff_location(dropoff)

			# Then enter pickup location
			self.waymo_actions.enter_pickup_location(pickup)

			# Extract trip info
			trip_info = self.trip_info_extractor._extract_trip_info(pickup, dropoff)

			# Return to homepage
			self.waymo_actions.return_to_home_screen()
			
			return trip_info

		except Exception as e:
			self.waymo_actions.return_to_home_screen()
			raise WaymoClientError(f"Failed to get trip info: {str(e)}")