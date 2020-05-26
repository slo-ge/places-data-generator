import xml.etree.ElementTree as ET
from datetime import datetime

import requests

API_URL = 'https://locations.phipluspi.com/wp-json/wp/v2'
FE_URL_PLACE = 'https://www.goove.at/detail'
FE_URL_BLOG = 'https://www.goove.at/blog'

BASE = 'https://www.goove.at'
BLOG = 'blog'
SEARCH = 'search'
HOME = 'home'
LOCATION_TYPE = 'locations'
TAGS = 'tags'
BLOG_TYPE = 'posts'
PAGE_TYPE = 'pages'


def xml_element():
	"""
	get the xml element with the correct set urlset element
	:return:
	"""
	return ET.Element('urlset', {
		'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9'
	})


def get_sitemap_from_type(type: str) -> str:
	url_set = xml_element()
	append_url_from_wp_type(type, url_set, FE_URL_PLACE)

	return ET.tostring(url_set, encoding='utf8', method='xml')


def main():
	url_set = xml_element()
	append_url_from_wp_type('locations', url_set, FE_URL_PLACE)
	append_url_from_wp_type('posts', url_set, FE_URL_BLOG)

	for url in [BLOG, SEARCH, HOME]:
		url_set.append(element_from_wp_object(None, f'{BASE}/{url}'))
	append_search_pages(url_set)

	with open('sitemap.xml', 'wb') as writer:
		writer.write(ET.tostring(url_set, encoding='utf8', method='xml'))


def get_wp_response(url):
	wp_response = requests.get(f'{url}?_embed')  # TODO: control _embed query param by a PARAMS DICT
	wp = wp_response.json()
	page_count = int(wp_response.headers.get('X-WP-TotalPages'))
	for page in range(2, page_count):
		wp += requests.get(url + '?page={}&_embed'.format(page)).json()
	return wp


def append_search_pages(url_set):
	wp_response = requests.get(f'{API_URL}/{LOCATION_TYPE}')
	page_count = int(wp_response.headers.get('X-WP-TotalPages'))
	for index in range(1, page_count):
		url_set.append(element_from_wp_object(None, f'{BASE}/{SEARCH}?page={index}'))


def append_url_from_wp_type(type, url_set, route):
	places = get_wp_response(API_URL + '/' + type)
	for index, place in enumerate(places):
		url_set.append(element_from_wp_object(place, route))


def element_from_wp_object(wp_object, route):
	url = ET.Element('url')
	loc = ET.SubElement(url, 'loc')
	lastmod = ET.SubElement(url, 'lastmod')
	ET.SubElement(url, 'changefreq').text = 'weekly'
	if wp_object:
		try:
			loc.text = route + '/' + wp_object['slug']
		except:
			raise ()
		lastmod.text = wp_object['modified'].split('T')[0]
	else:
		loc.text = route
		now = datetime.now()
		lastmod.text = now.strftime('%Y-%m-%d')
	return url


if __name__ == '__main__':
	main()
