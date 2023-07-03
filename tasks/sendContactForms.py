from re import I
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import requests
import requests
import colorama
import time
import sys
import csv
from selenium.webdriver.chrome.service import Service as ChromeService

# init the colorama module
colorama.init()
RED = colorama.Fore.RED
GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
CAPTCHA_API_KEY = '4e178e32b76aaa742cf48ae452fd7ec2'

inputFields = {
    "name": "",
    "email": "",
    "phone": "",
    "subject": "",
    "message": "", 
    "company": "",
    "department": "", 
    "skype": "",
    "address": "",
    "website": ""
}

status = {
    "name": 0,
    "email": 0,
    "phone": 0,
    "subject": 0,
    "message": 0, 
    "company": 0,
    "department": 0, 
    "skype": 0,
    "address": 0,
    "website": 0
}
summaryText = "Summary information: \n"
# keywords describing input fields optional names
keyword = {
    "xpath" : ["@id", "@name", "@class", "@type", "placeholder"],
    "Name" : ["Name", "name", "Title", "title", "Login", "login", "Naam", "naam", "register_nume", "שם מלא"],
    "Email" : ["Email", "email", "Mail", "mail", "מייל", "אימייל"],
    "Phone" : ["Phone", "phone", "Number", "number", "Mobile", "mobile", "טלפון"],
    "Subject" : ["Subject", "subject", "subiect", "נושא"],
    "Message" : ["Message", "message", "Content", "content", "text", "txtComments", "your-message", "הודעה"],
    "Captcha" : ["captcha", "gcaptcha", "recaptcha"],
    "Checkbox" : ["checkbox"],
    "Button" : ["Submit", "submit", "Register", "register", "Send", "send", "שלח"],
    "Company" : ["Company", "company", "חברה"],
    "Department" : ["Department", "department"],
    "Address" : ["Address", "address", "כתובת"],
    "Website" : ["Website", "website", "Site", "site", "URL", "url", "אתר"],
    "Submit" : ["Submit", "submit", "שלח", "send", "Send"]
}

def update_context(url, subject, context):
    domain = url.split("/")
    domain = domain[2].split(".")
    inputFields["subject"] = subject.replace("{{domain}}", domain[1])
    inputFields["message"] = context.replace("{{domain}}", domain[1])

def fill_form():
    global summaryText
    fields_list = {   
            "Name" : 0, 
            "Email" : 0,
            "Phone" : 0,
            "Subject" : 0,
            "Message" :0}


    fields_list = find_and_fill_elements_on_site(fields_list, 'Name')
    fields_list = find_and_fill_elements_on_site(fields_list, 'Email')
    fields_list = find_and_fill_elements_on_site(fields_list, 'Phone')
    fields_list = find_and_fill_elements_on_site(fields_list, 'Subject')
    fields_list = find_and_fill_elements_on_site(fields_list, 'Message')
    fields_list = find_and_fill_elements_on_site(fields_list, 'Company')
    fields_list = find_and_fill_elements_on_site(fields_list, 'Department')
    fields_list = find_and_fill_elements_on_site(fields_list, 'Address')
    fields_list = find_and_fill_elements_on_site(fields_list, 'Website')

    print(f" └───{GRAY} [~] Looking for Captcha... {RESET}", end="\r")  
    
    captcha_result = try_captcha()
    
    if captcha_result == "No captcha":
        print(f" └───{GRAY} [~] {captcha_result}!                      {RESET}") 
        fields_list = find_and_fill_elements_on_site(fields_list, 'Submit')
    elif captcha_result == 'Has Captcha but cannot solve':
        print(f" └───{RED} [-] Captcha: ❌             {RESET}") 
        print(f"      └───{GRAY} [~] {captcha_result} {RESET}")
        summaryText += f" └─── [-] Captcha: fail             "
    else:           
        print(f"      └───{GRAY} [~] Solving captcha..{RESET}", end="\r")       
        did_solve = solve_captcha(CAPTCHA_API_KEY, captcha_result, driver)
    
        if did_solve:
            fields_list = find_and_fill_elements_on_site(fields_list, 'Submit')
            print(f" └───{GREEN} [-] Captcha: ✔️                   {RESET}") 
        else:
            print(f" └───{RED} [-] Captcha: ❌                   {RESET}") 
            print(f"      └───{GRAY} [~] Failed to solve captcha! {RESET}")
            summaryText += f" └─── [-] Captcha: fail             "
    print(fields_list)
    return fields_list

def find_and_fill_elements_on_site(fields_list, field):
    for path in keyword['xpath']:
        input_elements = find_elements_on_site(field, path)

        if input_elements:
            return fill_elements_on_site(input_elements, fields_list, field)
    return fields_list

def find_elements_on_site(field, path):

    try:
        if field == "Submit":
            try:
                input_elements = driver.find_elements(By.XPATH, '//form//button[@type="submit"]')
                if (not input_elements):
                    for word in keyword["Submit"]:
                        input_elements += driver.find_elements(By.XPATH, f'//form//a[contains(@id, "{word}")]')
            except:
                pass
        elif field == "Captcha":
            conditions = " or ".join([f"contains({path}, '%s')" % x for x in keyword['Captcha'] ])
            expression = "//*[%s]" % conditions
            input_elements = WebDriverWait(driver, 2).until(EC.visibility_of_element_located((By.XPATH, expression)))
        elif field == "Message": # message can be either a textarea or a normal input, so we need to check both
            try:
                input_elements = driver.find_elements(By.XPATH, "//textarea")
            except:
                pass
        else:
            conditions = " or ".join([f"contains({path}, '%s')" % x for x in keyword[f'{field}'] ])
            expression = "//input[%s]" % conditions
            input_elements = driver.find_elements(By.XPATH, expression)
    except Exception as e:
        input_elements = []
    
    return input_elements

def find_exists_form_element(fields_list):
    for path in keyword['xpath']:
        for field in fields_list:
            try:
                conditions = " or ".join([f"contains({path}, '%s')" % x for x in keyword[f'{field}'] ])
                expression = "//input[%s]" % conditions
                return driver.find_elements(By.XPATH, expression)[0]
            except:
                continue

def fill_elements_on_site(input_elements, fields_list, field):
    global summaryText
    for input_element in input_elements:
        if input_element.is_displayed():
            try:
                if field == "Submit":   
                    file_name = f'submited_{driver.current_url.split(".")[1]}.png'
                    driver.get_screenshot_as_file("before-" + file_name) #save screenshot 
                    input_element.click()
                    print(f" └───{GRAY} [~] Submiting... {RESET}", end="\r")  
                    time.sleep(4)

                    try:
                        # if can access element then its exists
                        input_element.get_attribute("id")
                        print(f" └─── {RED}[+] {field}: ❌      {RESET}")
                        summaryText += f" └─── [+] {field}: fail      \n"
                        
                    except Exception as e: 
                        print(f" └─── {GREEN}[+] {field}: ✔️         {RESET}")
                        summaryText += f" └─── [+] {field}: success      \n"
                        driver.get_screenshot_as_file("after-" + file_name) #save screenshot

                else:
                   
                    if field == "Name":
                        new_field = inputFields["name"]
                    elif field == "Email":
                        new_field = inputFields["email"]
                    elif field == "Phone":
                        new_field = inputFields["phone"]
                    elif field == "Subject":
                        new_field = inputFields["subject"]
                    elif field == "Message":
                        new_field = inputFields["message"]
                    elif field == "Company":
                        new_field = inputFields["company"]
                    elif field == "Department":
                        new_field = inputFields["department"]
                    elif field == "Address":
                        new_field = inputFields["address"]
                    elif field == "Website":
                        new_field = inputFields["website"]

                    input_value = input_element.get_attribute('value')
                    if input_value != new_field and input_value == "":
                        input_element.send_keys(new_field)
                        fields_list[field] = 1
                        print(f" └─── {GREEN}[+] {field}: ✔️ {RESET}")
                        summaryText += f" └─── [+] {field}: success      \n"
                        break
                    if field == "Name":
                        continue
                    elif field == "Email":
                        continue
                    else:
                        return fields_list
            except Exception as e: 
                #print(e)
                print(f" └───{RED} [-] {field}: ❌ {RESET}")
                summaryText += f" └─── [+] {field}: fail      \n"
                if field == "Submit":
                    print(f"      └───{GRAY} [~] Can't be clicked {RESET}")
                    if e == TimeoutException:
                        print(f"      └───{GRAY} [~] Did not proceed {RESET}")
                else:
                    print(f"      └───{GRAY} [~] Can't be filled automaticlly {RESET}")
                continue
    return fields_list

def try_captcha():
    for path in reversed(keyword['xpath']):
        try:
            data = find_elements_on_site("Captcha", path)
            if (data.get_attribute('data-sitekey') is not None):
                return data.get_attribute('data-sitekey')
            else: 
                return "Has Captcha but cannot solve"
        except:
            continue
    return "No captcha"

def solve_captcha(API_KEY, data, driver):
    u1 = f"https://2captcha.com/in.php?key={API_KEY}&method=userrecaptcha&googlekey={data}&pageurl={driver.current_url}&json=1&invisible=1"
    r1 = requests.get(u1)
    rid = r1.json().get("request")
    if (rid == "ERROR_WRONG_GOOGLEKEY"):
        return False
    u2 = f"https://2captcha.com/res.php?key={API_KEY}&action=get&id={int(rid)}&json=1"
    time.sleep(5)
    con = 0
    while True:
        con += 1
        r2 = requests.get(u2)
        if r2.json().get("status") == 1:
            form_tokon = r2.json().get("request")
            break
        time.sleep(5)
    try:
        driver.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML = "{form_tokon}";')
    except:
        return False 
    time.sleep(1)
    return True

