import os
import sys
import json

import utils
import config
import syllabus

def main():
	try: department = sys.argv[1]
	except IndexError:
		utils.die('Usage:', sys.argv[0], '<department>')

	config.init(department)

	html = open(config.HTML_TEMPLATE_PATH).read()
	print(html.format(
		title      = config.TITLE,
		stylesheet = config.CSS_PATH,
		favicon    = config.FAVICON_PATH,
		script     = config.JS_PATH,
		background = config.BACKGROUND_PATH,
		heading    = config.HEADING,
		courses    = generate_course_html()
	), file=open(department.lower() + '.html', 'w'))

def generate_course_html():
	course_map = json.loads(open(config.COURSEMAP_PATH).read())
	discover_syllabi_files(course_map)
	return course_map_to_html(course_map)

# augment course map with list of syllabi files from filesystem
def discover_syllabi_files(course_map):
	# schema of course map file: '{<category>:{<course_code>:<course_name>}}'
	for category in course_map:
		for course_code in course_map[category].copy():
			course_path = config.SYLLABI_PATH + '/' + course_code.replace(' ', '_')
			try: syllabi_files = os.listdir(course_path)
			except FileNotFoundError:
				syllabi_files = []

			course_name = course_map[category][course_code]
			course_map[category][course_code] = {
				'course_name': course_code + ': ' + course_name,
				'files': utils.sort_chronologically(syllabi_files)
			}
	# schema of post-processed course map file:
	# '{<category>:{<course_code>:{"course_name":<course_name>,"files":[<files>]}}}'

def course_map_to_html(course_map):
	category_html = '<details open class="{classname}">{summary}<div class="content">{courses}</div></details>'
	course_html   = '<details class="{classname}">{summary}{div}</details>'

	categories = []
	for category in course_map:

		courses = []
		for course_code in course_map[category]:

			course_path = config.SYLLABI_PATH + '/' + course_code.replace(' ', '_')
			course_name = course_map[category][course_code]['course_name']

			bullets = []
			for file in course_map[category][course_code]['files']:
				s = syllabus.parse(file)
				a = '<a href="{url}">{value}</a>'.format(
					url = course_path + '/' + file,
					value = utils.pretty_syllabus_name(s.semester, s.professor)
					        or file
				)
				icon = utils.faculty_icon(s.professor)
				li = '<li>{bullet}</li>'.format(
					bullet = a if not icon else (icon + a)
				)
				bullets.append(li)

			bullets = '<ul>' + '\n'.join(bullets) + '</ul>' if bullets else ''
			courses.append(course_html.format(
				classname = 'courses',
				summary   = '<summary class="course-title">' + course_name + '</summary>',
				div       = '<div>' + bullets + '</div>'
			))

		categories.append(category_html.format(
			classname = 'category',
			summary   = '<summary class="category-title">' + utils.pretty_category(category) + '</summary>',
			courses   = '\n'.join(courses)
		))

	return '\n'.join(categories)

main()
