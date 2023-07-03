import requests
from os import path
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import colorama
import re
import csv
import time

# init the colorama module
colorama.init()
RED = colorama.Fore.RED
GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET

contact_in_diffrent_languages = ['contact', 'ContactUs', 'contact-us', 'kontakt', 'keep-in-touch', 'be-in-touch', 'impressum', 'over-ons', 'kontakti', 'yhteyshenkilö', 'ota meihin yhteyttä', 'ottaa yhteyttä', 'contatti', 'צור_קשר', 'צור-קשר', 'מלא-פרטים']
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
fieldnames = ['url', 'contact_page', 'email']
total_urls_visited = 0
countVisitedLinks = 0 # count per crawl
contact_urls = {
    "urls": [],
    "external_urls": [],
    "no_form": []
}

def is_url_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return parsed.netloc and parsed.scheme 

def is_find_form(soup):
    try:
        form = soup.find('form')
        return form != None and "search" not in str(form).lower()
    except:
        return False

def is_contactus_url(url):
    if "www" in url:
        if any(contact in url.lower() for contact in contact_in_diffrent_languages):
            if is_site_online(url):
                return True
            
    return False

def get_site_status(url):
    try:
        status = requests.get(url, headers=headers, timeout=2).status_code
        return status
    except Exception as e:
        if "sslerror" in str(e).lower():
            return "SSL error"
        return None

def is_site_online(url):
    return get_site_status(url) == 200

def checkSiteHttp(url):
    url = url.replace("http://","")
    url = url.replace("https://","")
    url = url.replace("www.","")

    if is_site_online("https://www." + url + "/"):
        return True, "https://www." + url + "/"
    elif is_site_online("http://www." + url + "/"):
        return  True, "http://www." + url + "/"
    else:
        return False, "http://www." + url + "/" # default return http url   

def get_email(url):

    # extract all email addresses and add them into the resulting set
    # You may edit the regular expression as per your requirement
    try:
        response = requests.get(url, timeout=5)
        new_emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*(?!\.(?:png|jpg))\.[a-zA-Z0-9]+", response.text, re.I)
        emails = new_emails
    except:
        emails = []

    return emails

def get_all_website_links(url, url_links={"internal_urls": [], "external_urls": []}):
    """
    Add all URLs that is found on `url` to url_links internal_urls and external_urls 
    """

    # domain name of the URL without the protocol
    domain_name = urlparse(url).netloc
    soup = BeautifulSoup(requests.get(url, timeout=3).content, "html.parser")
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None: continue

        # join the URL if it's relative (not absolute link)
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        # remove URL GET parameters, URL fragments, etc.
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path

        if not is_url_valid(href): continue 
        if href in url_links: continue
        if domain_name not in href: 
            # external link
            if href not in url_links["external_urls"]:
                url_links["external_urls"].append(href)
            continue

        url_links["internal_urls"].append(href)

    return url_links

def getAllSiteLinks(url, url_links={"internal_urls": [], "external_urls": []}, max_urls=30):
    """
    Get all gived url links in max_urls depth
    params:
        url_links (dict): must have internal_urls and external_urls keys
        max_urls (int): number of max urls to crawl, default is 30.
    """
    url_links = get_all_website_links(url, url_links)
    global countVisitedLinks
    countVisitedLinks += 1
    for link in url_links["internal_urls"]:

        if countVisitedLinks > max_urls: break

        getAllSiteLinks(link, url_links, max_urls=max_urls)
        global total_urls_visited
        total_urls_visited += 1

    return url_links

def remove_list_duplicates(_list):
    return list(dict.fromkeys(_list))

