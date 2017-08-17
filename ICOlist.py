'''
Created on Aug 17, 2017

Scrapes through the "Over" tab on ico-list.com, pulling only the listed ICO names.
Saves to an excel spreadsheet with name=NEW_DATASET_FILENAME.

@author: Jason Zhu
'''
NEW_DATASET_FILENAME = "ICO-list Past Projects - 8.17.2017.xlsx"
LINK = "https://ico-list.com/index.php?m=Index&a=newslist&id=3&p="
MAX_PAGE = -1

import time
import openpyxl
from selenium import webdriver

def get_max_page(driver):
    footer = driver.find_element_by_class_name("page").text
    footer = footer.split(" ")
    num = footer[2]
    max_page = num.split("/")[1]
    return int(max_page)

def get_cur_page(driver):
    footer = driver.find_element_by_class_name("page").text
    footer = footer.split(" ")
    num = footer[2]
    cur_page = num.split("/")[0]
    return int(cur_page)

driver = webdriver.Chrome()
driver.get("https://ico-list.com/index.php?m=Index&a=newslist&id=3&p=1")
time.sleep(0.5)

MAX_PAGE = get_max_page(driver)
print "Total pages: " + str(MAX_PAGE)

names = []

for page in range(1, MAX_PAGE+1):
    driver.get(LINK + str(page))
    time.sleep(0.5)
    print "Parsing page " + str(page),
    while (get_cur_page(driver) != page):
        # Checks the page number - ico-list sometimes messes up the listings
        driver.get(LINK + str(page))
        time.sleep(0.5)
    table = driver.find_element_by_class_name("threadlist")
    table_body = table.find_element_by_tag_name("tbody")
    for row in table_body.find_elements_by_tag_name("tr"):
        name = row.find_elements_by_tag_name("a")[1].text
        names.append(name)
        print ".",
    print "done"

new_data = openpyxl.Workbook()
new_data1 = new_data.active
new_data1.title = "Sheet 1"
new_data1['A1'] = "Project Name"

row = 2
for name in names:
    new_data1['A' + str(row)] = name
    
    if (row % 5 == 0):
        new_data.save(filename = NEW_DATASET_FILENAME)
    row += 1

new_data.save(filename = NEW_DATASET_FILENAME)
print "    All data successfully parsed."
driver.quit()
