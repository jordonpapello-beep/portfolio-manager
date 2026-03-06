"""
INTERFACE MODULE:
• This module handles all user interaction, input collection, and input validation.
• Main.py acts as the controller, while this module acts as the interface.

The 'Frontend' of the CLI (Command Line Interface): a text-based user interface used to interact with software.
- Port() class = The Engine (Data/Math)
- Interface.py = The Dashboard (User Input Functions)
- Main.py = The Ignition (Start Button/Running the loop)

Keeping these separate prevents main.py from becoming a file that does too many things at once!

RATIONALE:
By separating the CLI logic from main.py, we achieve separation of concerns.
This keeps the main execution loop clean and ensures that the user interface
logic is separated from the core Portfolio data structures. This makes the
code easier to test and allows for future UI changes (like adding a GUI)
without rewriting the entire program.
"""
import yfinance as yf
from pathlib import Path
from port import Port
import sys # for sys.exit()


def ticker_exists(ticker):
    """
    Simple boolean function used to see check if an inputted Ticker abbreviation is authentic or not (can be found
    on and has data from Yahoo Finance).

    :param ticker: (str) the abbreviation of the stock / ETF.
    :return: returns boolean. True if the ticker returns at least 1 row of data, meaning it exists.
    """
    data = yf.download(ticker, period="1d", progress=False) # try to download the asset data
    return not data.empty # if no rows of data could be found and downloaded then return False


def view_input():
    """
    The purpose of this function is to display all the portfolios in the 'Portfolios' folder, and present the user
    with options on what to do: 'Buy', 'Sell', 'Refresh', 'View', 'Create', 'Delete', or 'Exit'. Running this
    function acts as a sort of main menu selection screen where all portfolios can be accessed and be acted on.
    """

    # Get the set of all portfolios in 'Portfolios' folder, and a lowercase version for error forgiveness:
    # using sets here instead of lists because sets are faster for lookups than lists:
    folder_names = {f.name for f in Path("Portfolios").iterdir() if f.is_dir()}
    folder_names_lower = {f.name.lower() for f in Path("Portfolios").iterdir() if f.is_dir()}

    # While loop that only allows the user to continue when a valid input is entered:
    while True:
        # Print out the list of all portfolios so the user can choose one:
        print("\n*** LIST OF PORTFOLIOS ***")
        i = 1
        for f in folder_names:  # Loop that numbers the folders names as they print in console:
            print(f"{i}.) {f}")  # Format: "1.) Folder Name"
            i += 1
        # Ask the user which folder/portfolio they want to view:
        chosen_portfolio_name = input("\nType the name of a Portfolio from the list above: ")

        # Spelling error checking/folder exists checking:
        if chosen_portfolio_name.lower() in folder_names_lower:
            # If valid, exit the loop and proceed with the program:
            break

        # If the logic reaches this point, the name was invalid:
        print(f"\n{'*' * 14} ERROR! YOU DIDN'T ENTER A VALID PORTFOLIO NAME {'*' * 14}")
        # The loop will now restart, re-printing the list and re-prompting the user automatically

    # If correct spelling, then load the CSV, save as a 'Port()' object, and display:
    chosen_portfolio_object = Port.load_from_csv(f"Portfolios/{chosen_portfolio_name}/" 
                                                 f"{chosen_portfolio_name}.csv",
                                                 name={chosen_portfolio_name.lower().capitalize()}) # Aesthetic choice
    chosen_portfolio_object.refresh_prices() # refresh the CSV before displaying it
    print(chosen_portfolio_object) # display the portfolio in the console

    # User Decision, what do they want to do now that they have selected this portfolio:
    # Do you want to 'Buy', 'Sell', 'Refresh', 'View', 'Create', 'Delete', or 'Exit':
    user_decision = input("\nDo you want to 'buy' or 'sell' assets with this portfolio, 'refresh' the prices for this "
                          "portfolio, 'view' another portfolio, \n'create' a new portfolio, 'delete' this portfolio, "
                          "or 'exit' the program?\nPlease enter 'Buy', 'Sell', 'Refresh', 'View', 'Create', "
                          "'Delete', or 'Exit': ").lower()
    # Input Error Handling:
    while user_decision not in ['buy', 'sell', 'refresh', 'view', 'create', 'delete', 'exit']:
        user_decision = input("\nINVALID INPUT! INPUT OPTIONS ARE 'Buy', 'Sell', 'Refresh', 'View', 'Create', "
                              "'Delete', or 'Exit': ").lower()

    # Match - Case ladder to handle the user's input:
    match user_decision:
        case 'exit':
            print("Exiting the Program")
            sys.exit() # Stops the program immediately
        case 'refresh':
            chosen_portfolio_object.refresh_prices() # refresh the data
            print(chosen_portfolio_object) # re-print the data
        case 'view':
            view_input()
        case 'create':
            create_input()
        case 'delete':
            double_check = input("Are you sure you want to delete this portfolio? 'Yes' or 'No': ").lower()
            while double_check not in ['yes', 'no']: # user input error handling:
                print(f"\n{'*' * 14} ERROR! YOU DIDN'T ENTER EITHER 'YES' OR 'NO'. {'*' * 14}")
                double_check = input("\nAre you sure you want to delete this portfolio? 'Yes' or 'No': ").lower()
            if double_check == 'yes':
                chosen_portfolio_object.delete_portfolio_folder(chosen_portfolio_name) # delete the portfolio
                # NOTE: if 'double_check' == 'no', then 'view_input' will end, returning the user to the start of 'main'
        case 'buy':
            buy_input(chosen_portfolio_name) # 'buy' takes a portfolio name as a parameter
        case 'sell':
            sell_input(chosen_portfolio_name) # 'sell' takes a portfolio name as a parameter


