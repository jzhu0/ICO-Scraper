'''
Created on Aug 16, 2017

Scrapes through all listed ICOs on smithandcrown.com. Pulls all basic data from the table for each ICO.
Saves to an excel spreadsheet with name=NEW_DATASET_FILENAME.

@author: Jason Zhu
'''
NEW_DATASET_FILENAME = "Smith and Crown Past Projects - 8.17.2017.xlsx"
HARDCODED = False
HARDCODED_LINKS = []

import time
import openpyxl
from selenium import webdriver
from selenium.common.exceptions import InvalidArgumentException

def easy_concat(a, b):
# Comma separates two strings, but checks if either is empty
    if (a == ""):
        return b
    elif (b == ""):
        return a
    else:
        return a + ", " + b

def parse_attributes(attributes_table):
# Parses the detail-col-attribute element, translating icons to type. Returns as comma separated string
    auditable = "https://www.smithandcrown.com/wp-content/uploads/2017/03/ico_transparency_large-2.png"
    detailed = "https://www.smithandcrown.com/wp-content/uploads/2017/01/ident-200.png"
    new_chain = "https://www.smithandcrown.com/wp-content/uploads/2017/01/chain-200.png"
    code = "https://www.smithandcrown.com/wp-content/uploads/2017/01/code-600.png"
    barred = "https://www.smithandcrown.com/wp-content/uploads/2017/06/ico_nous_large.png"
    attributes = ""
    for ele in attributes_table.find_elements_by_tag_name("li"):
        icon = ele.find_element_by_tag_name("img").get_attribute("src")
        if (icon == auditable):
            attributes = easy_concat(attributes, "Auditable Raise Amount")
        elif (icon == detailed):
            attributes = easy_concat(attributes, "Detailed Founder Identities")
        elif (icon == new_chain):
            attributes = easy_concat(attributes, "New Blockchain")
        elif (icon == code):
            attributes = easy_concat(attributes, "Project Code Available")
        elif (icon == barred):
            attributes = easy_concat(attributes, "Sale Barred to U.S. Participants")
        else:
            raise InvalidArgumentException("Unknown icon in attributes")
    return attributes

def index_to_col(index):
# Returns the column letter corresponding to the index returned from founded_list
    if (index < 26):
        return str(chr(index+65))
    else:
        raise InvalidArgumentException("index shouldn't be this high")

def generate_workbook():
    new_data = openpyxl.Workbook()
    new_data1 = new_data.active
    new_data1.title = "Sheet 1"
    new_data1['A1'] = "Project Name"
    new_data1['B1'] = "Report Type"
    new_data1['C1'] = "Description"
    new_data1['D1'] = "Attributes"
    new_data1['E1'] = "Start Date"
    new_data1['F1'] = "End Date"
    new_data1['G1'] = "Amount Raised (USD)"
    new_data1['H1'] = "URL"
    for i in range(0, 8):
        new_data1.column_dimensions[index_to_col(i)].width = 30
    new_data1.row_dimensions[1].height = 30
    
    return new_data

driver = webdriver.Chrome()
driver.get("https://www.smithandcrown.com/icos/")
time.sleep(0.5)

tables = driver.find_elements_by_class_name("table-responsive")

new_data = generate_workbook()
new_data1 = new_data.active
row = 2

for table in tables:
    body = table.find_element_by_tag_name("tbody")
    for table_row in body.find_elements_by_tag_name("tr"):
        name = table_row.find_element_by_class_name("detail-col-name").text
        if (name == ""):
            continue
        report = table_row.find_element_by_class_name("detail-col-report").text
        if (report == ""):
            report = "None"
        description = table_row.find_element_by_class_name("detail-col-descr").text
        if (description == ""):
            description = "None"
        attributes_table = table_row.find_element_by_class_name("detail-col-attribute")
        attributes = parse_attributes(attributes_table)
        if (attributes == ""):
            attributes = "None"
        dates = table_row.find_elements_by_class_name("detail-col-date")
        start = dates[0].text
        end = dates[1].text
        if (start == ""):
            start = "None"
        if (end == ""):
            end = "None"
        amount = table_row.find_element_by_class_name("field-raised").text
        if (amount == "--" or amount == ""):
            amount = "N/A"
        url = table_row.get_attribute("data-url")
        if (url == ""):
            url = "N/A"
        
        print "Name: " + name
        print "Report: " + report
        print "Description: " + description
        print "Attributes: " + attributes
        print "Start: " + start
        print "End: " + end
        print "Amount: " + amount
        print "Url: " + url
        
        new_data1['A' + str(row)] = name
        new_data1['B' + str(row)] = report
        new_data1['C' + str(row)] = description
        new_data1['D' + str(row)] = attributes
        new_data1['E' + str(row)] = start
        new_data1['F' + str(row)] = end
        new_data1['G' + str(row)] = amount
        new_data1['H' + str(row)] = url
        
        new_data1.row_dimensions[row].height = 30
        
        if (row % 5 == 0):
            new_data.save(filename = NEW_DATASET_FILENAME)
        row += 1
        print ""

new_data.save(filename = NEW_DATASET_FILENAME)
print "    All data successfully parsed."
driver.quit()
