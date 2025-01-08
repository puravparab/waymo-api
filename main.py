import time
from datetime import datetime
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

def search_waymo_trip(pickup, dropoff):
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
		print("Connected!")
		
		state = driver.query_app_state(options.app_package)
		if state > 1:  # 2,3,4 means app is running in some form
			print("App is running, terminating it...")
			driver.terminate_app(options.app_package)
			time.sleep(2)

		print("Launching Waymo app...")
		driver.activate_app(options.app_package)
		time.sleep(6)
		
		# Click the search box
		print("Clicking search box...")
		search_box = driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'Where to')]")
		search_box.click()
		time.sleep(2)
		
		# Type the dropoff destination
		print(f"Typing dropoff destination: {dropoff}")
		search_input = driver.find_element(AppiumBy.ID, "com.waymo.carapp:id/input_text_dropoff")
		search_input.send_keys(dropoff)
		time.sleep(3)
		
		# Click the first result that matches dropoff
		print("Selecting dropoff location...")
		first_result = driver.find_element(AppiumBy.XPATH, f"//android.widget.LinearLayout[@clickable='true']//android.widget.TextView[@text='{dropoff}']")
		first_result.click()
		print(f"Selected dropoff: {dropoff}")
		time.sleep(3)
		
		# After selecting dropoff location
		print("Looking for pickup entry...")
		try:
			# Click on the pickup waypoint to activate search
			pickup_waypoint = driver.find_element(AppiumBy.XPATH, "//android.widget.FrameLayout[@content-desc[contains(., 'pickup')]]")
			pickup_waypoint.click()
			print("Clicked pickup entry")

			time.sleep(2)

			# Now enter pickup location in search field
			print(f"Typing pickup location: {pickup}")
			pickup_input = driver.find_element(AppiumBy.ID, "com.waymo.carapp:id/input_text_pickup")
			pickup_input.send_keys(pickup)

			time.sleep(2)

			# Try to select from results
			print(f"Selecting {pickup} from results...")
			result = driver.find_element(AppiumBy.XPATH, f"//android.widget.TextView[contains(@text, '{pickup}')]")
			result.click()
			print(f"Selected pickup: {pickup}")

		except Exception as e:
			print(f"Error during pickup selection process: {e}")
			raise e
		
		time.sleep(6)

		# Extract trip information using more general selectors
		try:
			# For pickup wait time (under PICKUP label)
			pickup_wait = driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[@text='PICKUP']/following-sibling::android.widget.ViewSwitcher//android.widget.TextView[@resource-id='com.waymo.carapp:id/eta_text']").text
			if not pickup_wait.isdigit():
				pickup_wait = ''.join(filter(str.isdigit, pickup_wait))

			# For dropoff time (under DROPOFF label)
			dropoff_time = driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[@text='DROPOFF']/following-sibling::android.widget.TextView[@resource-id='com.waymo.carapp:id/eta_text']").text
			period = driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[@text='DROPOFF']/following-sibling::android.widget.TextView[@resource-id='com.waymo.carapp:id/eta_suffix']").text
			dropoff_time = f"{dropoff_time} {period}"
			
			price = driver.find_element(AppiumBy.ID, "com.waymo.carapp:id/fare_estimate_text").text
			
			# Get current time
			current_time = datetime.now().strftime("%I:%M %p PST")
			
			print("\nTrip Summary:")
			print(f"Current time: {current_time}")
			print(f"Pickup wait time: {pickup_wait} minutes")
			print(f"Estimated arrival: {dropoff_time}")
			print(f"Price: {price}")
			
		except Exception as e:
			print(f"Error extracting trip information: {e}")
			
		driver.quit()
		return True
			
	except Exception as e:
		print(f"""
			Error: {e}\n
			Make sure:\n
			1. Appium is running in another terminal (run 'appium')\n
			2. Android emulator is running\n
			""")
		if 'driver' in locals():
			driver.quit()
		return False
			
if __name__ == "__main__":
  search_waymo_trip("Radhaus", "Chase Center")