def create_input():
    """
    The purpose of this function is create a new 'Port()' portfolio object at the user's request. Through user input,
    this function will collect the desired portfolio name (after some input error handling), and then ask the user what
    they want to do next (similar to 'view_input()' at the end, just without a few options for practical reasons).
    """

    # Get a set of existing folder names (Sets are faster for lookups than lists)
    # Convert to lower case immediately for spelling error forgiveness
    existing_portfolios = {f.name.lower() for f in Path("Portfolios").iterdir() if f.is_dir()}

    while True:
        # Best way to check multiple conditions with different error messages.
        # If any of the cases fail below, it gives the error message and repeats the loop:
        portfolio_name = input("\nWhat would you like to call your portfolio (MAX: 23 chars): ")
        portfolio_name_check = input("Confirm portfolio name (MAX: 23 chars): ")

        # 1. Check length constraint: will be off the console screen in most cases if over 23 chars:
        if len(portfolio_name) >= 23 or len(portfolio_name_check) >= 23:
            print(f"\n{'*' * 14} ERROR! CHOSEN NAME EXCEEDS 23 CHARACTERS. TRY AGAIN. {'*' * 14}")
            continue  # Jump back to the start of the loop

        # 2. Check for matching inputs:
        if portfolio_name != portfolio_name_check:
            print(f"\n{'*' * 14} ERROR! THOSE NAMES DON'T MATCH. TRY AGAIN. {'*' * 14}")
            continue

        # 3. Check for existing names (case-insensitive):
        if portfolio_name.lower() in existing_portfolios:
            print(f"\n{'*' * 14} ERROR! THAT NAME IS ALREADY BEING USED. ENTER ANOTHER {'*' * 14}")
            continue

        # If we made it here, all checks passed, exit the loop:
        break

    # Initializing an empty Port() object with the users custom portfolio name:
    port_object = Port(name=portfolio_name)
    # Save the portfolio to the 'Portfolios' folder:
    port_object.save_to_csv(f"Portfolios/{portfolio_name}/{portfolio_name}.csv") # save it as a csv file
    print("Your empty portfolio was added to the 'Portfolios' folder!") # output message

    # User Decision:
    # Do you want to buy, sell, view other, or exit?
    user_decision = input("Do you want to 'buy' assets with this portfolio, 'view' another portfolio,"
                          " 'create' a new portfolio, or 'exit' the program?\nPlease enter 'Buy', 'View', 'Create', "
                          "or 'Exit': ").lower()
    # Input Error Handling:
    while user_decision not in ['buy', 'view', 'create', 'exit']:
        user_decision = input("\nINVALID INPUT! INPUT OPTIONS ARE 'Buy', 'Sell', 'View', or 'Exit': ").lower()

    # Match - Case ladder:
    match user_decision:
        case 'exit':
            print("Exiting the Program")
            sys.exit()  # Stops the program immediately
        case 'view':
            view_input()
        case 'create':
            create_input()
        case 'buy':
            buy_input(portfolio_name)
        # No 'sell' here because there's no case where you create an empty portfolio and then sell from it
        # similar reasoning for not including 'delete', and 'refresh'


