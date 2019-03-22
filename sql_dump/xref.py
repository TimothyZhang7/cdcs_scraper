import csv

THE_CDCS_SCHEMA = ['crn', 'cname', 'title', 'semester', 'credit', 'status'
					, 'schedule', 'begin', 'end', 'building', 'room', 'capacity'
					, 'professor', 'preq', 'desc', 'major']
COURSE_SCHEMA = ['id', 'school_id', 'semester', 'major', 'crn', 'cname'
					, 'title', 'credit', 'score', 'desc', 'preq']
PROFESSOR_SCHEMA = ['id', 'name', 'email', 'website', 'cv_url', 'avatar', 'intro', 'note', 'create_t', 'update_t']

TEACH_SCHEMA = ['professor_id','course_id', 'term', 'capacity', 'location']

SCHEDULE_SCHEMA = ['teaching_id', 'weekday', 'start_t', 'end_t', 'building','room']

def main():
	cdcs = []
	with open('cdcs_fall2019_open.csv', 'r', encoding='utf-8') as f:
		reader = csv.reader(f)
		cdcs = list(reader)
	professors = []
	with open('courscio_professor.csv', 'r', encoding='utf-8') as f:
		reader = csv.reader(f)
		professors = list(reader)
	courses = []
	with open('courscio_course.csv', 'r', encoding='utf-8') as f:
		reader = csv.reader(f)
		courses = list(reader)
	xref_data = []
	with open('professor_xref.csv', 'r', encoding='utf-8') as f:
		reader = csv.reader(f)
		xref_data = list(reader)

	outfile = open('teaching.csv', 'w', encoding='utf-8')
	out_handler = csv.writer(outfile, delimiter=',')

	outfile_s = open('schedule.csv', 'w', encoding='utf-8')
	out_s_handler = csv.writer(outfile_s, delimiter=',')

	cdcs_dict = make_dict(cdcs,0)
	print('cdcs no duplicate')
	prof_dict = make_dict(professors, 1)
	print('Professor no duplicate')
	xref = make_dict(xref_data, 1)
	print('Xrefed')
	print(xref)

	teaching_index = get_indexer(TEACH_SCHEMA)
	course_index = get_indexer(COURSE_SCHEMA)
	professor_index = get_indexer(PROFESSOR_SCHEMA)
	cdcs_index = get_indexer(THE_CDCS_SCHEMA)
	schedule_index = get_indexer(SCHEDULE_SCHEMA)

	teaching_id = 1
	for row in courses:
		if len(row) >= 7:
			tupn = []
			for i in range(len(TEACH_SCHEMA)):
				tupn.append('NULL')

			tups = []
			for j in range(len(SCHEDULE_SCHEMA)):
				tups.append('NULL')

			#Teaching table
			cdcs_row = cdcs_dict[row[course_index['crn']]]
			professor = cdcs_row[cdcs_index['professor']]
			tupn[teaching_index['course_id']] = row[course_index['id']]
			tupn[teaching_index['term']] = cdcs_row[cdcs_index['semester']]
			tupn[teaching_index['capacity']] = cdcs_row[cdcs_index['capacity']]
			building = cdcs_row[cdcs_index['building']]
			room = cdcs_row[cdcs_index['room']]
			tupn[teaching_index['location']] = building + ' ' + room

			#Schedule table
			tups[schedule_index['teaching_id']] = teaching_id
			tups[schedule_index['start_t']] = cdcs_row[cdcs_index['begin']]
			tups[schedule_index['end_t']] = cdcs_row[cdcs_index['end']]
			tups[schedule_index['building']] = cdcs_row[cdcs_index['building']]
			tups[schedule_index['room']] = cdcs_row[cdcs_index['room']]

			if cdcs_row[cdcs_index['schedule']] == None or cdcs_row[cdcs_index['schedule']] == 'TBA' or len(cdcs_row[cdcs_index['schedule']]) < 1:
				tups[schedule_index['weekday']] = 'NULL'
				out_s_handler.writerow(tups)
			else:
				for c in cdcs_row[cdcs_index['schedule']]:
					if c == 'M':
						tups[schedule_index['weekday']] = 'MON'
					elif c == 'T':
						tups[schedule_index['weekday']] = 'TUE'
					elif c == 'W':
						tups[schedule_index['weekday']] = 'WEN'
					elif c == 'R':
						tups[schedule_index['weekday']] = 'THU'
					elif c == 'F':
						tups[schedule_index['weekday']] = 'FRI'
					elif c == 'S':
						tups[schedule_index['weekday']] = 'SAT'
					elif c == 'U':
						tups[schedule_index['weekday']] = 'SUN'
					else:
						tups[schedule_index['weekday']] = 'NULL'
						print('weekday parsing err')
					out_s_handler.writerow(tups)

			teaching_id = teaching_id + 1

			if professor in xref:
				parsed_prof = xref[professor]
				professor_row = prof_dict[parsed_prof[0]]
				tupn[teaching_index['professor_id']] = professor_row[professor_index['id']]
				print(tupn)
				out_handler.writerow(tupn)
			else:
				tupn[teaching_index['professor_id']] = -1
				print(tupn)
				out_handler.writerow(tupn)


	outfile.close()
	print('finish')

def make_dict(data, key_index):
	result = dict()
	for row in data:
		if len(row) > 1:
			result[row[key_index]] = row
	return result

def get_indexer(schema):
	indexer = dict()
	i = 0
	for attr in schema:
		indexer[attr] = i
		i = i+1
	return indexer

main()