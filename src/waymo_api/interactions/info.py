import logging
from datetime import datetime

from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from core.models import TripInfo
from core.exceptions import WaymoClientError

from utils.logger import get_logger
logger = get_logger(__name__)

class TripInfoExtractor:
	def __init__(self, driver, wait):
		self.driver = driver
		self.wait = wait

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
			raise WaymoClientError(f"Failed to extract trip information: {str(e)}")