def extractInputData(data_filename):
    with open(data_filename, encoding='utf-8-sig') as f:
        lines = f.readlines()
        for line in lines:
            splited = line.split('-')
            if(len(splited) == 1): # is a message
                inputFields["message"] = inputFields["message"] + splited[0].strip() + "\n"

            try: 
                field = splited[0].lower().strip()
                inputFields[field] = splited[1].strip()
            except:
                continue

def getData():
    for field in inputFields:
        print(f"{RESET}Enter {field}: {GRAY}", end="")
        inputFields[field] = input()

def update_summary():
    with open('output/fill_forms_summary.txt', 'w', encoding="utf-8") as file:
        file.write(summaryText)

def simpleRun(contact_urls, userInformation):
    global driver
    global inputFields 
    inputFields = userInformation

    options = Options()
    #options.add_argument("--headless")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.set_page_load_timeout(6)

    ################################################################
    #   Find && Fill information form
    ################################################################
    unhandledUrls = []
    for url in contact_urls:
        if not url: continue
        if "error" in url: continue

        url = url.strip('\n')
        url = url.replace('\t', '')
        try:
            driver.switch_to.new_window()
            driver.get(url)
            base_url = driver.current_url
        except:
            print(f"{RED}[-] Site {url} can't be accessed at the moment.{RESET}")
            continue

        # update the current site url as the addressee in the subject and text
        update_context(url, inputFields["subject"], inputFields["message"])
        
        print(f"{GREEN}[+] Seraching for Form in {url} {RESET}")
        
        try:
            content = driver.find_element(By.XPATH, "//form[1]")
            fill_form() 
        except Exception as e:
            unhandledUrls.append(url)
            print(f"{RED}[-] Site {url} can't be filled automaticlly.{RESET}")
            continue     
    return summaryText
    driver.close()
    print('[~] Finished!') 

def run():
    ################################################################
    #   Get the wanted sites URLS
    ################################################################
    print("""\

             _____                _                 _     _____         _      _              
            /  __ \              | |               | |   /  ___|       (_)    | |             
            | /  \/  ___   _ __  | |_   __ _   ___ | |_  \ `--.  _ __   _   __| |  ___  _ __  
            | |     / _ \ | '_ \ | __| / _` | / __|| __|  `--. \| '_ \ | | / _` | / _ \| '__| 
            | \__/\| (_) || | | || |_ | (_| || (__ | |_  /\__/ /| |_) || || (_| ||  __/| |    
            \____/  \___/ |_| |_| \__| \__,_| \___| \__| \____/ | .__/ |_| \__,_| \___||_|    
                                                                | |                         \  /
                                                                |_|                          \/ 3 """)
    print(f'{GRAY}Starting...{RESET}')

    contact_urls = []
    file = open('input/contact_Urls.csv', 'r')
    file = csv.DictReader(file)
    for col in file:
        contact_urls.append(col['contact_page'])

    print(f'{GREEN}[+] Successfully extracted urls. {RESET}')

    ################################################################
    #   Get the user information
    ################################################################
    driver_path = "chromedriver"
    options = Options()
    options.add_argument("--headless")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    s = Service(driver_path)
    driver = webdriver.Chrome(service=s, options=options)
    driver.set_page_load_timeout(5)

    # try read from file
    try:
        if (sys.argv[1]):
            extractInputData(sys.argv[1])
        else:
            getData()
    except Exception as e:
        print(f"{RED}[-] Couldn't extract data from file (Try 'python contact_pider_v3.py yourFileName.txt'){RESET}")


        getData()


    ################################################################
    #   Find && Fill information form
    ################################################################
    unhandledUrls = []
    for url in contact_urls:
        if not url: continue
        if "error" in url: continue

        url = url.strip('\n')
        url = url.replace('\t', '')
        try:
            driver.switch_to.new_window()
            driver.get(url)
            base_url = driver.current_url
        except:
            print(f"{RED}[-] Site {url} can't be accessed at the moment.{RESET}")
            continue

        # update the current site url as the addressee in the subject and text
        update_context(url, inputFields["subject"], inputFields["message"])
        
        print(f"{GREEN}[+] Seraching for Form pages in {url} {RESET}")
        summaryText += f"- {url}\n"
        try:
            content = driver.find_element(By.XPATH, "//form[1]")
            print(fill_form())
        except:
            unhandledUrls.append(url)
            print(f"{RED}[-] Site {url} can't be filled automaticlly.{RESET}")
            summaryText += f"[-] Site {url} can't be filled automaticlly \n"
            continue   
        finally:
            update_summary()     
    
    driver.close()
    print('[~] Finished!') 

if __name__ == "__main__":
    contact_urls = ["https://www.pais.co.il/contactus/contact_us.aspx"]
    simpleRun(contact_urls, inputFields)

        
