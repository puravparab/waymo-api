from core.waymo_client import WaymoClient

def main():
	try:
		# Using context manager for automatic cleanup
		with WaymoClient() as client:
			trip_info = client.get_trip_info(
				pickup="Radhaus",
				dropoff="Salesforce park"
			)
			
			# Print trip details
			print("\nTrip Details:")
			print(f"Pickup Location: {trip_info.pickup_location}")
			print(f"Dropoff Location: {trip_info.dropoff_location}")
			print(f"Pickup Wait Time: {trip_info.pickup_wait_time}")
			print(f"Dropoff Time: {trip_info.dropoff_time}")
			print(f"Price: {trip_info.price}")
			print(f"Current Time: {trip_info.current_time}")
					
	except Exception as e:
		print(f"Error: {str(e)}")
		print("\nTroubleshooting:")
		print("1. Make sure Appium is running (run 'appium' in another terminal)")
		print("2. Make sure Android emulator is running")
		print("3. Check if Waymo app is installed on the emulator")

if __name__ == "__main__":
	main()