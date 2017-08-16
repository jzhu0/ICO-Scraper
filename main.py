'''
Created on Aug 15, 2017

@author: Jason Zhu
'''
NEW_DATASET_FILENAME = "ICOrating Past Projects - 8.16.2017.xlsx"
HARDCODED = False
HARDCODED_LINKS = ["http://icorating.com/project/2/Decent",
                   "http://icorating.com/project/107/district0x",
                   "http://icorating.com/project/172/bhotspot"]

import time
import openpyxl
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, InvalidArgumentException

def goto_past_ICOs(driver):
    if not (HARDCODED):
        driver.get("http://www.icorating.com/")
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

def parse_project(driver):
# parse_project:
# Parses the ICOrating project page, and returns the data as a list.
# [0] = Project Name
# [1-10] = Overview
# [11-14] = Progress
# [15-17] = Tabs->Project Details
# [18-25] = Tabs->ICO Details
# [26-29] = Tabs->Tech
# [30] = Tabs->Team
# [31] = Summary
    project_data = []
    title = get_title(driver)
    project_data.append(title)
    print "Parsing " + project_data[0]
    print "  title...done"
    
    overview_data = get_overview(driver)
    project_data.extend(overview_data)
    print "  overview...done"
    
    time.sleep(0.5)   #progress takes some time to load
    progress_data = get_progress(driver)
    project_data.extend(progress_data)
    print "  progress...done"
    
    tab_data = get_tabs(driver)
    project_data.extend(tab_data)
    print "  tabs...done"
    
    summary = get_summary(driver)
    project_data.append(summary)
    print "  summary...done"
    
    ''' testing:
    for i in range(0, len(project_data)):
        try:
            ele = str(project_data[i])
        except UnicodeEncodeError:
            ele = project_data[i].encode('utf-8')
        print str(i) + ": " + ele
    '''
    
    return project_data

def get_title(driver):
# Returns the project title, or -1 if not found.
    try:
        title = driver.find_element_by_class_name("ico-name-title").text
    except NoSuchElementException:
        print "  No title found."
        return -1
    return title

def parse_founded(year_loc):
# Formats the overview->founded data to be a list.
# [0-1] = year, location. Defaults to -1 if either is not available.
    split = year_loc.split(", ")
    founded_list = [-1,-1]
    if (len(split) == 0 or year_loc == ""):
        return founded_list
    elif (len(split) == 1):
        try:
            # if only available info is year
            int(split[0])
            founded_list[0] = split[0]
        except ValueError:
            # if only available info is location
            founded_list[1] = split[0]
        return founded_list
    elif (len(split) == 2):
        return split
    elif (len(split) == 3):
        # year, city, state format
        founded_list[0] = split[0]
        founded_list[1] = split[1] + ", " + split[2]
    else:
        raise InvalidArgumentException("overview->founded contained 4 pieces")
    return founded_list

def get_overview(driver):
# Returns a list containing all information from the overview.
# [0-9] = deep rating, hype score, risk score. invest score. category. description
#            founded year, founded location, all links (comma separated), other.
# If no overview information, defaults to -1.
    overview_data = [-1,-1,-1,-1,-1,-1,-1,-1,-1,"N/A"]
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
            founded = contents[1].text
            founded_list = parse_founded(founded)
            overview_data[6] = founded_list[0]
            overview_data[7] = founded_list[1]
        elif (varname == "Website: "):
            pass
        elif (varname == "Social: "):
            social_table = contents[1].find_element_by_class_name("ico-card-socials")
            all_socials = ""
            for link in social_table.find_elements_by_tag_name("a"):
                name = link.get_attribute("title")
                url = link.get_attribute("href")
                
                name_url = name + ": " + url
                if (all_socials == ""):
                    all_socials = name_url
                else:
                    all_socials = all_socials + ", " + name_url
            overview_data[8] = all_socials
        else:   # ANY OTHER VARIABLES. Saved as comma separated.
            other = varname + ": " + contents[1].text
            if (overview_data[10] == "N/A"):
                overview_data[10] = other
            else:
                overview_data[10] = overview_data[10] + ", " + other
    
    return overview_data

