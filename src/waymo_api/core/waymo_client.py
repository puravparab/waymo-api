import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)

@dataclass
class TripInfo:
	pickup_location: str
	pickup_wait_time: str
	dropoff_location: str
	dropoff_time: str
	current_time: str
	time_zone: str
	price: str
	currency: str

class WaymoClientError(Exception):
	"""Base exception for WaymoClient errors"""
	pass

class WaymoClient:
	def __init__(self, device_name: str = 'emulator-5554', timeout: int = 20):
		self.platform_name = 'Android'
		self.device_name = device_name
		self.timeout = timeout
		self.driver = None
		self.wait = None
		self.app_package = 'com.waymo.carapp'
		self.app_activity = 'com.google.android.apps.car.carapp.LaunchActivity'

	def _setup_driver(self) -> UiAutomator2Options:
		"""Configure and return Appium driver options"""
		options = UiAutomator2Options()
		options.platform_name = self.platform_name
		options.device_name = self.device_name
		options.app_package = self.app_package
		options.app_activity = self.app_activity
		options.no_reset = True
		return options

	def _connect_to_appium(self):
		"""Establish connection to Appium server"""
		try:
			logger.info("Connecting to Appium...")
			options = self._setup_driver()
			self.driver = webdriver.Remote('http://localhost:4723', options=options)
			self.wait = WebDriverWait(self.driver, self.timeout)
			logger.info("Connected successfully to Appium")
		except Exception as e:
			logger.error(f"Failed to connect to Appium: {str(e)}")
			raise WaymoClientError(f"Appium connection failed: {str(e)}")
	
	def _handle_app_state(self):
		"""Handle the Waymo app state (terminate if running, then launch)"""
		try:
			logger.info("Launching Waymo app...")
			self.driver.activate_app(self.app_package)
		except Exception as e:
			logger.error(f"Failed to handle app state: {str(e)}")
			raise WaymoClientError(f"App state handling failed: {str(e)}")

	def __enter__(self):
		"""Context manager enter method"""
		self._connect_to_appium()
		self._handle_app_state()
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		"""Context manager exit method"""
		try:
			if self.driver:
				self.driver.quit()
		except Exception as e:
			logger.error(f"Error closing driver: {str(e)}")
			raise WaymoClientError(f"Failed to close driver: {str(e)}")

	def _enter_pickup_location(self, pickup: str):
		"""Enter and select pickup location"""
		try:
			logger.info("Looking for pickup entry...")
			pickup_waypoint = self.wait.until(EC.presence_of_element_located(
				(AppiumBy.XPATH, "//android.widget.FrameLayout[@content-desc[contains(., 'pickup')]]")
			))
			pickup_waypoint.click()
			logger.info("Clicked pickup entry")

			logger.info(f"Typing pickup location: {pickup}")
			pickup_input = self.wait.until(EC.presence_of_element_located(
				(AppiumBy.ID, "com.waymo.carapp:id/input_text_pickup")
			))
			pickup_input.clear()
			pickup_input.send_keys(pickup)

			logger.info(f"Selecting {pickup} from results...")
			result = self.wait.until(EC.presence_of_element_located((
				AppiumBy.XPATH, "//android.widget.LinearLayout[@clickable='true'][.//android.widget.TextView[@resource-id='com.waymo.carapp:id/location_title']][1]"
			)))
			result.click()
			logger.info(f"Selected pickup: {pickup}")

		except TimeoutException as e:
			logger.error(f"Timeout during pickup selection: {str(e)}")
			self._app_home_screen()
			raise WaymoClientError(f"Pickup location entry failed: {str(e)}")


	def _enter_dropoff_location(self, dropoff: str):
		"""Enter and select dropoff location"""
		try:
			logger.info("Clicking search box...")
			search_box = self.wait.until(EC.presence_of_element_located(
				(AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'Where to')]")
			))
			search_box.click()

			logger.info(f"Typing dropoff destination: {dropoff}")
			search_input = self.wait.until(EC.presence_of_element_located(
				(AppiumBy.ID, "com.waymo.carapp:id/input_text_dropoff")
			))
			search_input.send_keys(dropoff)

			logger.info("Selecting dropoff location...")
			try:
				result = self.wait.until(EC.presence_of_element_located((
					AppiumBy.XPATH, "//android.widget.LinearLayout[@clickable='true'][.//android.widget.TextView[@resource-id='com.waymo.carapp:id/location_title']][1]"
				)))
			except TimeoutException:
				result = self.wait.until(EC.presence_of_element_located((
					AppiumBy.XPATH, "//android.widget.LinearLayout[@clickable='true'][1]"
				)))
			result.click()
			logger.info(f"Selected dropoff: {dropoff}")

		except TimeoutException as e:
			logger.error(f"Timeout during dropoff selection: {str(e)}")
			self._app_home_screen()
			raise WaymoClientError(f"Dropoff location entry failed: {str(e)}")

	def _enter_locations(self, pickup: str, dropoff: str):
		"""Enter both pickup and dropoff locations"""
		self._enter_dropoff_location(dropoff)
		self._enter_pickup_location(pickup)

	def _extract_trip_info(self, pickup: str, dropoff: str) -> TripInfo:
		"""Extract trip information from the app"""
		try:
			# Get pickup wait time
			pickup_wait = self.wait.until(EC.presence_of_element_located(
				(AppiumBy.XPATH, "//android.widget.TextView[@text='PICKUP']/following-sibling::android.widget.ViewSwitcher//android.widget.TextView[@resource-id='com.waymo.carapp:id/eta_text']")
			)).text
			if not pickup_wait.isdigit():
				pickup_wait = ''.join(filter(str.isdigit, pickup_wait))

			# Get dropoff time
			dropoff_time = self.wait.until(EC.presence_of_element_located(
				(AppiumBy.XPATH, "//android.widget.TextView[@text='DROPOFF']/following-sibling::android.widget.TextView[@resource-id='com.waymo.carapp:id/eta_text']")
			)).text
			period = self.wait.until(EC.presence_of_element_located(
				(AppiumBy.XPATH, "//android.widget.TextView[@text='DROPOFF']/following-sibling::android.widget.TextView[@resource-id='com.waymo.carapp:id/eta_suffix']")
			)).text
			dropoff_time = f"{dropoff_time} {period}"

			# Get price
			price = self.wait.until(EC.presence_of_element_located(
				(AppiumBy.ID, "com.waymo.carapp:id/fare_estimate_text")
			)).text

			current_time = datetime.now().strftime("%I:%M %p PST")

			trip_info = TripInfo(
				pickup_location=pickup,
				pickup_wait_time=f"{pickup_wait} minutes",
				dropoff_location=dropoff,
				dropoff_time=dropoff_time,
				current_time=current_time,
				time_zone="PST",
				price=price,
				currency="$"
			)

			logger.info(f"Successfully extracted trip info: {trip_info}")
			return trip_info

		except TimeoutException as e:
			logger.error(f"Timeout while extracting trip information: {str(e)}")
			self._app_home_screen()
			raise WaymoClientError(f"Failed to extract trip information: {str(e)}")

	def _app_home_screen(self):
		"""Ensure we're on the app home screen"""
		try:
			logger.info("")
			back_button = self.wait.until(EC.element_to_be_clickable(
				(AppiumBy.ACCESSIBILITY_ID, "Back")
			))
			back_button.click()
			logger.info("Clicked back button")
			return
		except Exception as e:
			logger.error(f"Error returning to app home screen: {str(e)}")
			raise WaymoClientError(f"Failed to return app home screen: {str(e)}")

	def get_trip_info(self, pickup: str, dropoff: str) -> TripInfo:
		try:
			self._enter_locations(pickup, dropoff)
			trip_info = self._extract_trip_info(pickup, dropoff)
			self._app_home_screen()
			return trip_info
		except Exception as e:
			logger.error(f"Error getting trip info: {str(e)}", exc_info=True)
			self._app_home_screen()
			raise WaymoClientError(f"Failed to get trip info: {str(e)}")