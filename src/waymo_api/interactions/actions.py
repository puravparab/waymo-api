from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from ..core.exceptions import WaymoClientError

from ..utils.logger import get_logger
logger = get_logger(__name__)

class WaymoActions:
	def __init__(self, driver, wait):
		self.driver = driver
		self.wait = wait

	def return_to_home_screen(self):
		try:
			logger.info("Returning to home screen...")
			back_button = self.wait.until(EC.element_to_be_clickable(
				(AppiumBy.ACCESSIBILITY_ID, "Back")
			))
			back_button.click()
			logger.info("Successfully returned to home screen")
		except TimeoutException as e:
			logger.error(f"Failed to return to home screen: {str(e)}")
			raise WaymoClientError("Could not return to home screen")
	
	def enter_pickup_location(self, pickup: str):
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
			self.return_to_home_screen
			raise WaymoClientError(f"Pickup location entry failed: {str(e)}")


	def enter_dropoff_location(self, dropoff: str):
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
			self.return_to_home_screen
			raise WaymoClientError(f"Dropoff location entry failed: {str(e)}")