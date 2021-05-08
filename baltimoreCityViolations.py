# Bikram Kohli (bsk4uaa@virginia.edu)
# Web scraping people with tax violations from a PDF and finding their information to contact

import re
import time
import io

import requests
from bs4 import BeautifulSoup
import xlsxwriter
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from PyPDF2 import PdfFileReader
temp = []


# webdrivers
chromedriver = "/Users/bikramkohli/Documents/chromedriver 2"
driver = webdriver.Chrome(chromedriver)
driver2 = webdriver.Chrome(chromedriver)

# Excel worksheet basics
workbook = xlsxwriter.Workbook('330-339vals.xlsx')
worksheet = workbook.add_worksheet('1')
row = 0
worksheet.write(0, 0, "1 - First Name")
worksheet.write(0, 1, "1 - Last Name")
worksheet.write(0, 2, "2 - First Name")
worksheet.write(0, 3, "2 - Last Name")
worksheet.write(0, 4, "Property Street Address")
worksheet.write(0, 5, "City")
worksheet.write(0, 6, "State")
worksheet.write(0, 7, "Zip")
worksheet.write(0, 8, "Mailing Street Address")
worksheet.write(0, 9, "Mailing City")
worksheet.write(0, 10, "Mailing State")
worksheet.write(0, 11, "Mailing Zip")


# regex matching helper function
def match_test(regex, text):
    # Gives a list of all complete matches
    ans = ''
    for match in regex.finditer(text):
        ans += match.group(0)
    return ans


def navigateSite():
    # Opening up site
    driver.get("http://cels.baltimorehousing.org/Search_On_Map.aspx")
    time.sleep(1 / 2)

    # Checking neighborhood box
    neighborhoodID = "ctl00_ContentPlaceHolder1_ck2"
    neighborhoodCheck = driver.find_element_by_id(neighborhoodID).click()

    # Selecting neighborhood
    neighborhoodDropName = "ctl00$ContentPlaceHolder1$lstLoc"
    neighborhoodDrop = Select(driver.find_element_by_name(neighborhoodDropName))
    print("length", len(neighborhoodDrop.options))

    for i in range(330, 339):
        print(i)
        # opening site
        driver.get("http://cels.baltimorehousing.org/Search_On_Map.aspx")
        time.sleep(1 / 2)

        # Checking neighborhood box
        neighborhoodID = "ctl00_ContentPlaceHolder1_ck2"
        neighborhoodCheck = driver.find_element_by_id(neighborhoodID).click()

        # Selecting neighborhood
        neighborhoodDropName = "ctl00$ContentPlaceHolder1$lstLoc"
        neighborhoodDrop = Select(driver.find_element_by_name(neighborhoodDropName))
        neighborhoodDrop.select_by_index(i)

        # Clicking search
        searchID = "ctl00_ContentPlaceHolder1_btSearch"
        search = driver.find_element_by_id(searchID).click()
        findInfo()


