from datetime import datetime
from dataclasses import dataclass

@dataclass
class TimeInfo:
	value: datetime
	time_zone: str

@dataclass
class LocationInfo:
	address: str
	city: str

@dataclass
class PriceInfo:
	value: float
	currency: str

@dataclass
class WayPoint:
	location: LocationInfo
	time: TimeInfo
	wait_time: int # minutes (0 for dropoff)



@dataclass
class TripInfo:
	current_datetime: TimeInfo
	price: PriceInfo
	pickup: WayPoint
	dropoff: WayPoint