import pytz
import logging
from dateutil import parser
from datetime import datetime, timedelta

from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from ..core.models import TripInfo
from ..core.exceptions import WaymoClientError

from ..utils.logger import get_logger
logger = get_logger(__name__)

class TripInfoExtractor:
	def __init__(self, driver, wait):
		self.driver = driver
		self.wait = wait

	def _normalize_datetime(self, time_str: str, period: str, base_datetime: datetime, tz: pytz.timezone) -> datetime:
		# Parse the time with AM/PM
		parsed_time = parser.parse(f"{time_str} {period}")
		# Create a new datetime with the parsed time
		normalized_datetime = tz.localize(
			datetime.combine(
				base_datetime.date(),
				parsed_time.time()
			)
		)
		# If the normalized time is earlier than the base time, it must be next day
		if normalized_datetime < base_datetime:
			normalized_datetime += timedelta(days=1)
		return normalized_datetime

	def _calculate_trip_duration(self, pickup: datetime, dropoff: datetime) -> int:
		return round((dropoff - pickup).total_seconds() / 60)

	def _extract_trip_info(self, pickup: str, dropoff: str) -> TripInfo:
		"""Extract trip information from the app"""
		try:
			city = "SF" # temporary
			tz = pytz.timezone('America/Los_Angeles')
			current_datetime = tz.localize(datetime.now())

			# Get pickup wait time
			pickup_wait = self.wait.until(EC.presence_of_element_located(
				(AppiumBy.XPATH, "//android.widget.TextView[@text='PICKUP']/following-sibling::android.widget.ViewSwitcher//android.widget.TextView[@resource-id='com.waymo.carapp:id/eta_text']")
			)).text
			wait_minutes = int(''.join(filter(str.isdigit, pickup_wait)))

			# Get dropoff time
			dropoff_time = self.wait.until(EC.presence_of_element_located(
				(AppiumBy.XPATH, "//android.widget.TextView[@text='DROPOFF']/following-sibling::android.widget.TextView[@resource-id='com.waymo.carapp:id/eta_text']")
			)).text
			period = self.wait.until(EC.presence_of_element_located(
				(AppiumBy.XPATH, "//android.widget.TextView[@text='DROPOFF']/following-sibling::android.widget.TextView[@resource-id='com.waymo.carapp:id/eta_suffix']")
			)).text
			dropoff_time = f"{dropoff_time}"

			# Get price
			price_str = self.wait.until(EC.presence_of_element_located(
				(AppiumBy.ID, "com.waymo.carapp:id/fare_estimate_text")
			)).text
			price_value = float(price_str.replace('$', ''))

			# Calculate pickup time (current time + wait time)
			pickup_datetime = current_datetime + timedelta(minutes=wait_minutes)
			# Process dropoff time
			dropoff_datetime = self._normalize_datetime(dropoff_time, period, pickup_datetime, tz)
			# Calculate trip duration
			trip_duration = self._calculate_trip_duration(pickup_datetime, dropoff_datetime)

			# Format times for output
			current_time_24hr = current_datetime.strftime('%H:%M')
			pickup_time_24hr = pickup_datetime.strftime('%H:%M')
			dropoff_time_24hr = dropoff_datetime.strftime('%H:%M')

			# Get dates
			current_date_str = current_datetime.strftime('%m/%d/%Y')
			pickup_date_str = pickup_datetime.strftime('%m/%d/%Y')
			dropoff_date_str = dropoff_datetime.strftime('%m/%d/%Y')

			trip_info = {
				"city": city,
				"current_datetime": {
					"value": current_time_24hr,
					"time_zone": "PST",
					"date": current_date_str
				},
				"price": {
					"value": price_value,
					"currency": "USD"
				},
				"pickup": {
					"location": {
						"address": pickup,
						"city": city
					},
					"pickup_time": pickup_time_24hr,
					"wait_time": wait_minutes,
					"time_zone": "PST",
					"date": pickup_date_str
				},
				"dropoff": {
					"location": {
						"address": dropoff,
						"city": city
					},
					"dropoff_time": dropoff_time_24hr,
					"time_zone": "PST",
					"date": dropoff_date_str
				},
				"duration": trip_duration
			}

			logger.info(f"Successfully extracted trip info: {trip_info}")
			return trip_info

		except TimeoutException as e:
			logger.error(f"Timeout while extracting trip information: {str(e)}")
			raise WaymoClientError(f"Failed to extract trip information: {str(e)}")