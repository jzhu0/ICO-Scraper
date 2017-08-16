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
# [1-10] = Overview: 

def parse_project(driver):
    project_data = []
    title = get_title(driver)
    project_data.append(title)
    print "Parsing " + project_data[0]
    print "  title...done"
    
    overview_data = get_overview(driver)
    project_data.extend(overview_data)
    print "  overview...done"
    
    progress_data = get_progress(driver)
    project_data.extend(progress_data)
    print "  progress...done"
    
    tab_data = get_tabs(driver)
    project_data.extend(tab_data)
    print "  tabs...done"
    
    return project_data

def get_title(driver):
# Returns the project title
    title = driver.find_element_by_class_name("ico-name-title").text
    return title

def get_overview(driver):
# Returns a list containing all information from the overview.
# [0-9] = deep rating, hype score, risk score. invest score. category. description
#            founded year, founded location, list of all links, other.

    overview_data = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
    overview = driver.find_element_by_class_name("ico-overview")
    # deep rating
    header = overview.find_element_by_class_name("clearfix")
    deep_rating = header.find_element_by_class_name("ico-card-score")
    rating = deep_rating.find_element_by_class_name("ico-card-score__status").text
    overview_data[0] = rating
    
    table = overview.find_element_by_class_name("ico-card-table")
    table_items = table.find_elements_by_class_name("ico-card-table__tr")
    
    for ele in table_items:
        contents = ele.find_elements_by_class_name("ico-card-table__td")
        varname = contents[0].text
        if (varname == "Hype score: "):
            overview_data[1] = contents[1].text
        elif (varname == "Risk score: "):
            overview_data[2] = contents[1].text
        elif (varname == "Invest score: "):
            overview_data[3] = contents[1].text
        elif (varname == "Category: "):
            overview_data[4] = contents[1].text
        elif (varname == "Description: "):
            overview_data[5] = contents[1].text
        elif (varname == "Founded: "):
            founded = contents[1].text.split(", ")
            overview_data[6] = founded[0]
            overview_data[7] = founded[1]
        elif (varname == "Website: "):
            pass
        elif (varname == "Social: "):
            social_table = contents[1].find_element_by_class_name("ico-card-socials")
            all_socials = {}
            for link in social_table.find_elements_by_tag_name("a"):
                name = link.get_attribute("title")
                url = link.get_attribute("href")
                all_socials[name] = url
            overview_data[8] = all_socials
        else:   # ANY OTHER VARIABLES. Saved as comma separated.
            other = varname + ": " + contents[1].text
            if (overview_data[10] == -1):
                overview_data[10] = other
            else:
                overview_data[10] = overview_data[10] + ", " + other
    
    return overview_data

def get_progress(driver):
# Returns a list containing fundraising progress information
# [0-3] = BTC, ETH, USD, other.
    progress_data = [-1,-1,-1,-1]
    
    
    return progress_data

def get_tabs(driver):
# Returns a list containing information from all 4 tabs.
# [0-2] = Project details: Features, Similar projects, other.
# [3-9] = ICO details: ICO date, Tokens distribution, Token Sales, 
#            Bounty camping, Escrow, Accepts, other.
# [10-13] = Tech: Technical details, The source code, Proof of developer, other.
# [14] = Team: other.
    tabs_data = [-1,-1,-1,
                 -1,-1,-1,-1,-1,-1,-1,
                 -1,-1,-1,-1,
                 -1]
    
    
    return tabs_data

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
