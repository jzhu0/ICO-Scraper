'''
Created on Aug 15, 2017

,
                   "http://icorating.com/project/12/Wings",
                   "http://icorating.com/project/107/district0x",
                   "http://icorating.com/project/14/Golos"
@author: Jason Zhu
'''
DATASET_NAME = "ICOrating Scrape"
HARDCODED = True
HARDCODED_LINKS = ["http://icorating.com/project/2/Decent"]
ERROR_PROJECTS = []

import time
from bs4 import BeautifulSoup
import openpyxl
from selenium import webdriver

def goto_past_ICOs(driver):
    if not (HARDCODED):
        past_tab = driver.find_elements_by_class_name("js-projects-tab")[6]
        past_tab.click()
    return

def get_homepage_links(driver):
    if (HARDCODED):
        return HARDCODED_LINKS
    links = []
    # Absolute xpath for table of assessed projects
    assessed_table = driver.find_element_by_xpath("/html/body/div/div[3]/div[1]/div/div[2]/div[4]/div/table/tbody")
    for project in assessed_table.find_elements_by_tag_name("tr"):
        pURL = project.get_attribute("data-href")
        pURL = "http://icorating.com" + pURL
        links.append(pURL)
        print "Added link: " + pURL
    # Absolute xpath for table of unassessed projects
    unassessed_table = driver.find_element_by_xpath("/html/body/div/div[3]/div[1]/div/div[2]/div[7]/div/table/tbody")
    for project in unassessed_table.find_elements_by_tag_name("tr"):
        pURL = project.get_attribute("data-href")
        pURL = "http://icorating.com" + pURL
        links.append(pURL)
        print "Added link: " + pURL
    print "    All links successfully parsed"
    return links

# parse_project:
# Parses the ICOrating project page, and returns the data as a list.
# [0] = Project Name
# [1-9] = Overview: 
#        [1] deep rating
#        [2] hype score
#        [3] risk score
#        [4] invest score
#        [5] category
#        [6] description
#        [7] founded year
#        [8] founded location
#        [9] list containing all social links (including website)

def parse_project(driver):
    project_data = []
    title = get_title(driver)
    project_data.append(title)
    print "Parsing " + project_data[0]
    print "  title...done"
    
    overview_data = get_overview(driver)
    if (overview_data == "error"):
        ERROR_PROJECTS.append(title + "overview")
        project_data.extend([0,0,0,0,0,0,0,0])
        print "  overview...ERROR"
    else:
        project_data.extend(overview_data)
        print "  overview...done"
    
    
    return project_data

# Returns the project title
def get_title(driver):
    title = driver.find_element_by_class_name("ico-name-title").text
    return title

# Returns a list containing all 8 elements from the overview, or "error" if number of elements != 8
def get_overview(driver):
    overview_data = []
    overview = driver.find_element_by_class_name("ico-overview")
    # deep rating
    header = overview.find_element_by_class_name("clearfix")
    deep_rating = header.find_element_by_class_name("ico-card-score")
    rating = deep_rating.find_element_by_class_name("ico-card-score__status").text
    overview_data.append(rating)
    
    table = overview.find_element_by_class_name("ico-card-table")
    table_items = table.find_elements_by_class_name("ico-card-table__tr")
    # if overview table does not have all 8 sections, note it and skip
    if (len(table_items) != 8):
        return "error"
    # hype score
    hype_ele = table_items[0].find_elements_by_class_name("ico-card-table__td")
    assert(hype_ele[0].text == "Hype score: ")
    overview_data.append(hype_ele[1].text)
    # risk score
    risk_ele = table_items[1].find_elements_by_class_name("ico-card-table__td")
    assert(risk_ele[0].text == "Risk score: ")
    overview_data.append(risk_ele[1].text)
    # invest score
    invest_ele = table_items[2].find_elements_by_class_name("ico-card-table__td")
    assert(invest_ele[0].text == "Invest score: ")
    overview_data.append(invest_ele[1].text)
    # category
    category_ele = table_items[3].find_elements_by_class_name("ico-card-table__td")
    assert(category_ele[0].text == "Category: ")
    overview_data.append(category_ele[1].text)
    # description
    desc_ele = table_items[4].find_elements_by_class_name("ico-card-table__td")
    assert(desc_ele[0].text == "Description: ")
    overview_data.append(desc_ele[1].text)
    # founded
    found_ele = table_items[5].find_elements_by_class_name("ico-card-table__td")
    assert(found_ele[0].text == "Founded: ")
    founded = found_ele[1].text.split(", ")
    overview_data.extend(founded)
    # website: no need because it is also in social
    # social
    social_ele = table_items[7].find_elements_by_class_name("ico-card-table__td")
    assert(social_ele[0].text == "Social: ")
    social_table = social_ele[1].find_element_by_class_name("ico-card-socials")
    all_socials = {}
    for link in social_table.find_elements_by_tag_name("a"):
        name = link.get_attribute("title")
        url = link.get_attribute("href")
        all_socials[name] = url
    overview_data.append(all_socials)
    
    return overview_data

driver = webdriver.Chrome()

driver.get("http://www.icorating.com/")
goto_past_ICOs(driver)
time.sleep(0.5)

links = get_homepage_links(driver)
time.sleep(0.5)

for pURL in links:
    driver.get(pURL)
    time.sleep(0.5)
    
    #html = driver.page_source
    #data = BeautifulSoup(html, "html.parser")
    #time.sleep(0.5)
    
    project_data = parse_project(driver)
    # Put into excel

print "    All data successfully parsed."
driver.quit()
