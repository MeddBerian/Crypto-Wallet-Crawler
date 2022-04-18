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

## >>> Import custom package
from Packages.logger import Logger


## >>> Wallet crawler function declaration
def wallet_crawler() -> None:

    ## >> Logger configuration
    log = Logger("Wallet Crawler Logs")

    ## >> Test for availability of internet connection
    try:
        request = requests.get("http://www.google.com", timeout=5)
        log.info("Connected to the Internet!")
    except (requests.ConnectionError, requests.Timeout) as exception:
        log.critical("No active internet connection!")
        sys.exit()


    ## >> Collect and validate Crypto Wallet Address 
    while True:
        # Collect Wallet Address from user
        wallet_address = input("Please provide a valid Wallet Address: ").strip()  

        # Regular expression pattern to validate provided wallet address
        wallet_address_pattern = re.compile("^([a-zA-Z0-9]){24,45}$")               

        # Check if the provided walllet address is valid
        if(bool(wallet_address_pattern.match(wallet_address))):
            
            log.info(f"Checking for the existence of Wallet: {wallet_address}...")
            log.info(f"Please wait...")

            # Selenium webdriver configuration to test for the existence of the provided wallet address
            url = f"https://www.v2.tools.gemit.app/#/wallet/{wallet_address}"
            driver_path = "chromedriver.exe"
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--ignore-ssl-errors')
            driver = webdriver.Chrome(executable_path = driver_path, options = chrome_options)
            driver.get(url)

            # Check if the provided walllet address is exists
            try:
                WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.CLASS_NAME, "list-token")))
                log.info(f"Wallet address: {wallet_address} exist!")
                break

            except:
                log.error(f"This Wallet Address {wallet_address} does not exist!") 
                log.error(f"Also, check if your Internet connection is strong, then retry!") 

        else:
            log.error("Invalid wallet address!")


    ## >> Wallet crawling start point 
    ## >> Wallet crawling continues if the provided wallet address is valid and exist 
    try:

        ## >> Clicking the neccessary web element to extract details of all assets in wallets
        ## >> Wait for certain web elements to be completely loaded before extraction
        driver.execute_script("arguments[0].click();", WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.dropdown-button"))))
        driver.execute_script("arguments[0].click();", WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.LINK_TEXT, "all"))))
        log.info(f"Trying to extract details of all asset(s) in {wallet_address}...")

        # Wait for details of assets to be completely loaded before extraction
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.open-details")))

        # Extract complete source of loaded assets details to Beautiful soup
        assets_details_raw_source = BeautifulSoup(driver.page_source, "html.parser")
        consolidated_assets_details = []
        each_asset_detail = {}
        assets_details_source = assets_details_raw_source.find('div', {'class':'list-token'}).find_all("app-token-list-item")
        assets_details_source_indices =  list(range(1,len(assets_details_source))) 

        # Log the total number of asset(s) in the wallet
        # Executions might slow down if the number of asset(s) in the wallet is above 50
        log.info(f"There are a total of {len(assets_details_source_indices)} asset(s) in {wallet_address}{', this might take longer time to be completed...' if len(assets_details_source_indices) > 50 else '!'}\nYou can press 'CTRL C' to PAUSE the extraction process!")
        assets_count = 1

        ## >> Iterate through and extracting all loaded assets details
        for asset_index in assets_details_source_indices:

        ## >> Beginning of Try block enclosing the extraction process to enable Pause, Resume and Quit functionality 
            try:

                # Populating asset details into a dictionary 
                each_asset_detail["Wallet Address"] = wallet_address
                each_asset_detail["Name"] = assets_details_source[asset_index].find('div', {'class':'card-token'}).find('div', {'class':'informations--name'}).find('span', {'class':'value__name'}).string.replace(" ","")
                each_asset_detail["Price"] = assets_details_source[asset_index].find('div', {'class':'card-token'}).find('div', {'class':'informations--price'}).find('app-lp-price').find('div').find('div').find('span').string.split(" ")[0]
                each_asset_detail["Quantity"] = assets_details_source[asset_index].find('div', {'class':'card-token'}).find('div', {'class':'informations--quantity'}).find('span', {'class':'value'}).string.replace(" ","")
                each_asset_detail["Value"] = assets_details_source[asset_index].find('div', {'class':'card-token'}).find('div', {'class':'informations--value'}).find('app-lp-price').find('div').find('div').find('span').string.split(" ")[0]
                asset_logo_url = assets_details_source[asset_index].find('div', {'class':'card-token'}).find('div', {'class':'logo'}).find('img')["src"] 
                each_asset_detail["Logo Url"] = asset_logo_url if asset_logo_url != "assets/img/no-photo.svg" else "https://www.v2.tools.gemit.app/assets/img/no-photo.svg"
                
                # Click asset details button (WebElement) to expose asset details
                asset_detail_button = driver.find_elements(By.CSS_SELECTOR, "button.open-details")[asset_index]
                driver.execute_script("arguments[0].click();", asset_detail_button)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.content1 ul.table app-lp-price.row-value")))          
                each_asset_detail["Contract Address"] = driver.find_elements(By.CLASS_NAME, "links-outside__item--bsc")[1].get_attribute("href").split("/")[-1].split("#")[0]
                
                # Tries to gather indepth detail about the asset
                try:
                    each_asset_detail["Price Change In 24Hrs"] = assets_details_source[asset_index].find('div', {'class':'card-token'}).find('div', {'class':'informations--60'}).find('span', {'class':'value'}).find('span').find('b').string.replace("%","").strip()
                    each_asset_indepth_detail = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.content1 ul.table")))
                    each_asset_indepth_detail_source = BeautifulSoup(each_asset_indepth_detail.get_attribute("innerHTML"), "html.parser")
                    asset_indepth_detail = each_asset_indepth_detail_source.find_all("li", {"class" : "table__item"})

                    for detail in asset_indepth_detail:
                        asset_indepth_detail_title = detail.find("p", {"class" : "row-desc"}).string.replace(":","").strip()
                        if(asset_indepth_detail_title == "Result"):
                            continue
                        else:
                            try:
                                asset_indepth_detail_value = detail.find("p", {"class" : "row-value"})

                                if not asset_indepth_detail_value:
                                    each_asset_detail[asset_indepth_detail_title] = detail.find("app-lp-price", {"class" : "row-value"}).find("span", {"class" : "value"}).string.replace("$","").strip()
                                else:
                                    each_asset_detail[asset_indepth_detail_title] = asset_indepth_detail_value.string.replace("$","").strip()
                            except:
                                each_asset_detail[asset_indepth_detail_title] = "0"

                except:
                    each_asset_detail["Price Change In 24Hrs"] = "0"


                # Click close details button (WebElement) to hide asset details
                close_asset_detail_button = driver.find_element(By.CSS_SELECTOR, "button.header__close")
                driver.execute_script("arguments[0].click();", close_asset_detail_button)

                # Log asset details to confirm its extraction
                log.info(f"Wallet: {wallet_address} - {each_asset_detail['Name']} extracted - [{assets_count} of {len(assets_details_source)-1} asset(s)]")
                assets_count += 1
                # Append each asset details into a list
                consolidated_assets_details.append(each_asset_detail)
                each_asset_detail = {}

                # Check if the last element have been identified
                if asset_index == assets_details_source_indices[-1]:
                    log.info(f"Extraction from Wallet: {wallet_address} completed. Extracted [{len(assets_details_source)-1} of {len(assets_details_source)-1} asset(s)]")
                    break

        ## >> Catched exception of Try block enclosing the extraction process to enable Pause, Resume and Quit functionality 
            except KeyboardInterrupt:
                print("\nPAUSED!  ~ Type 'QUIT' to quit or 'RESUME' to resume\n")
                log.info(f"Extraction PAUSED!")

                end_extraction = False
                while True:
                    response = input("Do you want to 'QUIT' or 'RESUME'?: ").strip().lower()
                    if(response not in ['quit', 'resume']):
                        print("You can only 'QUIT' or 'RESUME'")

                    if response == 'quit':
                        end_extraction = True
                        break

                    if response == 'resume':
                        end_extraction = False
                        break
                    
                if end_extraction == True:
                    log.info(f"Extraction TERMINATED!")
                    break

                else:
                    print('RESUMING...\nPlease wait while we get back on track...')
                    assets_details_source_indices.append(asset_index)
                    driver = webdriver.Chrome(executable_path = driver_path, options = chrome_options)
                    driver.get(url)
                    driver.execute_script("arguments[0].click();", WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.dropdown-button"))))
                    driver.execute_script("arguments[0].click();", WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.LINK_TEXT, "all"))))
                    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.open-details")))
                    log.info(f"Extraction RESUMED!")

        # Convert and save the extracted details into a Pandas dataframe
        consolidated_assets_details_DF = pd.DataFrame([individual_asset_detail for individual_asset_detail in consolidated_assets_details])
        consolidated_assets_details_DF = consolidated_assets_details_DF.fillna(0)
        consolidated_assets_details_DF.index = np.arange(1, len(consolidated_assets_details) + 1)


        # Check if the folder and file already exist; creates one if it doesn't exist
        if not os.path.isdir('Results'):
            os.mkdir("Results")

        if not os.path.isfile(f"Results/Wallet Result.csv"):
            consolidated_assets_details_DF.to_csv(f"Results/Wallet Result.csv")
        else:
            while True:
                print(f"File: Wallet Result.csv already exists")
                replace_file_OR_not = input("Do you want to replace it [Y/N]: ").strip().lower() 
                
                if(replace_file_OR_not not in ['y', 'n']):
                    print("You can only input Y or y for Yes! and N or n for No!")
                
                if(replace_file_OR_not == 'y'):
                    os.remove(f"Results/Wallet Result.csv")
                    consolidated_assets_details_DF.to_csv(f"Results/Wallet Result.csv")
                    break
                
                if(replace_file_OR_not == 'n'):
                    break
                
        log.info(f"Data saved as: 'Wallet Result.csv' in 'Results' directory!")

        # Close selenium instance
        driver.quit()


    # Handle exception incase something went wrong
    except Exception as e:
        driver.quit()
        print("Something went wrong!")
        # print(f"{e} in Line {sys.exc_info()[-1].tb_lineno}") 

if __name__ == "__main__":
    wallet_crawler()