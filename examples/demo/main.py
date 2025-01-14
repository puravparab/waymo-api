import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor

root = Path(__file__).parent.parent.parent
sys.path.append(str(root))

from src.waymo_api.core.client import WaymoClient
from src.waymo_api.core.exceptions import WaymoClientError
from src.waymo_api.utils.logger import setup_logger

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
	parser.add_argument(
		'--workers',
		type=int,
		default=1,
		help='Number of parallel workers (default: 1)'
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

# def process_trips_parallel(trips: List[Dict[str, str]], max_workers: int) -> List[Dict]:
# 	"""Process multiple trips in parallel"""
# 	with ThreadPoolExecutor(max_workers=max_workers) as executor:
# 		results = list(executor.map(process_single_trip, trips))
# 	return results

def process_trip(client: WaymoClient, pickup: str, dropoff: str) -> Dict:
	"""Process a single trip and return results"""
	try:
		trip_info = client.get_trip_info(pickup=pickup, dropoff=dropoff)
		return {
			"pickup": pickup,
			"dropoff": dropoff,
			"success": True,
			"results": {
				"pickup_wait_time": trip_info.pickup_wait_time,
				"dropoff_time": trip_info.dropoff_time,
				"price": trip_info.price,
				"current_time": trip_info.current_time,
				"time_zone": trip_info.time_zone
			}
		}
	except Exception as e:
		return {
			"pickup": pickup,
			"dropoff": dropoff,
			"success": False,
			"error": str(e)
		}

def process_trips(trips: List[Dict[str, str]], max_workers: int = 1) -> List[Dict]:
	"""Process trips sequentially using a single client"""
	results = []
	with WaymoClient() as client:
		for trip in trips:
			result = process_trip(
				client=client,
				pickup=trip["pickup"],
				dropoff=trip["dropoff"]
			)
			results.append(result)
	return results

def print_trip_result(result: Dict):
	"""Print formatted trip result"""
	print("\nTrip Details:")
	print(f"Pickup Location: {result['pickup']}")
	print(f"Dropoff Location: {result['dropoff']}")

	if result['success']:
		print(f"Pickup Wait Time: {result['results']['pickup_wait_time']}")
		print(f"Dropoff Time: {result['results']['dropoff_time']}")
		print(f"Price: {result['results']['price']}")
		print(f"Current Time: {result['results']['current_time']} {result['results']['time_zone']}")
	else:
		print(f"Error: {result['error']}")

def main():
	log_dir = root / "logs"
	log_file = log_dir / "main.log"
	setup_logger(log_level="INFO", log_file=str(log_file))

	args = parse_arguments()
	try:
		if args.trip:  # Handle single trip from command line
			trips = [{"pickup": args.trip[0], "dropoff": args.trip[1]}]
		else:  # Handle trips from JSON file
			trips = load_trips_from_json(args.trips)
		
		results = process_trips(trips, args.workers)

		print("\nResults:")
		for result in results:
			print_trip_result(result)
		successful = sum(1 for r in results if r['success'])
		print(f"\nSummary: {successful}/{len(results)} trips completed successfully")

	except WaymoClientError as e:
		print(f"Waymo Client Error: {str(e)}")
	except ValueError as e:
		print(f"Invalid input: {str(e)}")
	except Exception as e:
		print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
	main()