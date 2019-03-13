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

THE_CDCS_SCHEMA = ['crn', 'name', 'title', 'term', 'credits', 'status'
					, 'schedule', 'begin', 'end', 'building', 'room', 'capacity'
					, 'professor', 'prereq', 'description']
TERM_DROPDOWN = (By.ID, 'ddlTerm')
SCHOOL_DROPDOWN = (By.ID, 'ddlSchool')
STATUS_DROPDOWN = (By.ID, 'ddlStatus')	
SUBJECT_DROPDOWN = (By.ID, 'ddlDept')

driver = webdriver.Chrome('chromedriver.exe')
driver.get("https://cdcs.ur.rochester.edu/")

db = open('cdcs.csv', 'w', encoding='utf-8')
dbms = csv.writer(db, delimiter=',')

def main():

	term_dropdown = WebDriverWait(driver,10).until(Expect.presence_of_element_located(TERM_DROPDOWN))
	school_dropdown = WebDriverWait(driver,10).until(Expect.presence_of_element_located(SCHOOL_DROPDOWN))
	status_dropdown = WebDriverWait(driver,10).until(Expect.presence_of_element_located(STATUS_DROPDOWN))	
	subject_dropdown = WebDriverWait(driver,10).until(Expect.presence_of_element_located(SUBJECT_DROPDOWN))	

	select_term = Select(term_dropdown)
	select_school = Select(school_dropdown)
	select_status = Select(status_dropdown)	
	select_subject = Select(subject_dropdown)

	try:
		select_term.select_by_value('D-20201')
		select_status.select_by_value('OP')
		select_school.select_by_value('1')
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


def subject_comprehend(subject):
	print('Scraping: '+subject)
	subject_dropdown = WebDriverWait(driver,10).until(Expect.presence_of_element_located(SUBJECT_DROPDOWN))	
	select_subject = Select(subject_dropdown)
	select_subject.select_by_value(subject)
	search_and_parse()

def search_and_parse():
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
		get_attributes(THE_CDCS_SCHEMA, course)

def get_attributes(schema, course):
	tup = []
	where = get_indexer(schema)
	for attr in schema:
		tup.append('NULL')
	for i in range(len(course)):
		if course[i][0]=='CRN':
			attrs = course[i+1]
			attrs.extend(course[i+3])
			for j in range(len(attrs)):
				tup[j] = attrs[j]
		if len(course[i]) >= 5:
			if course[i][0]=='Enrollment:':
				tup[where['capacity']] = course[i][4].replace('Total Cap','')
		if len(course[i]) >= 2:
			if course[i][0]=='Instructors:':
				tup[where['professor']] = course[i][1]
			if course[i][0]=='Prerequisites:':
				tup[where['prereq']] = course[i][1]
			if course[i][0]=='Description:':
				tup[where['description']] = course[i][1]

	print(tup)
	dbms.writerow(tup)

def get_indexer(schema):
	indexer = dict()
	i = 0
	for attr in schema:
		indexer[attr] = i
		i = i+1
	return indexer


main()


