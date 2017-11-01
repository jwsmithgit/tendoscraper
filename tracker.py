'''
TODO
try to find a document ready script
check preorder for buttons
'''

import sys

import smtplib

import time
import datetime

from selenium import webdriver

def _site_defs():
    return {
        'bestbuy' : {
            'xpath' : '//*[@id="btn-cart"]',
            'attribute' : 'class',
            'value' : 'btn btn-primary disabled',
            'price_xpath' : '//*[@id="schemaorg-offer"]/div[1]/div[3]/div[1]'
        },

        'ebgames' : {
            'xpath' : '//*[@id="btnAddToCart"]',
            'attribute' : 'style',
            'value' : 'display: none;',
            'price_xpath' : '//*[@id="prodMain"]/div[1]/div[2]/div[2]/div[2]/div[1]/div[2]/div/p/span/span'
        },

        'walmart' : {
            'xpath' : '//*[@id="favourite-a2c-container"]/button',
            'attribute' : 'disabled',
            'value' : 'true',
            'price_xpath' : '//*[@id="product-purchase-cartridge"]/div[3]/div[1]/div[1]/div[1]'
        },

        'amazon' : {
            'xpath' : '//*[@id="outOfStock"]',
            'attribute' : 'id',
            'value' : 'outOfstock',
            'price_xpath' : '//*[@id="priceblock_ourprice"]'
        },

        'source' : {
            'xpath' : '//*[@id="addToCartForm"]/button',
            'attribute' : 'disabled',
            'value' : 'true',
            'price_xpath' : '//*[@id="content"]/section/section/div[1]/div[3]/div[1]/div[1]/span'
        },

        'toysrus' : {
            'xpath' : '//*[@id="buy-interior"]/dl/dt[1]',
            'attribute' : 'class',
            'value' : 'unavail',
            'price_xpath' : '//*[@id="price"]/dl/dd[2]'
        }
    }

def setup():
    options = {}
    sites = []
    emails = []

    file = open('tracker_setup.txt', 'r')
    for line in file:
        line = line.strip()

        if line == '' or line[0] == '#':
            continue

        space = line.find(' ')
        option = line[0:space]
        value = line[space+1:]

        if option == 'browser':
            options[option] = value
        elif option == 'sleep':
            emails.append(int(value))
        elif option == 'login':
            #emails.append(value)
            options[option] = value
        elif option == 'password':
            options[option] = value
        elif option == 'email':
            emails.append(value)
        elif option == 'url':
            sites.append({'url' : value})
        else :
            sites[-1][option] = value

    options['sites'] = sites
    options['emails'] = emails

    return options

def detect_site(url):
    site_defs = _site_defs()
    for key in site_defs:
        if url.find(key) != -1:
            return key
    return None

def get_price(price_string):
    price_string = "".join(_ for _ in price_string if _ in ".1234567890")
    price = float(price_string)
    return price

def check_site(driver, site):

    if 'Not Found' in driver.title:
        return False

    if 'price' in site:
        try:
            element = driver.find_element_by_xpath(site['price_xpath'])
        except:
            print('price_xpath not found:')
            print('  ' + site['price_xpath'])
            return False

        text_price = element.text
        price = get_price(text_price)

        if float(site['price']) > price:
            return False

    try:
        element = driver.find_element_by_xpath(site['xpath'])
    except:
        print('xpath not found:')
        print('  ' + site['xpath'])
        return False

    try:
        if element.get_attribute(site['attribute']) != site['value']:
            return True
    except:
        print('attribute not found:')
        print('  ' + site['attribute'])
        return False

    return False

def automate(driver, sites, sleep):
    site_defs = _site_defs()

    while 1:
        for site in sites:

            print(str(datetime.datetime.now()) + ' : ' + site['url'])
            try:
                driver.get(site['url'])
            except:
                print("error: site not available, check url")

            site_name = site_name = detect_site(site['url'])
            if site_name != None:
                site['xpath'] = site_defs[site_name]['xpath']
                site['attribute'] = site_defs[site_name]['attribute']
                site['value'] = site_defs[site_name]['value']
                site['price_xpath'] = site_defs[site_name]['price_xpath']
            else:
                if 'xpath' not in site:
                    print('error: need xpath in setup for url:')
                    print('  ' + site['url'])
                    sys.exit()
                if 'attribute' not in site:
                    print('error: need attribute in setup for url:')
                    print('  ' + site['url'])
                    sys.exit()
                if 'value' not in site:
                    print('error: need value in setup for url:')
                    print('  ' + site['url'])
                    sys.exit()
                if 'price' in site and 'price_xpath' not in site:
                    print('error: need price_xpath in setup for url:')
                    print('  ' + site['url'])
                    sys.exit()

            time.sleep(sleep)

            if check_site(driver, site):
                return site

def sendemail(from_addr, to_addr_list,
              subject, message,
              login, password,
              smtpserver='smtp.gmail.com:587'):

    print(type(to_addr_list))

    header = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Subject: %s\n' % subject
    header += '\n'
    message = header + message

    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login, password)
    server.sendmail(from_addr, to_addr_list, message)
    server.quit()

def main():

    options = setup()

    if 'browser' not in  options:
        try: 
            driver = webdriver.Chrome("bin\chromedriver.exe")
        except:
            print("error: please install chrome")
            print("       if you have firefox, place")
            print("         browser firefox")
            print("       in setup.txt")
            sys.exit()
    else :
        if options['browser'] == 'chrome':
            driver = webdriver.Chrome("bin\chromedriver.exe")
        elif options['browser'] == 'firefox':
            driver = webdriver.Firefox(executable_path="bin\geckodriver.exe")

    if 'sleep' not in options:
        options['sleep'] = 10

    sites = options['sites']
    site = automate(driver, sites, options['sleep'])

    driver.close()

    from_addr = options['login']
    to_addr_list = options['emails']
    subject = 'tracker: item in stock'
    message = site['url']
    login = options['login']
    password = options['password']

    #sendemail(from_addr, to_addr_list, subject, message, login, password)

main()