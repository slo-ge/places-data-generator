import json
import logging

from sitemap.generate import get_wp_response, API_URL, BLOG_TYPE, PAGE_TYPE, LOCATION_TYPE


def main():
	for wp_type in [PAGE_TYPE, BLOG_TYPE, LOCATION_TYPE]:
		wp_response = get_wp_response(API_URL + '/' + wp_type)
		write(wp_response, wp_type)
		logging.info(f'/{wp_type}: Items {len(wp_response)}')


def write_geo_dtos():
	wp_response = get_wp_response(API_URL + '/' + LOCATION_TYPE)
	geo_dtos = []
	for wp_object in wp_response:
		title = wp_object['title']['rendered']
		wp_id = wp_object['id']
		slug = wp_object['slug']  # not used

		try:
			lat = float(wp_object['acf']['place']['lat'])
			lng = float(wp_object['acf']['place']['lng'])
		except:
			logging.error(f'place: {title}, has no lat/lng')
			continue

		try:
			url = wp_object['_embedded']['wp:featuredmedia'][0]['source_url']
		except:
			url = ''

		geo_dtos.append({'title': title, 'id': wp_id, 'lat': lat, 'lng': lng, 'imgUrl': url})

		with open(f'resources/geo-places.json', 'w') as file:
			file.write(json.dumps(geo_dtos))


def write(data, name):
	# write full
	# with open(f'resources/{name}.json', 'w') as file:
	#    file.write(json.dumps(data))
	for obj in data:
		with open(f'resources/{name}/{obj["slug"]}.json', 'w') as file:
			file.write(json.dumps(obj))


if __name__ == '__main__':
	write_geo_dtos()
