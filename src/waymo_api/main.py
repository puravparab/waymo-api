import json
import argparse
from core.waymo_client import WaymoClient, WaymoClientError

def parse_arguments():
	parser = argparse.ArgumentParser(description='Get Waymo trip inputs')
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument(
		'--trip',
		nargs=2,
		metavar=('PICKUP', 'DROPOFF'),
		help='Single trip pickup and dropoff locations'
	)
	group.add_argument(
		'--trips',
		type=str,
		help='Path to JSON file containing trips array. Each trip should have "pickup" and "dropoff" keys'
	)
	return parser.parse_args()

def load_trips_from_json(file_path):
	try:
		with open(file_path, 'r') as f:
			trips = json.load(f)
			if not isinstance(trips, list):
				raise ValueError("JSON file must contain an array of trips")
		for trip in trips:
			if not isinstance(trip, dict) or "pickup" not in trip or "dropoff" not in trip:
				raise ValueError("Each trip must have 'pickup' and 'dropoff' keys")
		return trips
	except json.JSONDecodeError:
		raise ValueError("Invalid JSON format in file")
	except FileNotFoundError:
		raise ValueError(f"File not found: {file_path}")

def main():
	args = parse_arguments()
	try:
		if args.trip:
			# Handle single trip from command line
			trips = [{
				"pickup": args.trip[0],
				"dropoff": args.trip[1]
			}]
		else:
			# Handle trips from JSON file
			trips = load_trips_from_json(args.trips)
		
		with WaymoClient() as client:
			for trip in trips:
				trip_info = client.get_trip_info(
					pickup=trip["pickup"],
					dropoff=trip["dropoff"]
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
	except ValueError as e:
		print(f"Invalid input: {str(e)}")
	except Exception as e:
		print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
	main()