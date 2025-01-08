from datetime import datetime
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def search_waymo_trip(pickup, dropoff, timeout=20):
	print("Starting...")
	
	options = UiAutomator2Options()
	options.platform_name = 'Android'
	options.device_name = 'emulator-5554'
	options.app_package = 'com.waymo.carapp'
	options.app_activity = 'com.google.android.apps.car.carapp.LaunchActivity'
	options.no_reset = True

	try:
		print("Connecting to Appium...")
		driver = webdriver.Remote('http://localhost:4723', options=options)
		wait = WebDriverWait(driver, timeout)
		print("Connected!")
		
		state = driver.query_app_state(options.app_package)
		if state > 1:  # 2,3,4 means app is running in some form
			print("App is running, terminating it...")
			driver.terminate_app(options.app_package)
			wait.until(lambda x: driver.query_app_state(options.app_package) <= 1)

		print("Launching Waymo app...")
		driver.activate_app(options.app_package)
		
		# Wait for and click the search box
		print("Clicking search box...")
		search_box = wait.until(EC.presence_of_element_located(
			(AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'Where to')]")
		))
		search_box.click()
		
		# Wait for and type the dropoff destination
		print(f"Typing dropoff destination: {dropoff}")
		search_input = wait.until(EC.presence_of_element_located(
			(AppiumBy.ID, "com.waymo.carapp:id/input_text_dropoff")
		))
		search_input.send_keys(dropoff)

		# Wait for any clickable result in the list
		print("Selecting dropoff location...")
		try:
			# First try by location_title
			result = wait.until(EC.presence_of_element_located((
				AppiumBy.XPATH,
				"//android.widget.LinearLayout[@clickable='true'][.//android.widget.TextView[@resource-id='com.waymo.carapp:id/location_title']][1]"
			)))
		except:
			# Fallback to just taking the first clickable result
			result = wait.until(EC.presence_of_element_located((
				AppiumBy.XPATH,
				"//android.widget.LinearLayout[@clickable='true'][1]"
			)))

		result.click()
		print(f"Selected dropoff: {dropoff}")
		
		# After selecting dropoff location
		print("Looking for pickup entry...")
		try:
			# Wait for and click on the pickup waypoint
			pickup_waypoint = wait.until(EC.presence_of_element_located(
				(AppiumBy.XPATH, "//android.widget.FrameLayout[@content-desc[contains(., 'pickup')]]")
			))
			pickup_waypoint.click()
			print("Clicked pickup entry")

			# Wait for and enter pickup location
			print(f"Typing pickup location: {pickup}")
			pickup_input = wait.until(EC.presence_of_element_located(
				(AppiumBy.ID, "com.waymo.carapp:id/input_text_pickup")
			))
			pickup_input.clear()  # Clear any existing text
			pickup_input.send_keys(pickup)  # Just send the pickup location string

			# Wait for any clickable result in the list
			print(f"Selecting {pickup} from results...")
			result = wait.until(EC.presence_of_element_located((
				AppiumBy.XPATH,
				"//android.widget.LinearLayout[@clickable='true'][.//android.widget.TextView[@resource-id='com.waymo.carapp:id/location_title']][1]"
			)))
			result.click()
			print(f"Selected pickup: {pickup}")

		except TimeoutException as e:
			print(f"Timeout during pickup selection process: {e}")
			raise e

		# Extract trip information using more general selectors
		try:
			# Wait for and get pickup wait time
			pickup_wait = wait.until(EC.presence_of_element_located(
				(AppiumBy.XPATH, "//android.widget.TextView[@text='PICKUP']/following-sibling::android.widget.ViewSwitcher//android.widget.TextView[@resource-id='com.waymo.carapp:id/eta_text']")
			)).text
			if not pickup_wait.isdigit():
				pickup_wait = ''.join(filter(str.isdigit, pickup_wait))

			# Wait for and get dropoff time
			dropoff_time = wait.until(EC.presence_of_element_located(
				(AppiumBy.XPATH, "//android.widget.TextView[@text='DROPOFF']/following-sibling::android.widget.TextView[@resource-id='com.waymo.carapp:id/eta_text']")
			)).text
			period = wait.until(EC.presence_of_element_located(
				(AppiumBy.XPATH, "//android.widget.TextView[@text='DROPOFF']/following-sibling::android.widget.TextView[@resource-id='com.waymo.carapp:id/eta_suffix']")
			)).text
			dropoff_time = f"{dropoff_time} {period}"
			
			# Wait for and get price
			price = wait.until(EC.presence_of_element_located(
				(AppiumBy.ID, "com.waymo.carapp:id/fare_estimate_text")
			)).text
			
			current_time = datetime.now().strftime("%I:%M %p PST")
			
			print("\nTrip Summary:")
			print(f"Current time: {current_time}")
			print(f"Pickup wait time: {pickup_wait} minutes")
			print(f"Estimated arrival: {dropoff_time}")
			print(f"Price: {price}")
			
		except TimeoutException as e:
			print(f"Timeout while extracting trip information: {e}")
			
		driver.quit()
		return True
			
	except Exception as e:
		print(f"""
			Error: {e}

			Make sure:
			1. Appium is running in another terminal (run 'appium')
			2. Android emulator is running
			""")
		if 'driver' in locals():
			driver.quit()
		return False
			
if __name__ == "__main__":
	search_waymo_trip("Radhaus", "Salesforce park")