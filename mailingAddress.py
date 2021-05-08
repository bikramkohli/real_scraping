# Bikram Kohli (bsk4uaa@virginia.edu)
# Web scraping to get mailing address for various property owners

# Importing selenium and BeautifulSoup to access html code and parse through it
# Importing time to help grab html code from different pages with same URL
# Importing re to use regular expressions to check for valid addresses
# Importing xlrd and xlutils.copy to manipulate data between Excel and Python
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time
import re
import xlrd
from xlutils.copy import copy


# Function to validate addresses
def match_test(regex, text):
    # Gives a list of all complete matches
    ans = ''
    for match in regex.finditer(text):
        ans += match.group(0)
    return ans


for i in range(1, 3148):

    # Opening up the given website
    chromedriver = "/Users/bikramkohli/Documents/chromedriver"
    driver = webdriver.Chrome(chromedriver)
    driver.get("https://sdat.dat.maryland.gov/RealProperty/Pages/default.aspx")
    time.sleep(1/2)

    # Select county from drop down menu
    countyDropName = "ctl00$ctl00$ctl00$MainContent$MainContent$cphMainContentArea$ucSearchType$wzrdRealPropertySearch" \
                     "$ucSearchType$ddlCounty"
    countyDrop = Select(driver.find_element_by_name(countyDropName))
    countyName = "BALTIMORE COUNTY"
    countyDrop.select_by_visible_text(countyName)

    # Selecting appropriate method of searching for properties (address)
    searchDropName = "ctl00$ctl00$ctl00$MainContent$MainContent$cphMainContentArea$ucSearchType$wzrdRealPropertySearch" \
                     "$ucSearchType$ddlSearchType"
    searchDrop = Select(driver.find_element_by_name(searchDropName))
    searchMethod = "STREET ADDRESS"
    searchDrop.select_by_visible_text(searchMethod)

    # Selecting the continue button
    time.sleep(1/2)
    continueButtonID = "MainContent_MainContent_cphMainContentArea_ucSearchType_wzrdRealPropertySearch_StartNavigation" \
                       "TemplateContainerID_btnContinue"
    continueButton = driver.find_element_by_id(continueButtonID).click()

    # Opening Excel spreadsheet containing list of properties
    filepath = "/Users/bikramkohli/Documents/PropertyListingData.xlsx"
    wb = xlrd.open_workbook(filepath)
    sheet = wb.sheet_by_index(0)

    try:
        # Finding and entering the address number
        streetNumberName = "ctl00$ctl00$ctl00$MainContent$MainContent$cphMainContentArea$ucSearchType$wzrd" \
                           "RealPropertySearch$ucEnterData$txtStreenNumber"

        streetNumberBox = driver.find_element_by_name(streetNumberName)
        addressNumberRE = re.compile(r'[0-9]+')
        streetNumberBox.send_keys(match_test(addressNumberRE, sheet.cell_value(i, 4)))

        # Finding and entering the street name
        streetNameID = "MainContent_MainContent_cphMainContentArea_ucSearchType_wzrdRealPropertySearch_uc" \
                       "EnterData_txtStreetName"
        streetNameBox = driver.find_element_by_id(streetNameID)
        streetNameRE = re.compile(r'[\sA-Za-z]+[^AVE|RD|LN|DR|ST|CT|PL|SQ|WAY]')
        streetNameBox.send_keys(match_test(streetNameRE, sheet.cell_value(i, 4))[1:-1])

        # Selecting the next button
        nextButtonID = "MainContent_MainContent_cphMainContentArea_ucSearchType_wzrdRealPropertySearch_Step" \
                       "NavigationTemplateContainerID_btnStepNextButton"
        nextButton = driver.find_element_by_id(nextButtonID).click()

        time.sleep(1/2)

        # Selecting appropriate owner and getting mailing address
        try:
            propertyOwner = sheet.cell_value(i, 3)[:15]
            propertyOwnerRE = re.compile('span id=[=_A-Za-z\s\"<>0-9]+' + propertyOwner)
            page_text = driver.page_source
            ownerMatch = match_test(propertyOwnerRE, page_text)[9:-30]
            clickOnDude = driver.find_element_by_id(ownerMatch).click()
            time.sleep(1/2)

        except:
            print("")

        soup = BeautifulSoup(driver.page_source, "html.parser")
        rb = xlrd.open_workbook('mailingAddressSheet.xls')
        wb = copy(rb)
        w_sheet = wb.get_sheet(0)
        w_sheet.write(i, 0, soup.find('span', {'id': 'MainContent_MainContent_cphMainContentArea_uc'
                                                     'SearchType_wzrdRealPropertySearch_ucDetailsSearch_dlstDetais'
                                                     'Search_lblMailingAddress_0'}).text.strip())
        w_sheet.write(0, 0, 'Mailing Addresses')
        wb.save('mailingAddressSheet.xls')
        driver.close()
        time.sleep(1/2)
    except:
        driver.close()
        time.sleep(1/2)
        continue