def handleUrl(url):
        emails = {}
        if not url: return

        global contact_urls
        count_unavailable_urls = 0
        count_contact_forms_urls = 0
        count_contact_urls_without_form = 0
        count_emails = 0
        contact_urls = contact_urls.fromkeys(contact_urls, [])

        url = url.strip()
        
        isAccess, url = checkSiteHttp(url)
        
        ################################################################
        #   Handle unavailable urls
        ################################################################
        if (not isAccess):
            print(f"{RED}[-] Site {url} can't be accessed at the moment.{RESET}")   
            count_unavailable_urls += 1

            status = get_site_status(url)
           
            with open(r'contact_Urls.csv', 'a', newline='', encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
                if csvfile.tell() == 0: # checks if the file already exists with headers then it skips writing headers again.
                    writer.writeheader()
                
                if isinstance(status, int):
                    print(f" └───{GRAY} [~] Got status code error {status} {RESET}")   
                    writer.writerow({'url': url, 'contact_page': status, 'email': ""}) 
                elif status == None: 
                    print(f" └───{GRAY} [~] Got - Site doesn't exists! {RESET}")  
                    writer.writerow({'url': url, 'contact_page': "DNS error", 'email': ""}) 
                elif "error" in str(status).lower():
                    print(f" └───{GRAY} [~] Got - {status}! {RESET}")  
                    writer.writerow({'url': url, 'contact_page': status, 'email': ""}) 
                else:
                    print(f" └───{GRAY} [~] Got - Site doesn't exists! {RESET}")  
                    writer.writerow({'url': url, 'contact_page': "General error", 'email': ""}) 

            return

        print(f"{GRAY}[+] Seraching for contact pages in {url} {RESET}")

        url_links = getAllSiteLinks(url, {"internal_urls": [], "external_urls": []}, 1)
        
        for link in url_links["internal_urls"]:
            if link in contact_urls["urls"]: continue
            if is_contactus_url(link):
                print(f" └───{GREEN} [+] Found contact page: {link} {RESET}")   
                if is_find_form(link):
                    contact_urls["urls"].append(link) 
                else:
                    contact_urls["no_form"].append(link) 
            
        
        for link in url_links["external_urls"]:
            if link in contact_urls["external_urls"]: continue
            if is_contactus_url(link):
                print(f" └───{GREEN} [+] Found external contact page: {link} {RESET}") 
                if is_find_form(link):
                    contact_urls["external_urls"].append(link) 
                else:
                    contact_urls["no_form"].append(link)  
                
        count_contact_forms_urls += len(contact_urls["external_urls"]) + len(contact_urls["urls"])
        count_contact_urls_without_form += len(contact_urls["no_form"])

        emails[url] = get_email(url)
        for email in emails[url]:
            print(f" └───{GREEN} [+] Found email: {email} {RESET}")  
            pass 
            
        final_emails = []
        domain_name = urlparse(url).netloc
        if not emails[url]:
            final_emails = ''
        else:
            emails[url] = remove_list_duplicates(emails[url])
            for email in emails[url]:
                count_emails += 1
                if domain_name.split(".")[1] in email:
                    final_emails.append(email)

        finalContactPages = []
        if not contact_urls["urls"]:
            finalContactPages = ''
        else:
            contact_urls["urls"] = remove_list_duplicates(contact_urls["urls"])
            finalContactPages = contact_urls["urls"][0]
            # for url in contact_urls["urls"]:
            #     finalContactPages.append(url)
        

        # with open('contact_Urls.csv', 'a', newline='', encoding="utf-8") as csvfile:
        #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
        #     if csvfile.tell() == 0: # checks if the file already exists with headers then it skips writing headers again.
        #         writer.writeheader()
        #     writer.writerow({'url': url, 'contact_page': finalContactPages, 'email': ", ".join(final_emails)})

        return {
            "domain_name": url, 
            "contact_page": finalContactPages, 
            "emails_found": ", ".join(final_emails), 
            "no_form": contact_urls["no_form"],
            "reached_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
def Run():
     ################################################################
    #   Get the wanted sites URLS
    ################################################################
    print(f'{GRAY}Starting...{RESET}')

    if (not path.exists("URLS.txt")):
        print(f"{RED}[-] Please create a file called 'URLS.txt' before running this script.{RESET}")
        exit()
    contact_form = open('URLS.txt', 'r', encoding="utf-8")
    urls_list = contact_form.readlines()


    ################################################################
    #   Search for contacts pages 
    ################################################################
    emails = {}
    count_unavailable_urls = 0
    count_contact_forms_urls = 0
    count_contact_urls_without_form = 0
    count_emails = 0
    for url in urls_list:
        if not url: continue

        global contact_urls
        contact_urls = contact_urls.fromkeys(contact_urls, [])

        url = url.strip()
        
        isAccess, url = checkSiteHttp(url)
        
        ################################################################
        #   Handle unavailable urls
        ################################################################
        if (not isAccess):
            print(f"{RED}[-] Site {url} can't be accessed at the moment.{RESET}")   
            count_unavailable_urls += 1

            status = get_site_status(url)
           
            with open(r'contact_Urls.csv', 'a', newline='', encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
                if csvfile.tell() == 0: # checks if the file already exists with headers then it skips writing headers again.
                    writer.writeheader()
                
                if isinstance(status, int):
                    print(f" └───{GRAY} [~] Got status code error {status} {RESET}")   
                    writer.writerow({'url': url, 'contact_page': status, 'email': ""}) 
                elif status == None: 
                    print(f" └───{GRAY} [~] Got - Site doesn't exists! {RESET}")  
                    writer.writerow({'url': url, 'contact_page': "DNS error", 'email': ""}) 
                elif "error" in str(status).lower():
                    print(f" └───{GRAY} [~] Got - {status}! {RESET}")  
                    writer.writerow({'url': url, 'contact_page': status, 'email': ""}) 
                else:
                    print(f" └───{GRAY} [~] Got - Site doesn't exists! {RESET}")  
                    writer.writerow({'url': url, 'contact_page': "General error", 'email': ""}) 

            continue

        print(f"{GRAY}[+] Seraching for contact pages in {url} {RESET}")

        url_links = getAllSiteLinks(url, {"internal_urls": [], "external_urls": []}, 1)
        
        for link in url_links["internal_urls"]:
            if link in contact_urls["urls"]: continue
            if is_contactus_url(link):
                print(f" └───{GREEN} [+] Found contact page: {link} {RESET}")   
                if is_find_form(link):
                    contact_urls["urls"].append(link) 
                else:
                    contact_urls["no_form"].append(link) 
            
        
        for link in url_links["external_urls"]:
            if link in contact_urls["external_urls"]: continue
            if is_contactus_url(link):
                print(f" └───{GREEN} [+] Found external contact page: {link} {RESET}") 
                if is_find_form(link):
                    contact_urls["external_urls"].append(link) 
                else:
                    contact_urls["no_form"].append(link)  
                
        count_contact_forms_urls += len(contact_urls["external_urls"]) + len(contact_urls["urls"])
        count_contact_urls_without_form += len(contact_urls["no_form"])

        emails[url] = get_email(url)
        for email in emails[url]:
            print(f" └───{GREEN} [+] Found email: {email} {RESET}")  
            pass 
            
        final_emails = []
        domain_name = urlparse(url).netloc
        if not emails[url]:
            final_emails = ''
        else:
            emails[url] = remove_list_duplicates(emails[url])
            for email in emails[url]:
                count_emails += 1
                if domain_name.split(".")[1] in email:
                    final_emails.append(email)

        finalContactPages = []
        if not contact_urls["urls"]:
            finalContactPages = ''
        else:
            contact_urls["urls"] = remove_list_duplicates(contact_urls["urls"])
            finalContactPages = contact_urls["urls"][0]
            # for url in contact_urls["urls"]:
            #     finalContactPages.append(url)
        
        with open('contact_Urls.csv', 'a', newline='', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if csvfile.tell() == 0: # checks if the file already exists with headers then it skips writing headers again.
                writer.writeheader()
            writer.writerow({'url': url, 'contact_page': finalContactPages, 'email': ", ".join(final_emails)})

    ################################################################
    #   Output summary information
    ################################################################
    
    with open('output_summary.txt', 'w', encoding="utf-8") as file:
        file.write("Summary information: \n")
        print(f'Summary information:')
    
        file.write(f' [+] Searched {len(urls_list)} urls \n')
        print(f' [+] Searched {len(urls_list)} urls')

        file.write(f' [+] Found total of {count_contact_forms_urls} Contact urls \n')
        print(f' [+] Found total of {count_contact_forms_urls} Contact urls ')
    
        file.write(f'  └───[+] {count_contact_urls_without_form} of it dont have a form \n')
        print(f'  └───[+] {count_contact_urls_without_form} of it dont have a form ')
    
        file.write(f' [+] Found {count_unavailable_urls} unavaliable urls \n')
        print(f' [+] Found {count_unavailable_urls} unavaliable urls')
        
        file.write(f' [+] Found {count_emails} emails \n')
        print(f' [+] Found {count_emails} emails')

        file.write(f'-----------------------------------------------------------------------------------------\n')
        print(f'-----------------------------------------------------------------------------------------')
    
    return contact_urls

def Simple_Run(urls_list):
    result = []
    ################################################################
    #   Search for contacts pages 
    ################################################################
    for url in urls_list:
        result.append(handleUrl(url))
    
    return result


if __name__ == "__main__":
    urls_list = ["https://www.produktenews.ch/", "https://www.swissbanking.ch/", "https://www.pga.info/"]
    Simple_Run(urls_list)
   


    
        
