# portfolio-manager
### OVERVIEW:
An interactive stock portfolio manager built with a custom Pandas-inherited architecture. Features real-time market data via yfinance, and interactive CRUD operations (Buy/Sell/View). Includes a specialized Pandas child class for portfolio object manipulation and display in the console.

The goal of this project was to create a program that runs entirely through user input, allows the user to create portfolios, buy and sell any assets they can find on Yahoo Finance, and then come back to view their portfolio to see how they're performing. The advantages of this structure are firstly and most importantly, that the user has access to unlitmited funds to buy assets with, and that the user can easily keep track of any and all portfolios they create and assests they purchase. A created 'Port' object (portfolio) is a pandas data frame with the ticker abbreviation of an asset set as the index. 

The metrics that are tracked and/or calculated for each asset in a portfolio the user creates are: shares owned, actual money invested, latest close price for the asset, current market value of the shares owned, average price the user paid for the shares they own, current unrealized profit/loss of the asset in dollars, current unrealized profit/loss of the asset expressed as a percentage increase or decrease, and finally the portfolio allocation percentage which represents how much of the portfolio that asset makes up. Furthermore, Port objects have a few attributes/metadata that is kept track of in order to identify and evaluate a portfolio: the portfolio's name, the date and time it was created, the date and time the portfolio was updated (assets bought, sold, or refreshed), the realized profit loss of the portfolio (P/L of any assets sold), and finally the current total profit/loss of the portfolio (realized P/L + sum(all assets unrealized P/L)). All of these will be visible in the images of an example portfolio that will be supplied in this repository.

---------------------------------------------------------------------------------------------------------------------------------------------------
### PROJECT ORDER:

Here's the order this project's folders should be viewed in:
- `Python Files` /
    -  `port.py`
    -  `interface.py`
    -  `main.py` (run this file)
    
-  `Example Portfolio`
    -  `portfolio_data.csv`
    -  `portfolio_image.png`

 - `Portfolio Operations` /
   -  `Create.png`
   -  `View.png`
   -  `Buy.png`
   -  `Sell.png`
 
 --------------------------------------------------------------------------------------------------------------------------------------------------
 ### IN DEPTH DESCRIPTION:

Below is a description of each file, and its purpose. For a more specific description of individual lines of code and/or functions, please view the Python files themselves. The files are **heavily commented** to help aid in the understanding of the code.

### 1. `port.py`:

This file is where the 'Port' Class resides, which means it's where the portfolio objects are defined, and the functions that act on them are located (mutators and disk methods). This file can be thought of as the engine behind this project, as it does all of the required calculations needed to compute a portfolio's metrics, and as it does all the data scraping from Yahoo Finance. Furthermore, this class subclasses Pandas to take advantage of Pandas' Data Frame functionality, which is perfect for creating, displaying, and altering a table of assets (i.e. a portfolio).  

### 2. `interface.py`:

This script handles all the user interaction: user input and error checking. 

### 3. `main.py`:


