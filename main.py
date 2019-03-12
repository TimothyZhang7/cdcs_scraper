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

TERM_DROPDOWN = (By.ID, 'ddlTerm')
SCHOOL_DROPDOWN = (By.ID, 'ddlSchool')
STATUS_DROPDOWN = (By.ID, 'ddlStatus')	
SUBJECT_DROPDOWN = (By.ID, 'ddlDept')
driver = webdriver.Chrome('chromedriver.exe')
driver.get("https://cdcs.ur.rochester.edu/")	

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

	for subject in subject_list:
		subject_comprehend(subject)


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
	for table in tables:
		data = []
		tbody = table.find('tbody')
		rows = tbody.find_all('tr')
		for row in rows:
			cols = row.find_all('td')
			cols = [ele.text.strip() for ele in cols]
			data.append([ele for ele in cols if ele])
		print(data)

main()


