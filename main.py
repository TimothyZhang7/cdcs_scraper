from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as Expect
from selenium.webdriver.support.select import Select
from bs4 import BeautifulSoup as bs
import csv
import sys

THE_CDCS_SCHEMA = ['crn', 'cname', 'title', 'semester', 'credit', 'status'
					, 'schedule', 'begin', 'end', 'building', 'room', 'capacity'
					, 'professor', 'preq', 'desc', 'major']
COURSE_SCHEMA = ['id', 'school_id', 'semester', 'major', 'crn', 'cname'
					, 'title', 'credit', 'score', 'desc', 'preq', 'professor']
TERM_DROPDOWN = (By.ID, 'ddlTerm')
SCHOOL_DROPDOWN = (By.ID, 'ddlSchool')
STATUS_DROPDOWN = (By.ID, 'ddlStatus')	
SUBJECT_DROPDOWN = (By.ID, 'ddlDept')
TYPE_DROPDOWN = (By.ID, 'ddlTypes')

driver = webdriver.Chrome('chromedriver.exe')
driver.get("https://cdcs.ur.rochester.edu/")

db = open('cdcs_spring2016_open.csv', 'w', encoding='utf-8')
dbms = csv.writer(db, delimiter=',')

ct = open('course_table.csv', 'w', encoding='utf-8')
ct_handler = csv.writer(ct, delimiter=',')

def main():

	default_term = 'Spring 2016'
	default_status = 'OP'
	default_school = 'Arts, Sciences, and Engineering'
	default_type = 'Main Course'

	args = sys.argv[1:]

	for arg in args:
		if 'Fall' in arg or 'Summer' in arg or 'Spring' in arg:
			default_term = arg
		elif 'OP' in arg or 'CA' in arg or 'Cl' in arg:
			default_status = arg
		elif 'Science' in arg or 'School' in arg or 'Institute' in arg:
			default_school = arg
		else:
			print('Invalid arguments')


	term_dropdown = WebDriverWait(driver,10).until(Expect.presence_of_element_located(TERM_DROPDOWN))
	school_dropdown = WebDriverWait(driver,10).until(Expect.presence_of_element_located(SCHOOL_DROPDOWN))
	status_dropdown = WebDriverWait(driver,10).until(Expect.presence_of_element_located(STATUS_DROPDOWN))	
	subject_dropdown = WebDriverWait(driver,10).until(Expect.presence_of_element_located(SUBJECT_DROPDOWN))	
	type_dropdown = WebDriverWait(driver,10).until(Expect.presence_of_element_located(TYPE_DROPDOWN))	

	select_term = Select(term_dropdown)
	select_school = Select(school_dropdown)
	select_status = Select(status_dropdown)	
	select_subject = Select(subject_dropdown)
	select_type = Select(type_dropdown)


	try:
		select_term.select_by_visible_text(default_term)
		select_status.select_by_value(default_status)
		select_type.select_by_visible_text(default_type)
		select_school.select_by_visible_text(default_school)
	except:
		print("Error finding element")

	time.sleep(5)
	subject_dropdown = WebDriverWait(driver,10).until(Expect.presence_of_element_located(SUBJECT_DROPDOWN))	
	subjects = [x.get_attribute('value') for x in subject_dropdown.find_elements_by_tag_name("option")]
	subject_list = subjects

#	for e in subjects:
#		subject_list.append(e.get_attribute('value'))


	subject_list = list(filter(None, subject_list))

	dbms.writerow(THE_CDCS_SCHEMA)

	for subject in subject_list:
		subject_comprehend(subject)

	db.close()
	ct.close()
	print('finished')


def subject_comprehend(subject):
	print('Scraping: '+subject)
	subject_dropdown = WebDriverWait(driver,10).until(Expect.presence_of_element_located(SUBJECT_DROPDOWN))	
	select_subject = Select(subject_dropdown)
	select_subject.select_by_value(subject)
	search_and_parse(subject)

def search_and_parse(subject):
	search = driver.find_element_by_id("btnSearchTop")
	search.click()
	time.sleep(5)
	table = driver.find_element_by_xpath('''//*[@id="UpdatePanel4"]/table/tbody/tr/td[3]''')
	htmlfile = table.get_attribute('outerHTML')
	soup = bs(htmlfile, 'html.parser')
	tables = soup.findAll("table")
	data = []
	for table in tables:
		tbody = table.find('tbody')
		rows = tbody.find_all('tr')
		for row in rows:
			cols = row.find_all('td')
			cols = [ele.text.strip().replace('\n','').replace('\xa0','') for ele in cols]
			data.append([ele for ele in cols if ele])

	clean_data = []
	cur_course = []
	i = -1
	for row in data:
		if len(row)>0 and row[0]=='CRN':
			if len(cur_course) > 0:
				clean_data.append(cur_course)
			i = 0
			cur_course = []
		if i != -1:
			if len(row)>0:
				cur_course.append(row)
			i = i+1

	for course in clean_data:
		get_attributes(THE_CDCS_SCHEMA, course, subject)

def get_attributes(schema, course, subject):
	tup = []
	where = get_indexer(schema)
	for attr in schema:
		tup.append('NULL')
	tup[-1] = subject
	for i in range(len(course)):
		if course[i][0]=='CRN':
			attrs = course[i+1]
			attrs.extend(course[i+3])
			for j in range(len(attrs)):
				tup[j] = attrs[j]
		if len(course[i]) >= 3:
			if course[i][0]=='Enrollment:':
				sc = 0
				if 'No Cap' in course[i][2]:
					sc = 0
				else:
					sc = int(course[i][2].replace('Section Cap',''))
				tc = 0
				if len(course[i]) >= 5:
					if 'No Cap' in course[i][4]:
						tc = -1
					else:
						tc = int(course[i][4].replace('Total Cap',''))
				tup[where['capacity']] = max(sc,tc)
		if len(course[i]) >= 2:
			if course[i][0]=='Instructors:':
				tup[where['professor']] = course[i][1]
			if course[i][0]=='Prerequisites:':
				tup[where['preq']] = course[i][1]
			if course[i][0]=='Description:':
				tup[where['desc']] = course[i][1]


	tup_course = filter_down_tuple(THE_CDCS_SCHEMA, COURSE_SCHEMA, tup, True)
	print(tup_course)
	dbms.writerow(tup)
	ct_handler.writerow(tup_course)

def filter_down_tuple(schema_l, schema_s, tuple_l, isAutoId):
	where = get_indexer(schema_l)
	tuple_s = []
	if isAutoId:
		for i in range(len(schema_s)-1):
			tuple_s.append('')
		for i in range(len(schema_s)-1):
			if schema_s[i+1] not in schema_l:
				tuple_s[i] = 'NULL'
			else:
				tuple_s[i] = tuple_l[where[schema_s[i+1]]]
	else:
		for i in range(len(schema_s)):
			tuple_s.append('')
		for i in range(len(schema_s)):
			if schema_s[i] not in schema_l:
				tuple_s[i] = 'NULL'
			else:
				tuple_s[i] = tuple_l[where[schema_s[i]]]

			
	return tuple_s



def get_indexer(schema):
	indexer = dict()
	i = 0
	for attr in schema:
		indexer[attr] = i
		i = i+1
	return indexer


main()


