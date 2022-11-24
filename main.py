import os
import time
import sys
from dotenv import load_dotenv
from exceptiongroup import catch
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from helper.colors import colors
from collections import defaultdict
load_dotenv()

# Get the cur directory 
directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(directory)

dictionaryCheck = defaultdict()

# make timeout 20 sec for command find element
def find_element(driver, by, value, timeout = 20):
    return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, value)), f'{colors.red}Timeout while trying to reach an element ❌{colors.reset}')
# make timeout 2 sec for command find element
def find_element_short(driver, by, value, timeout = 0):
    return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, value)), f'{colors.red}Timeout while trying to reach an element ❌{colors.reset}')

# Get Handles from file
def getHandles(file):
    f = open(file, "r")
    handles = f.read().strip().split('\n')
    f.close()
    return handles


# create chrome driver
def initalizeDriver():    
    print(f'{colors.blue}Creating Driver{colors.reset}')
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-deb-shm-usage')
    chrome_options.add_argument('--no--sandbox')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--disable-popup-blocking')
    driver = webdriver.Chrome(options = chrome_options)
    return driver

# Go to main page
def openCodeforces(link, driver):
    print(f'{colors.blue}Openning Codeforces Standing{colors.reset}')
    handle = os.getenv('Handle')
    password = os.getenv('Password')
    envTest = os.path.exists('.env')
    
    if not envTest:
        print(f'{colors.red}Please create env file{colors.reset}')
    if not handle or not password:
        print(f'{colors.red}Please set the env variables (handle or password){colors.reset}')
        return
    driver.get(link)
    time.sleep(1)
    find_element(driver, By.XPATH, '//*[@id="header"]/div[2]/div[2]/a[1]').click();
    time.sleep(1)
    find_element(driver, By.XPATH, '//*[@id="handleOrEmail"]').send_keys(handle);
    find_element(driver, By.XPATH, '//*[@id="password"]').send_keys(password);
    find_element(driver, By.XPATH, '//*[@id="enterForm"]/table/tbody/tr[4]/td/div[1]/input').click();
    time.sleep(2)

# main process Getting Data from standings

def getData(driver):
    print(f'{colors.blue}Getting Data ... {colors.reset}')
    dict = defaultdict(set)
    dictAccepted = defaultdict(set)
    try:
        for pages in range(1, 500):
            print(f'{colors.blue}Page #{pages}{colors.reset}')
            x = 0
            try:
                find_element_short(driver, By.XPATH, f'//*[@id="pageContent"]/div[10]/nobr[{pages}]').click()
            except:
                x = 1
            try:
                for i in range(2, 5000):
                    y = 0
                    try:
                        handle = find_element_short(driver, By.XPATH, f'//*[@id="pageContent"]/div[5]/div[6]/table/tbody/tr[{i}]/td[2]/a').text
                    except:
                        try:
                            handle = find_element_short(driver, By.XPATH, f'//*[@id="pageContent"]/div[5]/div[6]/table/tbody/tr[{i}]/td[2]/span').text
                        except:
                            try:
                                handle = find_element_short(driver, By.XPATH, f'//*[@id="pageContent"]/div[5]/div[6]/table/tbody/tr[{i}]/td[2]').text
                            except:
                                y = 1
                    if y == 1:
                        print(f'{colors.red}No more Handles in this page{colors.reset}')
                        break

                    if not handle in dictionaryCheck:
                        continue
                    cnt = 0
                    print(handle + ' : ', end = ' ')
                    try:
                        for j in range(5, 40):
                            try:
                                problems = find_element_short(driver, By.XPATH, f'//*[@id="pageContent"]/div[5]/div[6]/table/tbody/tr[{i}]/td[{j}]').text
                                try:
                                    problemID = find_element_short(driver, By.XPATH, f'//*[@id="pageContent"]/div[5]/div[6]/table/tbody/tr[1]/th[{j}]/a').text
                                except:
                                    try:
                                        problemID = find_element_short(driver, By.XPATH, f'//*[@id="pageContent"]/div[5]/div[6]/table/tbody/tr[1]/th[{j}]/span').text
                                    except:  
                                        try:
                                            problemID = find_element_short(driver, By.XPATH, f'//*[@id="pageContent"]/div[5]/div[6]/table/tbody/tr[1]/th[{j}]').text
                                        except:                                        
                                            print(f'{colors.red}Error getting problem Id with j = {j} {colors.reset}', end = ' ')
                                            break
                                try:
                                    test = str(problems)
                                    if test.find('+') != -1:
                                        cnt += 1
                                        dictAccepted[handle].add(problemID)
                                except:
                                    print(f'{colors.red}Error in checking + {colors.reset}', end = ' ')
                            except:
                                print(f'{colors.green}{cnt} Accepted{colors.reset}')
                                break
                            dict[handle].add(problemID)
                    except:
                        print(f'{colors.red}Error getting problems{colors.reset}')
            except:
                print(f'{colors.red}No more Handles in this page{colors.reset}')
            if x == 1:
                print(f'{colors.red}No more pages in the standings{colors.reset}')
                break
    except:
        print(f'{colors.red}No more pages in the standings{colors.reset}')
    return dictAccepted
# main function
def main():
    print(f'{colors.green}Starting the program ... {colors.reset}')
    handles = getHandles('handles.txt')
    for handle in handles:
        dictionaryCheck[handle] = 1
    driver = initalizeDriver()
    link = os.getenv('standings')
    openCodeforces(link, driver)
    dict = getData(driver)
    print(f'{colors.blue}Printing Data ... {colors.reset}')

    f = open('Output.txt', "w")
    for hand in handles:
        numberOfProblemsAccepted = len(dict[hand])
        f.write(f'{hand} : {numberOfProblemsAccepted} Problems Accepted\n')
    f.close()
    driver.close()
    print(f'{colors.green}Program Finished{colors.reset}')
# Run the main function
if __name__ == "__main__":
    main()