def buy_input(portfolio_name):
    """
    The purpose of this function is allow the user to purchase a sold assets from yahoo finance, and add it to the
    portfolio they are currently 'viewing'. These assets range from but are not limited too stocks, ETFs, futures,
    cryptocurrency, and foreign currency pairs. The user has the option to either sell by inputting a number of shares
    or an amount in dollars.

    :param portfolio_name: The name of the user's chosen portfolio from either a 'view_input()' or 'create_input()'
    call. This parameter is used in a 'load_from_csv()' to reference the relative file path that the portfolio is
    saved in.
    """

    # LOAD PORTFOLIO DATA SECTION --------------------------------------------------------------------------------------
    # Load the portfolio from either the 'view_input()' or 'create_input()':
    portfolio = Port.load_from_csv(f"Portfolios/{portfolio_name}/{portfolio_name}.csv",
                                   name={portfolio_name.lower().capitalize()}) # Aesthetic choice
    
    
    # BUY_INPUT LOOP SECTION -------------------------------------------------------------------------------------------
    exit_buy = False
    while not exit_buy: # while 'exit_buy' is True:
        # Some assets on Yahoo Finance have symbols in them to denote what class they are in:

        #   ASSET CATEGORY   SYMBOL   TICKER FORMAT               EXAMPLE
        # -----------------------------------------------------------------------------
        # • Cryptocurrency:    (-)   [TOKEN]-[FIAT]:	   BTC-USD
        # • Preferred Stocks:  (-)   [TICKER]-P[CLASS]:    BAC-PL
        # • Foreign Equities:  (.)   [TICKER].[EXCHANGE]:  RY.TO (Royal Bank of Canada)
        # • Currencies:        (=)   [CURRENCY]=X:         JPY=X
        # • Futures:           (=)   [COMMODITY]=F:        NQ=F (Nasdaq 100 Futures)
        # • Market Indices:    (^)   ^[INDEX]:             ^IXIC (Nasdaq Composite)
        # -----------------------------------------------------------------------------

        # TICKER INPUT SECTION -----------------------------------------------------------------------------------------
        # Create a table that maps these symbols to None (deleting them):
        remove_symbols = str.maketrans('', '', '-.=^')

        while True:
            # What asset does the user want to buy:
            ticker = input("\nWhat is the ticker of the stock/ETF you want to buy: ").upper()  # converts to UPPERCASE

            # Input Error Checking:
            # Check 1: Is the ticker alphabetical (ignoring special Yahoo symbols)?
            if not ticker.translate(remove_symbols).isalpha():
                print(f"\n{'*' * 14} ERROR! YOU DIDN'T ENTER AN ALPHABETICAL VALUE {'*' * 14}")
                continue  # Restart this loop to ask again

            # Check 2: Is this ticker a valid ticker from Yahoo Finance?
            if not ticker_exists(ticker):  # while 'ticker_exists()' returns false...(while ticker doesn't exist):
                print(f"\n{'*' * 14} ERROR! YOU DIDN'T ENTER A VALID TICKER. CHECK SPELLING AND LISTINGS {'*' * 14}")
                continue  # Restart this loop to ask again

            # If it passes both checks, we break out of the loop:
            break


        # PURCHASE TYPE SECTION ----------------------------------------------------------------------------------------
        while True:
            # How does the user want to buy this asset:
            amount_input = input(
                "\nWould you like to buy by share amount or $ value? Please type either 'Share' or 'Dollar': ").lower()

            # Input Error Checking:
            if amount_input in ['share', 'dollar']:
                # Assign the validated input and exit:
                amount = amount_input
                break

            print(f"\n{'*' * 14} INVALID INPUT! TRY AGAIN. 'Share' or 'Dollar' {'*' * 14}")


        # BUY IN SHARES SECTION ----------------------------------------------------------------------------------------
        # If the user chose to buy using shares:
        if amount == 'share':
            # Input Error Checking:
            while True:
                try:
                    amountBought = float(input(f"\nEnter the number of shares of {ticker} you would you like to buy: "))
                    break
                except ValueError:
                    print(f"\n{'*' * 14} ERROR! YOU DIDN'T ENTER A NUMERIC VALUE {'*' * 14}")

            amountBought = round(amountBought, 2)  # hundredths place

            # Actually buying the asset:
            portfolio.buy(ticker, shares=amountBought) # buy it
            portfolio.refresh_prices() # refresh all close data
            portfolio.save_to_csv(f"Portfolios/{portfolio_name}/{portfolio_name}.csv")# save it
            print(portfolio) # view purchase

            # Option to repeat the 'buy_input()' function:
            while True:
                buy_again_input = input("\nDo you want to buy anything else?\n'Yes' or 'No': ").lower()

                # Condition to exit the loop:
                if buy_again_input in ['yes', 'no']:
                    break # break this while loop, and then return to the beginning of 'buy_input'

                print(f"\n{'*' * 14} ERROR! INVALID INPUT. {'*' * 14}")

            # If the user doesn't want to buy anything else:
            if buy_again_input == 'no':
                exit_buy = True # leave the buy loop, return to beginning of 'main'


        # BUY IN DOLLARS SECTION ---------------------------------------------------------------------------------------
        # Else the user chose to buy with dollars:
        else:
            # Input Error Checking:
            while True:
                try:
                    amountBought = float(input(f"\nEnter how much of {ticker} you would you like to buy: $"))
                    break
                except ValueError:
                    print(f"\n{'*' * 14} ERROR! YOU DIDN'T ENTER A NUMERIC VALUE {'*' * 14}")

            amountBought = round(amountBought, 2)

            # Actually buying the asset:
            portfolio.buy(ticker, amount=amountBought) # buy it
            portfolio.refresh_prices()  # refresh all close data
            portfolio.save_to_csv(f"Portfolios/{portfolio_name}/{portfolio_name}.csv")  # save it
            print(portfolio) # view purchase

            # Option to repeat the 'buy_input()' function:
            while True:
                buy_again_input = input("\nDo you want to buy anything else?\n'Yes' or 'No': ").lower()

                # Condition to exit the loop:
                if buy_again_input in ['yes', 'no']:
                    break  # break this while loop, and then return to the beginning of 'buy_input'

                print(f"\n{'*' * 14} ERROR! INVALID INPUT. {'*' * 14}")

            # If the user doesn't want to buy anything else:
            if buy_again_input == 'no':
                exit_buy = True  # leave the buy loop, return to beginning of 'main'


