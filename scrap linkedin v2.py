
from matplotlib.style import available

from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from openpyxl import load_workbook
from selenium.webdriver.common.keys import Keys



login_email = "mail" #LinkedIn email 
login_password = "password" #LinkedIn password
salesops = ["Sales Operations Manager" , "Sales Operations" , "SalesOps" , "Sales Ops"]
sdrbdr = ["SDR", "BDR", "sales development representative" , "business development representative" , "partnership development representative" , "sales representative" , "account representative" , "sales manager"]
positions = ["Sales" ,"Business","Partnership","Account Executive", "SDR", "BDR"]
companies_list = ["https://www.linkedin.com/company/oxus-ai/" , "https://www.linkedin.com/company/dwellgreen-llc/", "https://www.linkedin.com/company/amazon/"]



driver = webdriver.Firefox("path to geckodriver")
driver.get("https://linkedin.com/uas/login")

time.sleep(1)
username = driver.find_element_by_id("username")

username.send_keys(login_email)  

pword = driver.find_element_by_id("password")
time.sleep(1)

pword.send_keys(login_password)        
time.sleep(1)
driver.find_element_by_xpath("//button[@type='submit']").click()

time.sleep(2)
if driver.current_url.startswith("https://www.linkedin.com/checkpoint/challenge"):
    time.sleep(30)




for link in companies_list:
    searchlist= []
    driver.get(link+"about")
    time.sleep(2)
    src = driver.page_source
    soup = BeautifulSoup(src, 'lxml')
    companyname = soup.find('h1',{'class':'t-24 t-black t-bold full-width'}).get('title')
    companyname = companyname.split(" ")
    for i in range(len(companyname)):
        if companyname[i]=="inc" or companyname[i]=="ghmb" or companyname[i]=="uab" or companyname[i]=="ltd" :
            companyname.remove(companyname[i])
            companyname = " ".join(companyname)
            break
    if type(companyname) == list:
        companyname = ' '.join(companyname)
    if len(companyname)>5:
        companyname = companyname.title()
    print(companyname)


    names = soup.find_all('dt',{'class' : 'mb1 text-heading-small'})
    values = soup.find_all('dd',{'class':'mb4 text-body-small t-black--light'})
    for i in range(len(names)):
        names[i] = names[i].text.strip()
    for i in range(len(values)):
        values[i] = values[i].text.strip()


    employee_nb = soup.find('dd',{'class':'text-body-small t-black--light mb4'})
    if employee_nb!=None:
        employee_nb = employee_nb.text.split("on")[0].strip()
    else:
        employee_nb = "Not found on LinkedIn"
    if "Headquarters" in names:
        indice = names.index("Headquarters")
        if "Company size" in names:
            hq = values[indice-1]
        else:
            hq = values[indice]
    else: 
        hq="Not found on linkedin profile"
    if "Website" in names:
        indice = names.index("Website")
        website = values[indice]
    print(hq)
    print(employee_nb)
    print(website)
    
    searchlist.append([companyname, link, hq])

    
    
    
    for elem in searchlist : 
        link = elem[1]
        companyname = elem[0]
        driver.get(link+"posts/?feedView=all")
        time.sleep(1)
        driver.find_element_by_css_selector(".artdeco-dropdown__trigger.artdeco-dropdown__trigger--placement-bottom.ember-view.display-flex.t-normal.t-12.t-black--light").click()
        time.sleep(2)
        try:
            driver.find_element_by_css_selector(".artdeco-button.artdeco-button--muted.artdeco-button--1.artdeco-button--full.artdeco-button--tertiary.ember-view.justify-flex-start.ph4").click()
        except:
            driver.find_element_by_css_selector(".artdeco-dropdown__trigger.artdeco-dropdown__trigger--placement-bottom.ember-view.display-flex.t-normal.t-12.t-black--light").click()
            time.sleep(2)
            try:
                driver.find_element_by_css_selector(".artdeco-button.artdeco-button--muted.artdeco-button--1.artdeco-button--full.artdeco-button--tertiary.ember-view.justify-flex-start.ph4").click()
            except Exception as e:
                print(e)
        time.sleep(2)

        src=driver.page_source
        soup =  BeautifulSoup(src, 'lxml')
        activity = soup.find('div',{'class':'scaffold-finite-scroll__content'})
        if activity!=None:
            activity = activity.find('span', {'aria-hidden':"true"}).text
            if "h" in activity or "d" in activity or "w" in activity or activity.startswith('1m'):
                activity = "Profile is active in the last 30 days" 
            else:
                activity = "Profile not active in the last 30 days"
        else:
            activity = "Profile not active at all"        
        time.sleep(3)


        elem.append(website)
        elem.append(employee_nb)
        elem.append(activity)
        available_positions = "available job positions are : "
        driver.get(link+"/jobs/")
        time.sleep(2)
        previouspos = ""
        for position in positions:
            try:
                jobinput = driver.find_element_by_css_selector(".artdeco-typeahead__input.org-jobs-job-search-form-module__typeahead-input")
                jobinput.send_keys(len(previouspos)*Keys.BACKSPACE)
                jobinput.send_keys(position)

                driver.find_element_by_css_selector(".artdeco-button.artdeco-button--primary.artdeco-button--3.flex-shrink-zero").click()
                driver.switch_to.window(driver.window_handles[1])
                time.sleep(5)
                src = driver.page_source
                soup = BeautifulSoup(src,  'lxml')
                pos = soup.select_one('h1' , {'class' : ".t-24.t-black.t-normal.mb5.mt5.text-align-center"}).text
                pos = "".join(pos.split()).lower()

                if pos.startswith("".join(position.split()).lower()):
                    available_positions+= position+"/"

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                previouspos = position
            except Exception as e:
                print(e)
        print(available_positions)
        if available_positions == "available job positions are : ":
            available_positions = "Not actively hiring"
        elem.append(available_positions)


        for jobpos in sdrbdr:
            driver.get(link+"people/?keywords="+jobpos) 
            time.sleep(5)
            src=driver.page_source
            soup =  BeautifulSoup(src, 'lxml')  

            soup = soup.find('span',{'class':'t-20 t-black t-bold'}).text
            
            if "".join(soup.split()) != "0employees":
                sdr = "Has SDR/BDR"
                break
            else:
                sdr = "Doesn't have SDR/BDR"
        
        for jobpos in salesops:
            driver.get(link+"people/?keywords="+jobpos) 
            time.sleep(5)
            src=driver.page_source
            soup =  BeautifulSoup(src, 'lxml')  

            soup = soup.find('span',{'class':'t-20 t-black t-bold'}).text
            
            if "".join(soup.split()) != "0employees":
                ops = "Has sales OPS"
                break
            else:
                ops = "Doesn't have sales OPS"

        elem.append(sdr)
        elem.append(ops)

        websitehas = "Keywords in website : "
        if website!="None":
            driver.get(website)
            time.sleep(1)
            src = driver.page_source
            soup = BeautifulSoup(src, 'lxml')
            text = "".join(soup.text.split())
            for j in ["B2B" , "Help businesses" , "businesses" , "SaaS" , "integrations"]:
                if j.lower() in text.lower():
                    websitehas+=j+" / "
        elem.append(websitehas)
        
        print(elem)


        



    wb = load_workbook("test.xlsx")
    ws = wb.worksheets[0]

    for row_data in searchlist:
        ws.append(row_data)

    wb.save("test.xlsx")


driver.close()