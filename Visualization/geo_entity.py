import collections
from geopy.geocoders import Nominatim
import pprint
from matplotlib.pyplot import plot
import reverse_geocode
import json
import time

def main():

	with open('my_dict.json') as f:
		data = json.load(f)

	name_frequency = collections.defaultdict(int)

	for name in data:
		name_frequency[name] += len(data[name])

	place_frequency = collections.defaultdict(int)

	for name, name_data in data.items():
		if name_data:
			for data_item in name_data:
				data_item[1] = data_item[1].strip()
				place_frequency[data_item[1]] += 1

	sorted_place_frequency = sorted(place_frequency.items(), key = lambda item: item[1], reverse = True)

	country_frequency = collections.defaultdict(int)
	city_frequency = collections.defaultdict(int)
	geolocator = Nominatim(user_agent="specify_your_app_name_here")

	# from geopy.extra.rate_limiter import RateLimiter
	# geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

	for place in sorted_place_frequency:
		location = geolocator.geocode(place[0])
		print(location)
		
		if location:
			coordinates = [(location.latitude, location.longitude)]
			geo_data = reverse_geocode.search(coordinates)
			country_frequency[geo_data[0]['country']] += place[1]
			city_frequency[geo_data[0]['city']] += place[1]

		time.sleep(1)

	sorted_country_frequency = sorted(country_frequency.items(), key = lambda item: item[1], reverse = True)
	print(sorted_country_frequency)

	sorted_city_frequency = sorted(city_frequency.items(), key = lambda item: item[1], reverse = True)
	print(sorted_city_frequency)

if __name__ == '__main__':
	main()
