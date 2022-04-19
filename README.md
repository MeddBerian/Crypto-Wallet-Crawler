# Crypto-Wallet-Crawler

## Web Scraping
Web scraping, web harvesting, or web data extraction is data scraping used for extracting data from websites. 
The web scraping software may directly access the World Wide Web using the Hypertext Transfer Protocol or a web browser. 
While web scraping can be done manually by a software user, the term typically refers to automated processes implemented using a bot or web crawler. 
It is a form of copying in which specific data is gathered and copied from the web, typically into a central local database or spreadsheet, for later retrieval or analysis.
This project is completely written in python

## Required Python External Libraries

- Selenium
- Beautiful Soup
- Pandas
- Requests
- Numpy

## How it works
### Data Extraction
The Crypto Wallet Crawling Bot gather all transactions information related to the provided Crytpo Wallet Address. 
The transaction informations will be harvested from https://www.v2.tools.gemit.app  
The cryptocurrencies will be refered to as Assets.
All the data extraction and scraping process takes place in the '[program.py](https://github.com/MeddBerian/Crypto-Wallet-Crawler/blob/master/program.py)' python file. 
At the onset of the extraction process, the Crypto Wallet Bot prompts/requests for a valid 'WALLET ADDRESS', then extraction process begins.
The extracton process can be PAUSED and TERMINATED with the combination of CTRL + C Keys.

The targeted information includes:
- Number of Asset (Crypto) found
- Wallet Address
- Asset (Crypto) Name
- Asset (Crypto) Price
- Asset (Crypto) Quantity
- Asset (Crypto) Value
- Asset (Crypto) Logo Url
- Asset (Crypto) Price Change in 24 Hrs
- Amount Invested on Asset (Crypto) 
- Amount Paid Out or Withdrawn
- Assets Reflection Gain
- Total Transaction/Swap Cost
- Asset (Crypto) Contract Address
- Asset (Crypto) Gain Without Reflection

The collected information will then be tabulated and stored as 'Wallet Result.csv' in the 'Results' folder using Pandas dataframe.

### Data Visualization
Microsoft Power BI was used for the data visualization. 
The visualization contains important metrics such as:
- Number of Assets
- Wallet Worth (Sum of the value of each Asset (Crypto))
- Total Amount Invested (Sum of the Amount Invested on each Asset (Crypto))
- Total Amount Paid/Cashed Out (Sum of the value of each Asset (Crypto))
- Amount Invested
- Amount Cashed/Paid Out
- Quantity of each Assets
- Asset Worths (Monetary value of each assets in Dollar)
- Result (Differences between the Wallet Worth and Amount Invested). This indicates whether the wallet is on Profit/Gain or Loss.
- Tabular representation of all the assets found in the wallet

A link to an interactive preview of the visualization >>> [Click me](https://app.powerbi.com/view?r=eyJrIjoiYzRhYjEwN2EtMzFjNS00ZWVlLThkNjItYTI5ZWJjOGY2MDMzIiwidCI6ImY1NTAyNjhkLTcwMzYtNDVkYi04ZTgwLTI2MjMyZGY2MjMyMCIsImMiOjF9&pageName=ReportSectiona19f1c9c034971050322)

Below is a pictoral snapshot of the visualization.

![vis1](https://user-images.githubusercontent.com/99067011/163991792-3950fb8c-00de-4c99-87b6-5d3185581e3e.JPG)
![vis2](https://user-images.githubusercontent.com/99067011/163991798-e85502d2-84d4-4356-8465-bc327a088f15.JPG)
![vis3](https://user-images.githubusercontent.com/99067011/163991801-3c4c9994-bd74-4b03-b3ce-f052048447c4.JPG)
![vis4](https://user-images.githubusercontent.com/99067011/163991804-84a893b0-8e8d-4a4c-a37e-4acdc976f08e.JPG)