def findInfo():
    global row

    # getting all "Vacant"s
    soup = BeautifulSoup(driver.page_source, "html.parser")
    listTR = soup.find_all('td', text=re.compile('Vacant'))

    # getting pdfs for all "vacant"
    for i in range(0, len(listTR)):
        # next row
        if len(listTR) == 0:
            continue
        try:
            # printing address
            print("Neighborhood: ")
            for child in listTR[i].findNext('td').findNext('td').findNext('td').findNext('td').descendants:
                print(child, end='')

            # getting pdf link
            pdfHref = listTR[i].findNext('td').findNext('td').findNext('td').findNext('td').findNext('td').find('a')['href']
            linkFirst = "http://cels.baltimorehousing.org"
            pdfLink = linkFirst + pdfHref[2:]
            print('')
            print(pdfLink)

            # opening pdf
            pdf_response = requests.get(pdfLink)

            # extracting pdf content
            with io.BytesIO(pdf_response.content) as f:
                pdf = PdfFileReader(f)
                information = pdf.getDocumentInfo()
                number_of_pages = pdf.getNumPages()
                txt = f"""
                Author: {information.author}
                Creator: {information.creator}
                Producer: {information.producer}
                Subject: {information.subject}
                Title: {information.title}
                Number of Pages: {number_of_pages}
                """

                numpage = 0
                page = pdf.getPage(numpage)
                page_content = page.extractText()

            # extracting block and lot
            blockLotRE = re.compile(r'(\bBlock:\b)[0-9]{4}|(\bSTBlock:\b)[0-9]{4}|(\bLot:\b)[0-9]{3}')
            blockLotList = match_test(blockLotRE, page_content)
            block = blockLotList[-11:-7]
            lot = blockLotList[-3:]
            print(block, lot)

            # if block AND lot not found
            if len(blockLotList) < 12:
                continue

            try:
                # opening site
                driver2.get("http://sdat.dat.maryland.gov/RealProperty/Pages/default.aspx")
                time.sleep(1)

                # Select county
                countyDropName = "ctl00$ctl00$ctl00$MainContent$MainContent$cphMainContentArea$ucSearchType$wzrdRealPropertySearch" \
                                 "$ucSearchType$ddlCounty"
                countyDrop = Select(driver2.find_element_by_name(countyDropName))
                countyName = "BALTIMORE CITY"
                countyDrop.select_by_visible_text(countyName)

                # Selecting method of searching (map/parcel)
                searchDropName = "ctl00$ctl00$ctl00$MainContent$MainContent$cphMainContentArea$ucSearchType$wzrdRealPropertySearch" \
                                 "$ucSearchType$ddlSearchType"
                searchDrop = Select(driver2.find_element_by_name(searchDropName))
                searchMethod = "MAP/PARCEL"
                searchDrop.select_by_visible_text(searchMethod)

                # Selecting continue
                time.sleep(1)
                continueButtonID = "MainContent_MainContent_cphMainContentArea_ucSearchType_wzrdRealPropertySearch_StartNavigation" \
                                   "TemplateContainerID_btnContinue"
                driver2.find_element_by_id(continueButtonID).click()
                time.sleep(1)

                # Enter block and lot
                blockName = "ctl00$ctl00$ctl00$MainContent$MainContent$cphMainContentArea$ucSearchType$wzrdRealPropertySearch$ucEnterData$txtMap_Block"
                blockBox = driver2.find_element_by_name(blockName)
                blockBox.send_keys(block)

                lotName = "ctl00$ctl00$ctl00$MainContent$MainContent$cphMainContentArea$ucSearchType$wzrdRealPropertySearch$ucEnterData$txtMap_Lot"
                lotBox = driver2.find_element_by_name(lotName)
                lotBox.send_keys(lot)

                # Selecting next
                nextButtonID = "MainContent_MainContent_cphMainContentArea_ucSearchType_wzrdRealPropertySearch_StepNavigationTemplateContainerID_btnStepNextButton"
                driver2.find_element_by_id(nextButtonID).click()
                time.sleep(1)
                print('')
                print('---------')
                print('')

                # getting owner name
                soup2 = BeautifulSoup(driver2.page_source, "html.parser")
                ownerNameA = soup2.find(string="Owner Name:")
                ownerNameTD = ownerNameA.find_parent("td")
                ownerTD = ownerNameTD.find_next_sibling("td")
                owner_name = list(ownerTD.descendants)[2]
                row += 1

                # if 2 listed owners
                if '\n' in owner_name:
                    owner_name = owner_name.splitlines()

                    one_first_name = owner_name[0].split()
                    both_one_last_name = one_first_name[0]
                    one_first_name.pop(0)
                    both_one_first_name = ' '.join([str(elem) for elem in one_first_name])
                    print("1 - First Name:", both_one_first_name)
                    worksheet.write(row, 0, both_one_first_name)
                    print("1 - Last Name:", both_one_last_name)
                    worksheet.write(row, 1, both_one_last_name)

                    two_first_name = owner_name[1].split()
                    both_two_last_name = two_first_name[0]
                    two_first_name.pop(0)

                    both_two_first_name = ' '.join([str(elem) for elem in two_first_name])
                    print("2 - First Name:", both_two_first_name)
                    worksheet.write(row, 2, both_two_first_name)
                    print("2 - Last Name:", both_two_last_name)
                    worksheet.write(row, 3, both_two_last_name)

                # if 1 listed owner
                else:
                    owner_name = owner_name.split()
                    one_last_name = owner_name[0]
                    owner_name.pop(0)
                    one_first_name = ' '.join([str(elem) for elem in owner_name])
                    print("First Name:", one_first_name)
                    worksheet.write(row, 0, one_first_name)
                    print("Last Name:", one_last_name)
                    worksheet.write(row, 1, one_last_name)

                # getting mailing address
                mailing_address = soup2.find('span', {'id': 'MainContent_MainContent_cphMainContentArea_uc'
                                         'SearchType_wzrdRealPropertySearch_ucDetailsSearch_dlstDetais'
                                         'Search_lblMailingAddress_0'})
                mailing_address = mailing_address.get_text("!")

                # getting address
                mailAddressRE = re.compile(r'.+?(?=!)')
                mailAddress = match_test(mailAddressRE, mailing_address)
                print("mailAddress", mailAddress)

                # getting zip code
                mailZipCodeRE = re.compile(r'[0-9]+-[0-9]+')
                mailZipCode = match_test(mailZipCodeRE, mailing_address)
                print("mailZipCode", mailZipCode)

                # getting state
                mailStateRE = re.compile(r'\!(.*).+?(?=[0-9]{5}-)')
                mailState = match_test(mailStateRE, mailing_address)[-3:-1]
                print("mailState", mailState)

                # getting city
                mailCityRE = re.compile(r'\!(.*).+?(?=MD|VA|DE|NJ|PA|WV|NY|NC|TN)')
                mailCity = match_test(mailCityRE, mailing_address)[1:]
                print("mailCity", mailCity)

                # getting premise address
                premise_address = soup2.find('span', {'id': 'MainContent_MainContent_cphMainContentArea_ucSearchType'
                                            '_wzrdRealPropertySearch_ucDetailsSearch_dlstDetaisSearch'
                                            '_lblPremisesAddress_0'})
                premise_address = premise_address.get_text("!")

                # getting address
                premiseAddressRE = re.compile(r'.+?(?=!)')
                premiseAddress = match_test(premiseAddressRE, premise_address[:-5])
                print("premiseAddress", premiseAddress)

                #getting zip code
                premiseZipCodeRE = re.compile(r'[0-9]+-[0-9]+')
                premiseZipCode = match_test(premiseZipCodeRE, premise_address)
                print("premiseZipCode", premiseZipCode)

                premiseCity = "BALTIMORE"
                premiseState = "MD"
                print('')
                print('----')
                print('')

                print(row)
                # writing values to worksheet
                worksheet.write(row, 4, premiseAddress)
                worksheet.write(row, 5, premiseCity)
                worksheet.write(row, 6, premiseState)
                worksheet.write(row, 7, premiseZipCode)
                worksheet.write(row, 8, mailAddress)
                worksheet.write(row, 9, mailCity)
                worksheet.write(row, 10, mailState)
                worksheet.write(row, 11, mailZipCode)
            except:
                print("error")
        except:
            print("error")


navigateSite()
workbook.close()
driver.quit()
driver2.quit()