def get_progress(driver):
# Returns a list containing fundraising progress information
# [0-3] = BTC, ETH, USD, other.
# If no fundraising information, defaults to -1.
    progress_data = [-1,-1,-1,"N/A"]
    try:
        progress_table = driver.find_element_by_class_name("ico-progress")
    except NoSuchElementException:
        print "  No fundraising information found."
        return progress_data
    
    table_items = progress_table.find_elements_by_class_name("ico-progress-block")
    for ele in table_items:
        varname = ele.find_element_by_class_name("ico-progress-block__title").text
        value = ele.find_element_by_class_name("ico-progress-block__value").text
        if (varname == "BTC:"):
            progress_data[0] = value
        elif (varname == "ETH:"):
            progress_data[1] = value
        elif (varname == "Total USD:"):
            progress_data[2] = value
        else:   # ANY OTHER CURRENCIES. Saved as comma separated.
            other = varname + ": " + value
            if (progress_data[3] == "N/A"):
                progress_data[3] = other
            else:
                progress_data[3] = progress_data[3] + ", " + other
    return progress_data

def get_tabs(driver):
# Returns a list containing information from all 4 tabs.
# [0-2] = Project details: Features, Similar projects, other.
# [3-10] = ICO details: ICO date, Tokens distribution, Token Sales, 
#            Bounty camping, Escrow, Accepts, other.
# [11-14] = Tech: Technical details, The source code, Proof of developer, other.
# [15] = Team: other.
# If no tab information, defaults to -1.
    tabs_data = [-1,-1,"N/A",
                 -1,-1,-1,-1,-1,-1,"N/A",
                 -1,-1,-1,"N/A",
                 "N/A"]
    description = driver.find_element_by_class_name("ico-description")
    tabs = description.find_element_by_class_name("ico-card-tabs")
    tabs_wrapper = tabs.find_element_by_class_name("ico-card-tabs__wrapper")
    
    tabs_buttons = tabs_wrapper.find_elements_by_class_name("ico-card-tab")
    tabs_content = description.find_element_by_class_name("ico-card-content")
    tabs_table = tabs_content.find_elements_by_class_name("ico-card-table")
    assert(len(tabs_buttons) == 4)   # All 4 tabs should be present
    
    # PROJECT DETAILS
    tabs_buttons[0].click()
    tab = tabs_table[0]
    for ele in tab.find_elements_by_class_name("ico-card-table__tr"):
        contents = ele.find_elements_by_class_name("ico-card-table__td")
        varname = contents[0].text
        if (varname == "Features: "):
            tabs_data[0] = contents[1].text
        elif (varname == "Similar projects: "):
            tabs_data[1] = contents[1].text
        else:   # ANY OTHER VARIABLES. Saved as comma separated.
            other = varname + ": " + contents[1].text
            if (tabs_data[2] == "N/A"):
                tabs_data[2] = other
            else:
                tabs_data[2] = tabs_data[2] + ", " + other
    
    # ICO DETAILS
    tabs_buttons[1].click()
    tab = tabs_table[1]
    for ele in tab.find_elements_by_class_name("ico-card-table__tr"):
        contents = ele.find_elements_by_class_name("ico-card-table__td")
        varname = contents[0].text
        if (varname == "ICO date: "):
            tabs_data[3] = contents[1].text
        elif (varname == "Tokens distribution: "):
            tabs_data[4] = contents[1].text
        elif (varname == "Token Sales: "):
            tabs_data[5] = contents[1].text
        elif (varname == "Bounty camping: "):
            tabs_data[6] = contents[1].text
        elif (varname == "Escrow: "):
            tabs_data[7] = contents[1].text
        elif (varname == "Accepts: "):
            tabs_data[8] = contents[1].text
        elif (varname == "Dividends: "):
            tabs_data[9] = contents[1].text
        else:   # ANY OTHER VARIABLES. Saved as comma separated.
            other = varname + ": " + contents[1].text
            if (tabs_data[10] == "N/A"):
                tabs_data[10] = other
            else:
                tabs_data[10] = tabs_data[10] + ", " + other
    
    # TECH
    tabs_buttons[2].click()
    tab = tabs_table[2]
    for ele in tab.find_elements_by_class_name("ico-card-table__tr"):
        contents = ele.find_elements_by_class_name("ico-card-table__td")
        varname = contents[0].text
        if (varname == "Technical details: "):
            tabs_data[11] = contents[1].text
        elif (varname == "The source code: "):
            tabs_data[12] = contents[1].text
        elif (varname == "Proof of developer: "):
            tabs_data[13] = contents[1].text
        else:   # ANY OTHER VARIABLES. Saved as comma separated.
            other = varname + ": " + contents[1].text
            if (tabs_data[14] == "N/A"):
                tabs_data[14] = other
            else:
                tabs_data[14] = tabs_data[14] + ", " + other
    
    # TEAM
    tabs_buttons[3].click()
    tab = tabs_table[3]
    for ele in tab.find_elements_by_class_name("ico-card-table__tr"):
        contents = ele.find_elements_by_class_name("ico-card-table__td")
        varname = contents[0].text
        other = varname + ": " + contents[1].text
        if (tabs_data[15] == "N/A"):
            tabs_data[15] = other
        else:
            tabs_data[15] = tabs_data[15] + ", " + other
    
    return tabs_data

