from dataclasses import dataclass

@dataclass
class TripInfo:
	pickup_location: str
	pickup_wait_time: str
	dropoff_location: str
	dropoff_time: str
	current_time: str
	time_zone: str
	price: str
	currency: str