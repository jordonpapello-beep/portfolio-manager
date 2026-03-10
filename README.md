# portfolio-manager
### OVERVIEW:
- An interactive stock portfolio manager built with a custom Pandas-inherited architecture. Features real-time market data via yfinance, and interactive CRUD operations (Buy/Sell/View). Includes a specialized Pandas child class for portfolio object manipulation and display in the console.

- The goal of this project was to create a program that runs entirely through user input, allows the user to create portfolios, buy and sell any assets they can find on Yahoo Finance, and then come back to view their portfolio to see how they're performing. The advantages of this structure are firstly and most importantly, that the user has access to unlitmited funds to buy assets with, and that the user can easily keep track of any and all portfolios they create and assests they purchase. A created 'Port' object (portfolio) is a pandas data frame with the ticker abbreviation of an asset set as the index. 

- The metrics that are tracked and/or calculated for each asset in a portfolio the user creates are: shares owned, actual money invested, latest close price for the asset, current market value of the shares owned, average price the user paid for the shares they own, current unrealized profit/loss of the asset in dollars, current unrealized profit/loss of the asset expressed as a percentage increase or decrease, and finally the portfolio allocation percentage which represents how much of the portfolio that asset makes up. Furthermore, Port objects have a few attributes/metadata that is kept track of in order to identify and evaluate a portfolio, which are: the portfolio's name, the date and time it was created, the date and time the portfolio was updated (assets bought, sold, or refreshed), the realized profit loss of the portfolio (P/L of any assets sold), and finally the current total profit/loss of the portfolio (realized P/L + sum(all assets' unrealized P/L)). All of these will be visible in the images of an example portfolio that will be supplied in this repository.

- For the best understanding of the program and it's functionality, and to see all of the options available when buying and selling assets, feel free to run the code on your own and test out making your own portfolios!
---------------------------------------------------------------------------------------------------------------------------------------------------
### PROJECT ORDER:

Here's the order this project's folders should be viewed in:
- `Python Files` /
    -  `port.py`
    -  `interface.py`
    -  `main.py` (run this file)
    
-  `Example Portfolio`
    -  `Test.csv`
    -  `Test_Portfolio.png`

 - `Portfolio Operations` /
   -  `Create.png`
   -  `Buy.png`
   -  `Sell.png`
   -  `View.png`
   -  `Refresh.png`
 
 --------------------------------------------------------------------------------------------------------------------------------------------------
 ### FILE DESCRIPTIONS:

Below is a description of each file, and its purpose. For a more specific description of individual lines of code and/or functions, please view the Python files themselves. The files are **heavily commented** to help aid in the understanding of the code.

### 1.) `port.py`:

 - This file is where the **'Port' Class resides**, which means it's **where the portfolio objects are defined, and the functions that act on them are located (mutators and disk methods).** This file can be thought of as the **engine behind this project**, as it does all of the required calculations needed to **compute a portfolio's metrics**, and as it does all the **data scraping** from Yahoo Finance. Furthermore, this class **subclasses Pandas to take advantage of Pandas' Data Frame functionality**, which is perfect for creating, displaying, and altering a table of assets (i.e. a portfolio).
 - One main **problem arose when trying to subclass Pandas** and implement the Port Class. When you perform any Pandas operation (iloc[], .copy(), concat) on a Port object, **Pandas would automatically return a Pandas Data Frame instead of the desired Port object** after the function was completed. In order to successfully subclass Pandas in a way that allowed the custom Port object functionality, **a few specific function overrides had to be added:** `_constructor`, and `_constructor_sliced`.
     -  **`_constructor`**: This tells Pandas, "When you perform an operation that returns a whole DataFrame (like df.drop(), etc...), use the Port class to build the new one, not the standard pd.DataFrame." Without this, the custom methods like `.buy()` or `.sell()` would vanish as soon as you manipulated the data.
     -  **`_constructor_sliced`**: This is for when a pandas operation returns a single column or row (a Series). Usually, we point this back to pd.Series because a single column of stock prices doesn't need to be a full Port object.
     
    Now that we have access to Pandas functionality, we can create the rest of the Port Class like we would any other. The main constructor,           a custom `__str__` method, mutators for altering both portfolio header data and the asstes' data, and disk operations like `load`, `save`, and     `delete`. 

### 2.) `interface.py`:

- **This script handles all the user interaction**: user input collection and error checking. It is the 'frontend' of this project, the 'Command Line Interface (CLI)': **a text-based user interface used to interact with software.** All of the functions defined in this script are designed to collect user input, handle any errors in that input, and to guide the user to make a choice to perform an action on a portfolio or exit the program. The only function that does not fall into this category is `ticker_exists`, which is a simple helper function designed to validate that an assets ticker abbreviation exists on Yahoo Finance.
    - **`view_input`:** can be thought of as the **main menu** where all portfolios can be accessed and selected for display in the console.
    - **`create_input`:** for when the user wants to create a new portfolio. User can name their portfolio whatever they want.
    - **`buy_input`:** for when the user wants to buy a new asset or more of the same asset for a specific portfolio. The user can choose to buy an asset by shares or by dollar amount.
    - **`sell_input`:** for when the user wants to sell all or some of an asset from a specific portfolio. The user can choose to buy an asset by shares or by dollar amount, or choose to sell all of the asset.

### 3.) `main.py`:

- This script acts as the **start button for the porgram**. It serves as the program's entry point and control framework. It implements a **persistent event loop** that manages user interaction through a command-driven menu. By utilizing a match-case routing structure, it validates user input and delegating tasks to the appropriate user input functions while maintaining the program's state until the user chooses to exit the program.