def get_summary(driver):
# Returns the project summary, or -1 if not found.
    try:
        summary = driver.find_element_by_class_name("ico-summary")
    except NoSuchElementException:
        print "  No summary found."
        return -1
    
    summary_top = summary.find_element_by_class_name("ico-summary-text")
    try:
        # Clicks the show more button, pulls the rest of summary, then splices off the " Hide" tail text
        summary_top.find_element_by_class_name("js-summary-expand").click()
        summary_bot = summary_top.find_element_by_class_name("ico-summary-more__rest").text[:-5]
    except NoSuchElementException:
        summary_bot = ""
    return summary_top.text + summary_bot

def index_to_col(index):
# Returns the column letter corresponding to the index returned from founded_list
    to_alpha = {26:"AA", 27:"AB", 28:"AC", 29:"AD", 30:"AE", 31:"AF"}
    if (index < 26):
        return str(chr(index+65))
    elif (index < 32):
        return to_alpha[index]
    else:
        raise InvalidArgumentException("founded_list has too many elements")

def generate_workbook():
    new_data = openpyxl.Workbook()
    new_data1 = new_data.active
    new_data1.title = "Sheet 1"
    new_data1['A1'] = "Project Name"
    new_data1['B1'] = "Deep Rating"
    new_data1['C1'] = "Hype Score"
    new_data1['D1'] = "Risk Score"
    new_data1['E1'] = "Invest Score"
    new_data1['F1'] = "Category"
    new_data1['G1'] = "Description"
    new_data1['H1'] = "Year"
    new_data1['I1'] = "Location"
    new_data1['J1'] = "Social Links"
    new_data1['K1'] = "Other overview"
    new_data1['L1'] = "BTC Funding"
    new_data1['M1'] = "ETH Funding"
    new_data1['N1'] = "USD Funding"
    new_data1['O1'] = "Other funding"
    new_data1['P1'] = "Features"
    new_data1['Q1'] = "Similar Projects"
    new_data1['R1'] = "Other project details"
    new_data1['S1'] = "ICO Date"
    new_data1['T1'] = "Tokens Distribution"
    new_data1['U1'] = "Token Sales"
    new_data1['V1'] = "Bounty Camping"
    new_data1['W1'] = "Escrow"
    new_data1['X1'] = "Accepts"
    new_data1['Y1'] = "Dividends"
    new_data1['Z1'] = "Other ICO details"
    new_data1['AA1'] = "Technical Details"
    new_data1['AB1'] = "Source Code"
    new_data1['AC1'] = "Proof of Developer"
    new_data1['AD1'] = "Other tech"
    new_data1['AE1'] = "Other team"
    new_data1['AF1'] = "Summary"
    for i in range(0, 32):
        new_data1.column_dimensions[index_to_col(i)].width = 30
    new_data1.row_dimensions[1].height = 30
    
    return new_data

driver = webdriver.Chrome()
goto_past_ICOs(driver)
time.sleep(0.5)

links = get_homepage_links(driver)
time.sleep(0.5)

new_data = generate_workbook()
new_data1 = new_data.active

row = 2
for pURL in links:
    driver.get(pURL)
    time.sleep(0.5)
    project_data = parse_project(driver)
    
    # Put into excel
    for j in range(0, len(project_data)):
        item = project_data[j]
        cell = index_to_col(j) + str(row)
        new_data1[cell] = item
    
    new_data1.row_dimensions[row].height = 30
    
    if (row % 5 == 0):
        new_data.save(filename = NEW_DATASET_FILENAME)
    row += 1

new_data.save(filename = NEW_DATASET_FILENAME)
print "    All data successfully parsed."
driver.quit()
