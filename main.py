import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

def search_waymo_trip(pickup, dropoff):
	print("Starting...")
	
	options = UiAutomator2Options()
	options.platform_name = 'Android'
	options.device_name = 'emulator-5554'
	options.app_package = 'com.waymo.carapp'
	options.app_activity = 'com.google.android.apps.car.carapp.CarAppMainActivity'
	options.no_reset = True

	try:
		print("Connecting to Appium...")
		driver = webdriver.Remote('http://localhost:4723', options=options)
		print("Connected!")
		
		print("Launching Waymo app...")
		driver.activate_app('com.waymo.carapp')
		time.sleep(5)
		
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
		
		# Click the pickup search element
		print("Clicking pickup search...")
		pickup_element = driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[@text='Search for a pickup']")
		pickup_element.click()
		time.sleep(2)
		
		# Ttype the pickup location
		print(f"Typing pickup location: {pickup}")
		pickup_input = driver.find_element(AppiumBy.ID, "com.waymo.carapp:id/input_text_pickup")
		pickup_input.send_keys(pickup)
		time.sleep(3)
		
		# Click the first result that matches pickup
		print("Selecting pickup location...")
		pickup_result = driver.find_element(AppiumBy.XPATH, f"//android.widget.LinearLayout[@clickable='true']//android.widget.TextView[@text='{pickup}']")
		pickup_result.click()
		print(f"Selected pickup: {pickup}")
		
		time.sleep(5)
		driver.quit()
		return
			
	except Exception as e:
		print(f"""
			Error: {e}\n
			Make sure:\n
			1. Appium is running in another terminal (run 'appium')\n
			2. Android emulator is running\n
			""")
		if 'driver' in locals():
			driver.quit()

if __name__ == "__main__":
  search_waymo_trip("Salesforce Tower", "Chase Center")