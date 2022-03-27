## >>> Import required packages
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import requests
import sys
import re
import numpy as np
import os

from Packages.logger import Logger



## >>> Wallet crawler function declaration
def walletCrawler():

    ## >>> Logger configuration
    log = Logger("Wallet Crawler Logs")

    ## >>> Test for availability of internet connection
    try:
        request = requests.get("http://www.google.com", timeout=5)
        log.info("Connected to the Internet!")
    except (requests.ConnectionError, requests.Timeout) as exception:
        log.critical("No active internet connection!")
        sys.exit()


    ## >>> Collect and validate Crypto Wallet Address 
    while True:
        # Collect Wallet Address from user
        walletAddress = input("Please provide a valid Wallet Address: ").strip()  

        # Regular expression pattern to validate provided wallet address
        walletAddressPattern = re.compile("^([a-zA-Z0-9]){24,45}$")               


        # Check if the provided walllet address is valid
        if(bool(walletAddressPattern.match(walletAddress))):
            
            log.info(f"Checking for the existence of Wallet: {walletAddress}...")
            log.info(f"Please wait...")

            # Selenium webdriver configuration to test for the existence of the provided wallet address
            url = f"https://www.v2.tools.gemit.app/#/wallet/{walletAddress}"
            driverPath = "chromedriver.exe"
            chromeOptions = webdriver.ChromeOptions()
            chromeOptions.add_argument("--headless")
            chromeOptions.add_argument("--log-level=3")
            chromeOptions.add_argument('--ignore-certificate-errors')
            chromeOptions.add_argument('--ignore-ssl-errors')
            driver = webdriver.Chrome(executable_path = driverPath, options = chromeOptions)
            driver.get(url)

            # Check if the provided walllet address is exists
            try:
                WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.CLASS_NAME, "list-token")))
                log.info(f"Wallet address: {walletAddress} exist!")
                break

            except:
                log.error(f"This Wallet Address {walletAddress} does not exist!") 
                log.error(f"Also, check if your Internet connection is strong, then retry!") 

        else:
            log.error("Invalid wallet address!")


    ## >>> Wallet crawling start point 
    ## >>> Wallet crawling continues if the provided wallet address is valid and exist 
    try:

        # Extract general wallet details
        walletDetailsSource = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, "list-details"))) 
        
        # Initializing beautiful soup for extraction to extract total worth of the wallet
        walletDetalContent = BeautifulSoup(walletDetailsSource.get_attribute("innerHTML"), "html.parser") 
        walletWorth = walletDetalContent.find_all("li", {"class" : "list-details__item"})[5].find("app-result").find("div").find("span").string.replace(" $","")

        # Log wallet worth
        log.info(f"Wallet: {walletAddress} is worth around ${walletWorth}")



        ## >> Clicking the neccessary web element to extract details of all assets in wallets
        ## >> Wait for certain web elements to be completely loaded before extraction
        driver.execute_script("arguments[0].click();", WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.dropdown-button"))))
        driver.execute_script("arguments[0].click();", WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.LINK_TEXT, "all"))))
        log.info(f"Trying to extract details of all asset(s) in {walletAddress}...")

        # Waiting for details of assets to be completely loaded before extraction
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.open-details")))

        # Extracting complete source of loaded assets details to Beautiful soup
        assetsContentsSource = driver.page_source
        assetDetailSource = BeautifulSoup(assetsContentsSource, "html.parser")
        allAssetsProfile = []
        assetProfile = {}
        allAssetsContents = assetDetailSource.find('div', {'class':'list-token'}).find_all("app-token-list-item")
        allAssetsContentsIndices =  list(range(1,len(allAssetsContents)))  

        # Log the total number of asset(s) in the wallet
        # Executions might slow down if the number of asset(s) in the wallet is above 50
        log.info(f"There are a total of {len(allAssetsContentsIndices)} asset(s) in {walletAddress}{', this might take longer time to be completed...' if len(allAssetsContentsIndices) > 50 else '!'}\nYou can press 'CTRL C' to PAUSE the extraction process!")
        assetsCount = 1

        ## >> Iterate through and extracting all loaded assets details
        for contentIndex in allAssetsContentsIndices:

        ## >> Beginning of Try block enclosing the extraction process to enable Pause, Resume and Quit functionality 
            try:

                # Populating asset details into a dictionary 
                assetProfile["Name"] = allAssetsContents[contentIndex].find('div', {'class':'card-token'}).find('div', {'class':'informations--name'}).find('span', {'class':'value__name'}).string.replace(" ","")
                assetProfile["Price"] = allAssetsContents[contentIndex].find('div', {'class':'card-token'}).find('div', {'class':'informations--price'}).find('app-lp-price').find('div').find('div').find('span').string.split(" ")[0]
                assetProfile["Quantity"] = allAssetsContents[contentIndex].find('div', {'class':'card-token'}).find('div', {'class':'informations--quantity'}).find('span', {'class':'value'}).string.replace(" ","")
                assetProfile["Value"] = allAssetsContents[contentIndex].find('div', {'class':'card-token'}).find('div', {'class':'informations--value'}).find('app-lp-price').find('div').find('div').find('span').string.split(" ")[0]
                logoUrl = allAssetsContents[contentIndex].find('div', {'class':'card-token'}).find('div', {'class':'logo'}).find('img')["src"] 
                assetProfile["Logo Url"] = logoUrl if logoUrl != "assets/img/no-photo.svg" else "https://www.v2.tools.gemit.app/assets/img/no-photo.svg"
                

                # Click asset details button (WebElement) to expose asset details
                detailButton = driver.find_elements(By.CSS_SELECTOR, "button.open-details")[contentIndex]
                driver.execute_script("arguments[0].click();", detailButton)
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.content1 ul.table app-lp-price.row-value")))          
                assetProfile["Contract Address"] = driver.find_elements(By.CLASS_NAME, "links-outside__item--bsc")[1].get_attribute("href").split("/")[-1].split("#")[0]
                
                # Tries to gather more detail about the asset
                try:
                    assetProfile["Price Change In 24Hrs"] = allAssetsContents[contentIndex].find('div', {'class':'card-token'}).find('div', {'class':'informations--60'}).find('span', {'class':'value'}).find('span').find('b').string.replace("%","").strip()
                    targetElements = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.content1 ul.table")))
                    targetElementsSource = BeautifulSoup(targetElements.get_attribute("innerHTML"), "html.parser")
                    targetItems = targetElementsSource.find_all("li", {"class" : "table__item"})

                    for item in targetItems:
                        targetItemsTitle = item.find("p", {"class" : "row-desc"}).string.replace(":","").strip()
                        if(targetItemsTitle == "Result"):
                            continue
                        else:
                            try:
                                targetItemsValue = item.find("p", {"class" : "row-value"})

                                if not targetItemsValue:
                                    assetProfile[targetItemsTitle] = item.find("app-lp-price", {"class" : "row-value"}).find("span", {"class" : "value"}).string.replace("$","").strip()
                                else:
                                    assetProfile[targetItemsTitle] = targetItemsValue.string.replace("$","").strip()
                            except:
                                assetProfile[targetItemsTitle] = ""

                except:
                    assetProfile["Price Change In 24Hrs"] = ""



                # Click close details button (WebElement) to hide asset details
                closeDetailButton = driver.find_element(By.CSS_SELECTOR, "button.header__close")
                driver.execute_script("arguments[0].click();", closeDetailButton)

                # Log asset details to confirm its extraction
                log.info(f"Wallet: {walletAddress} - {assetProfile['Name']} extracted - [{assetsCount} of {len(allAssetsContents)-1} asset(s)]")
                assetsCount += 1
                # Append each asset details into a list
                allAssetsProfile.append(assetProfile)
                assetProfile = {}

                # Check if the last element have been identified
                if contentIndex == allAssetsContentsIndices[-1]:
                    log.info(f"Extraction from Wallet: {walletAddress} completed. Extracted [{len(allAssetsContents)-1} of {len(allAssetsContents)-1} asset(s)]")
                    break


        ## >> Catched exception of Try block enclosing the extraction process to enable Pause, Resume and Quit functionality 
            except KeyboardInterrupt:
                print("\nPAUSED!  ~ Type 'QUIT' to quit or 'RESUME' to resume\n")
                endExtraction = False
                while True:
                    response = input("Do you want to 'QUIT' or 'RESUME'?: ").strip().lower()
                    if(response not in ['quit', 'resume']):
                        print("You can only 'QUIT' or 'RESUME'")

                    if response == 'quit':
                        endExtraction = True
                        break

                    if response == 'resume':
                        endExtraction = False
                        break
                    
                if endExtraction == True:
                    break
                else:
                    print('RESUMING...\nPlease wait while we get back on track...')
                    allAssetsContentsIndices.append(contentIndex)
                    driver = webdriver.Chrome(executable_path = driverPath, options = chromeOptions)
                    driver.get(url)
                    driver.execute_script("arguments[0].click();", WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.dropdown-button"))))
                    driver.execute_script("arguments[0].click();", WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.LINK_TEXT, "all"))))
                    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.open-details")))
                   



        # Convert and save the extracted details into a Pandas dataframe
        allAssetsProfileDf = pd.DataFrame([eachAssetProfile for eachAssetProfile in allAssetsProfile])
        allAssetsProfileDf.index = np.arange(1, len(allAssetsProfile) + 1)



        # Check if the folder and file already exist; creates one if it doesn't exist
        if not os.path.isdir('Results'):
            os.mkdir("Results")

        if not os.path.isfile(f"Results/{walletAddress}.csv"):
            allAssetsProfileDf.to_csv(f"Results/{walletAddress}.csv")
        else:
            while True:
                print(f"File: {walletAddress}.csv already exists")
                replaceFileOrNot = input("Do you want to replace it [Y/N]: ").strip().lower()  # Collect Wallet Address from user
                
                if(replaceFileOrNot not in ['y', 'n']):
                    print("You can only input Y or y for Yes! and N or n for No!")
                
                if(replaceFileOrNot == 'y'):
                    os.remove(f"Results/{walletAddress}.csv")
                    allAssetsProfileDf.to_csv(f"Results/{walletAddress}.csv")
                    break
                
                if(replaceFileOrNot == 'n'):
                    break
                
        log.info(f"Data saved as: '{walletAddress}.csv' in 'Results' directory!")

        # Close selenium instance
        driver.quit()




    # Handle exception incase something went wrong
    except Exception as e:
        driver.quit()
        print("Something went wrong!")
        print(f"{e} in Line {sys.exc_info()[-1].tb_lineno}")

if __name__ == "__main__":
    walletCrawler()
