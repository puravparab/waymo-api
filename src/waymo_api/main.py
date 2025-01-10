from core.waymo_client import WaymoClient, WaymoClientError

def main():
	try:
		with WaymoClient() as client:
			trip_info = client.get_trip_info(
				pickup="Radhaus",
				dropoff="Salesforce park"
			)
			
			print("\nTrip Details:")
			print(f"Pickup Location: {trip_info.pickup_location}")
			print(f"Dropoff Location: {trip_info.dropoff_location}")
			print(f"Pickup Wait Time: {trip_info.pickup_wait_time}")
			print(f"Dropoff Time: {trip_info.dropoff_time}")
			print(f"Price: {trip_info.price}")
			print(f"Current Time: {trip_info.current_time}")	

	except WaymoClientError as e:
		print(f"Waymo Client Error: {str(e)}")

	except Exception as e:
		print(f"Unexpected error: {str(e)}")
		
if __name__ == "__main__":
	main()