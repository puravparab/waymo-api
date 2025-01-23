import sys
import time
import random
import csv
import pandas as pd
from pathlib import Path
from datetime import datetime

root = Path(__file__).parent.parent.parent
sys.path.append(str(root))

from src.waymo_api.core.client import WaymoClient
from src.waymo_api.core.exceptions import WaymoClientError
from src.waymo_api.utils.logger import setup_logger

def load_locations(csv_path):
	"""Load locations from CSV file"""
	df = pd.read_csv(csv_path)
	locations = df.apply(lambda row: {
		'name': row['name'],
		'neighborhood': row['neighborhood'],
		'latitude': row['latitude'],
		'longitude': row['longitude']
	}, axis=1).tolist()
	return locations

def select_random_locations(locations):
	"""Select two random different locations"""
	pickup, dropoff = random.sample(locations, 2)
	return pickup, dropoff

def load_excluded_pairs(excluded_csv):
	"""Load excluded location pairs from CSV file"""
	df = pd.read_csv(excluded_csv)
	pairs = df.apply(lambda row: {
		'pickup': {
			'name': row['pickup_name'],
			'neighborhood': row['pickup_neighborhood']
		},
		'dropoff': {
			'name': row['dropoff_name'],
			'neighborhood': row['dropoff_neighborhood']
		}
	}, axis=1).tolist()
	return pairs

def get_trip_estimates(client, pickup, dropoff):
	"""Get trip information using Waymo API"""
	try:
		trip_info = client.get_trip_info(
			pickup=pickup['name'],
			dropoff=dropoff['name']
		)

		return {
			# Request metadata
			'request_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
			
			# Pickup location details
			'pickup_name': pickup['name'],
			'pickup_neighborhood': pickup['neighborhood'],
			'pickup_latitude': pickup['latitude'],
			'pickup_longitude': pickup['longitude'],
			'pickup_time': trip_info['pickup']['pickup_time'],
			'pickup_date': trip_info['pickup']['date'],
			'pickup_wait_time_mins': trip_info['pickup']['wait_time'],
			
			# Dropoff location details
			'dropoff_name': dropoff['name'],
			'dropoff_neighborhood': dropoff['neighborhood'],
			'dropoff_latitude': dropoff['latitude'],
			'dropoff_longitude': dropoff['longitude'],
			'dropoff_time': trip_info['dropoff']['dropoff_time'],
			'dropoff_date': trip_info['dropoff']['date'],
			
			# Trip details
			'trip_duration_mins': trip_info['duration'],
			'price_usd': trip_info['price']['value'],
			'price_currency': trip_info['price']['currency'],
			
			# Additional context
			'current_time': trip_info['current_datetime']['value'],
			'current_date': trip_info['current_datetime']['date'],
			'timezone': trip_info['current_datetime']['time_zone'],
			'city': trip_info['city']
		}

	except Exception as e:
		print(f"Error getting trip data: {str(e)}")
		return None

def save_to_csv(data, output_file):
	"""Append trip data to CSV file"""
	file_exists = Path(output_file).exists()

	if file_exists:
		with open(output_file, 'r') as f:
				headers = next(csv.reader(f))
	else:
		# Use explicit headers for new file
		headers = [
			'request_timestamp',
			'pickup_name','pickup_neighborhood','pickup_latitude','pickup_longitude',
			'pickup_time','pickup_date','pickup_wait_time_mins',
			'dropoff_name','dropoff_neighborhood','dropoff_latitude','dropoff_longitude',
			'dropoff_time','dropoff_date',
			'trip_duration_mins','price_usd','price_currency',
			'current_time','current_date','timezone','city'
		]

	with open(output_file, 'a', newline='') as f:
		writer = csv.DictWriter(f, fieldnames=headers)
		if not file_exists:
			writer.writeheader()
		writer.writerow(data)

def save_error_to_csv(error_data, error_file):
	"""Save error data to a separate CSV file"""
	file_exists = Path(error_file).exists()
	
	headers = [
		'timestamp',
		'pickup_name',
		'pickup_neighborhood',
		'dropoff_name',
		'dropoff_neighborhood',
	]
	
	with open(error_file, 'a', newline='') as f:
		writer = csv.DictWriter(f, fieldnames=headers)
		if not file_exists:
			writer.writeheader()
		writer.writerow(error_data)

def main():
	log_dir = root / "logs"
	log_file = log_dir / "sf_trips.log"
	setup_logger(log_level="INFO", log_file=str(log_file))

	input_csv = root / "examples/sf/data/sf_locations.csv"
	excluded_csv = root / "examples/sf/data/excluded_pairs.csv"
	outputs_dir = root / "examples/sf/output"
	outputs_dir.mkdir(exist_ok=True)
	output_csv = outputs_dir / 'sf_waymo_estimates.csv'
	error_csv = outputs_dir / 'sf_waymo_errors.csv'
	
	locations = load_locations(input_csv)
	excluded_pairs = load_excluded_pairs(excluded_csv)
	
	# Initialize Waymo client
	with WaymoClient() as client:
		for pair in excluded_pairs:
			try:
				pickup = pair['pickup']
				dropoff = pair['dropoff']

				print(f"\nGetting trip info for: {pickup['name']} → {dropoff['name']}")

				# Find full location details from locations list
				pickup_full = next(loc for loc in locations if loc['name'] == pickup['name'])
				dropoff_full = next(loc for loc in locations if loc['name'] == dropoff['name'])

				# Get trip estimates
				trip_estimates = get_trip_estimates(client, pickup_full, dropoff_full)

				# Save data if successful
				if trip_estimates:
					save_to_csv(trip_estimates, output_csv)
					print(f"Trip estimates data saved successfully: {pickup['name']} to {dropoff['name']}")
					print(f"Price: ${trip_estimates['price_usd']:.2f}, Duration: {trip_estimates['trip_duration_mins']} mins")
				else:
					error_data = {
						'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
						'pickup_name': pickup['name'],
						'pickup_neighborhood': pickup['neighborhood'],
						'dropoff_name': dropoff['name'],
						'dropoff_neighborhood': dropoff['neighborhood'],
					}
					save_error_to_csv(error_data, error_csv)
					print("Failed to get trip estimate data - skipping this pair")

			except KeyboardInterrupt:
				print("\nStopping the script...")
				break
			except Exception as e:
				error_data = {
					'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
					'pickup_name': pickup['name'],
					'pickup_neighborhood': pickup['neighborhood'],
					'dropoff_name': dropoff['name'],
					'dropoff_neighborhood': dropoff['neighborhood'],
				}
				save_error_to_csv(error_data, error_csv)
				print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
	main()