def sell_input(portfolio_name):
    """
    The purpose of this function is allow the user to sell assets from yahoo finance, and remove it from the
    portfolio they are currently 'viewing'. These assets range from but are not limited too stocks, ETFs, futures,
    cryptocurrency, and foreign currency pairs. The user has the option to either sell by inputting a number of shares
    or an amount in dollars.

    :param portfolio_name: The name of the user's chosen portfolio from either a 'view_input()' or 'create_input()'
    call. This parameter is used in a 'load_from_csv()' to reference the relative file path that the portfolio is
    saved in.
    """
    
    # LOAD PORTFOLIO DATA SECTION --------------------------------------------------------------------------------------
    # Load the portfolio from either the 'view_input()' or 'create_input()':
    portfolio = Port.load_from_csv(f"Portfolios/{portfolio_name}/{portfolio_name}.csv",
                                   name={portfolio_name.lower().capitalize()})  # Aesthetic choice

    # get the list of the tickers of the portfolio you are viewing ('.index' because 'ticker' col IS the index):
    ticker_list = portfolio.index.tolist()

    # SELL_INPUT LOOP SECTION ------------------------------------------------------------------------------------------
    exit_sell = False
    while not exit_sell: # while 'exit_buy' is True:
        # Some asset on Yahoo Finance have symbols in them to denote what class they are in:

        #   ASSET CATEGORY   SYMBOL   TICKER FORMAT               EXAMPLE
        # -----------------------------------------------------------------------------
        # • Cryptocurrency:    (-)   [TOKEN]-[FIAT]:	   BTC-USD
        # • Preferred Stocks:  (-)   [TICKER]-P[CLASS]:    BAC-PL
        # • Foreign Equities:  (.)   [TICKER].[EXCHANGE]:  RY.TO (Royal Bank of Canada)
        # • Currencies:        (=)   [CURRENCY]=X:         JPY=X
        # • Futures:           (=)   [COMMODITY]=F:        NQ=F (Nasdaq 100 Futures)
        # • Market Indices:    (^)   ^[INDEX]:             ^IXIC (Nasdaq Composite)
        # -----------------------------------------------------------------------------

        # TICKER INPUT SECTION -----------------------------------------------------------------------------------------
        # Create a table that maps these symbols to None (deleting them):
        remove_symbols = str.maketrans('', '', '-.=^')

        while True:
            # What asset does the user want to sell:
            ticker = input("\nChoose which stock/ETF from your portfolio you want to sell:\n "
                           f"{ticker_list} : ").upper()

            # Input Error Checking:
            # Check 1: Is the ticker alphabetical (ignoring special Yahoo symbols)?
            if not ticker.translate(remove_symbols).isalpha(): # while input 'ticker' is not alpha, minus special chars
                print(f"\n{'*' * 14} ERROR! YOU DIDN'T ENTER AN ALPHABETICAL VALUE {'*' * 14}")
                continue # Restart this loop to ask again

            # Check 2: Is this ticker a valid ticker from Yahoo Finance?
            if ticker not in ticker_list:  # if the input isn't in your portfolio:
                print(f"\n{'*' * 14} ERROR! YOU DIDN'T ENTER A TICKER FROM YOUR PORTFOLIO {'*' * 14}")
                continue # Restart this loop to ask again

            break # If it passes both checks, we break out of the loop:

        # USEFUL VARIABLES SECTION -------------------------------------------------------------------------------------
        # After we get the 'ticker', we can calculate the number of shares/dollars the user currently owns of the asset.
        # This will be very useful below as we can call these in f-strings to reference specific asset price data:
        owned_shares = portfolio.loc[ticker, 'SharesOwned']
        owned_dollars = portfolio.loc[ticker, 'MarketValue']


        # PURCHASE TYPE SECTION ----------------------------------------------------------------------------------------
        while True:
            # How does the user want to buy this asset:
            amount_input = input(
                "\nWould you like to sell by share amount, $ value, or sell ALL? Please type either "
                "'Share', 'Dollar', or 'All': ").lower()

            # Input Error Checking:
            if amount_input in ['share', 'dollar', 'all']:
                # Assign the validated input and exit:
                amount = amount_input
                break # If it passes the check, we break out of the loop:

            print(f"\n{'*' * 14} INVALID INPUT! TRY AGAIN. 'Share', 'Dollar', or 'All' {'*' * 14}")


        # SELL ALL SECTION ---------------------------------------------------------------------------------------------
        # If the user wants to sell all of the asset:
        if amount == 'all':
            # Ask user for confirmation:
            while True:
                sell_all_input = input(
                    f"\nAre you sure you want to sell all {owned_shares:,.2f} shares of "
                    f"{ticker}?\n'Yes' or 'No': ").lower()

                # Input Error Checking:
                if sell_all_input in ['yes', 'no']:
                    break # If it passes the check, we break out of the loop:

                print(f"\n{'*' * 14} ERROR! INVALID INPUT. {'*' * 14}")

            # Do what the user wants:
            if sell_all_input == 'no':
                continue  # back to the beginning of the first while loop of the 'sell_input' function

            # If code reaches here, it must be 'yes':
            print(f"\nYou sold all of {ticker}:\n")  # Confirmation Message
            portfolio.sell(ticker, shares=portfolio.loc[ticker, 'SharesOwned'])  # sell all of it
            portfolio.refresh_prices()  # refresh all close data
            portfolio.save_to_csv(f"Portfolios/{portfolio_name}/{portfolio_name}.csv")  # save it
            print(portfolio)  # view purchase
            break  # Back to 'View', 'Create', or 'Exit' menu selection


        # SELL IN SHARES SECTION ---------------------------------------------------------------------------------------
        # If the user chose to sell using shares:
        elif amount == 'share':

            amountSold = 0.0 # Pre-declare to avoid 'possibly undefined' scope errors for this variable.
            # Input Error Checking:
            while True:
                # Input error checking:
                # Check 1: Make sure user input is numeric:
                try:
                    amountSold = float(input(f"\nEnter the number of shares of {ticker} you would you like to sell out "
                                             f"of your {owned_shares:,.2f} shares: "))
                except ValueError:
                    print(f"\n{'*' * 14} ERROR! YOU DIDN'T ENTER A NUMERIC VALUE {'*' * 14}")
                    continue # back to the beginning of this while loop

                # Check 2: Does the user have enough of the asset to sell:
                if amountSold > owned_shares:
                    print(f"\n{'*' * 14} ERROR! YOU DON'T HAVE {amountSold:,.2f} SHARES OF {ticker}{'*' * 14}\n"
                          f"{'*' * 14} YOU ONLY HAVE {owned_shares:,.2f} SHARES OF "
                          f"{ticker}!!! {'*' * 14}")
                    continue # back to the beginning of this while loop

                # If we made it past the 'except' and the 'if', the input is valid:
                amountSold = round(amountSold, 2)  # hundredths place
                break # exit the while loop

            # Actually selling the asset:
            print("\nSale Completed:\n")
            portfolio.sell(ticker, shares=amountSold) # sell it
            portfolio.refresh_prices()  # refresh all close data
            portfolio.save_to_csv(f"Portfolios/{portfolio_name}/{portfolio_name}.csv")  # save it
            print(portfolio)  # view purchase


            # Option to repeat the 'sell_input()' function:
            while True:
                sell_again_input = input("\nDo you want to sell anything else?\n'Yes' or 'No': ").lower()

                # Condition to exit the loop:
                if sell_again_input in ['yes', 'no']:
                    break  # break this while loop, and then return to the beginning of 'sell_input'

                print(f"\n{'*' * 14} ERROR! INVALID INPUT. {'*' * 14}")

            # If the user doesn't want to sell anything else:
            if sell_again_input == 'no':
                exit_sell = True  # leave the sell loop, return to beginning of 'main'


        # SELL IN DOLLARS SECTION --------------------------------------------------------------------------------------
        # If the user chose to sell using dollars:
        else:

            amountSold = 0.0 # Pre-declare to avoid 'possibly undefined' scope errors for this variable.
            # Input Error Checking:
            while True:
                # Input error checking:
                # Check 1: Make sure user input is numeric:
                try:
                    amountSold = float(
                        input(f"\nEnter the number of dollars of {ticker} you would you like to sell "
                              f"out of your ${owned_dollars:,.2f} in market value: "))
                except ValueError:
                    print(f"\n{'*' * 14} ERROR! YOU DIDN'T ENTER A NUMERIC VALUE {'*' * 14}")
                    continue  # back to the beginning of this while loop

                # Check 2: Does the user have enough of the asset to sell:
                if amountSold > owned_dollars:
                    print(f"\n{'*' * 14} ERROR! YOU DON'T HAVE {amountSold:,.2f} SHARES OF {ticker}{'*' * 14}\n"
                          f"{'*' * 14} YOU ONLY HAVE {owned_dollars:,.2f} SHARES OF "
                          f"{ticker}!!! {'*' * 14}")
                    continue  # back to the beginning of this while loop

                # If we made it past the 'except' and the 'if', the input is valid:
                amountSold = round(amountSold, 2)  # hundredths place
                break  # exit the while loop

            # Actually selling the asset:
            print("\nSale Completed:\n")
            portfolio.sell(ticker, amount=amountSold)  # sell it
            portfolio.refresh_prices()  # refresh all close data
            portfolio.save_to_csv(f"Portfolios/{portfolio_name}/{portfolio_name}.csv")  # save it
            print(portfolio)  # view purchase

            # Option to repeat the 'sell_input()' function:
            while True:
                sell_again_input = input("\nDo you want to sell anything else?\n'Yes' or 'No': ").lower()

                # Condition to exit the loop:
                if sell_again_input in ['yes', 'no']:
                    break  # break this while loop, and then return to the beginning of 'sell_input'

                print(f"\n{'*' * 14} ERROR! INVALID INPUT. {'*' * 14}")

            # If the user doesn't want to sell anything else:
            if sell_again_input == 'no':
                exit_sell = True  # leave the sell loop, return to beginning of 'main'
