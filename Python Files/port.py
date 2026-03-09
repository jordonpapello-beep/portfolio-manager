import pandas as pd # for Data Frame structure, properties, and functions (Parent Class)
import yfinance as yf # for scraping financial data
from pathlib import Path # for 'disk' operations (saving, loading, and deleting 'portfolio' objects)
import numpy as np # for 'np.nan' (Serves as standard placeholder for empty cells like 'NA', helps w/ error prevention)
from datetime import datetime # for timestamps


class Port(pd.DataFrame):
    """
        Some insight behind the thinking of the following code:
        Subclassing pd.DataFrame is notoriously finicky.
        Pandas operations like .iloc[], .copy(), concat, slicing a column, or .drop() don't just modify
        the existing object; they often CREATE A NEW ONE!!!
        This means, if you haven't told Pandas how to "rebuild" the specific 'Port class', it
        defaults back to a standard pd.DataFrame, and the custom functionality is lost.
        This is a huge problem for this project because the whole idea behind portfolio objects are that they are
        pandas data frames, with some added 'Port' (portfolio) functionality (buying/selling/etc...), and we want
        to be able to use all the pandas functionality (especially in our custom Port Class functions).

        To make a subclass "stick" after using pandas functionality, you need to define two specific internal
        properties: _constructor and _constructor_sliced. Here's what they do specifically:

        • _constructor: This tells Pandas, "When you perform an operation that returns a whole DataFrame
          (like df.drop()), use the Port class to build the new one, not the standard pd.DataFrame." Without this, the
          custom methods like .buy() or .sell() would vanish as soon as you manipulated the data.

        • _constructor_sliced: This is for when a pandas operation returns a single column or row (a Series). Usually,
          we point this back to pd.Series because a single column of stock prices doesn't need to be a full Port object.

        With these implemented, we now don't have to worry about pandas functions returning a Pandas object when
        performed on the custom portfolio objects defined in this class! This is the main hurdle!

        Another important aspect to note obout how this class operates is that it functions around treating the
        'ticker' column of a Port object as the index of the data frame. This makes it much less 'clunky' to perform
        operations on specific cells of a portfolio and makes it much easier to read:
            • With 'ticker' as the index:    self.loc[ticker, "SharesOwned"] = shares
            • Without 'ticker' as the index: self.loc[self['Ticker'] == ticker, 'SharesOwned'] = shares
        """

    # INFORMATION ABOUT _metadata:
    # _metadata: A Pandas-specific "whitelist" for custom attributes.
    # Standard operations (like .copy(), .iloc, or .set_index()) create new object instances.
    # Because Pandas doesn't know about custom variables by default, this list "registers" them, so they persist
    # across those operations instead of being lost.
    # Pandas specifically looks for the name '_metadata' to know which extra attributes (like name, created_at, etc.)
    # need to be "carried over" when it creates a copy of your data.
    _metadata = ["name", "created_at", "last_updated", "realized_pl"]

    @property
    def _constructor(self):
        """
        • The purpose of this function is to tell Pandas, "When you perform an operation that returns a whole DataFrame
          (like df.drop()), use thePort class to build the new one, not the standard pd.DataFrame." Without this, the
          custom methods like .buy() or .sell() would vanish as soon as you manipulated the data.

        • Usually after a Pandas method acts on an object, Pandas will ask _constructor "what clas should the
          result be?" It then checks our @property def _constructor(self), sees 'return Port', and now instead of
          making a generic pd.DataFrame, it runs the Port constructor to build the result! This is also why the
          custom __str__ (the big header) stays visible even after we filter or sort the data. Without this override,
          it would revert to a boring, standard table.

        • The @property decorator turns a method into a "computed attribute". Without it: we'd have to call
          my_portfolio.total_pl(). With it: We can access it like a variable: my_portfolio.total_pl.
          It makes your class feel more like a native Pandas object where you access attributes (like .shape or .index)
          rather than calling functions.

          :return: Port Object.
        """
        return Port

    @property
    def _constructor_sliced(self):
        """
        • This is for when a pandas operation returns a single column or row (a Series). Usually, we point this back
        to pd.Series because a single column of stock prices doesn't need to be a full Port object.

        • The @property decorator turns a method into a "computed attribute". Without it: we'd have to call
          my_portfolio.total_pl(). With it: We can access it like a variable: my_portfolio.total_pl.
          It makes your class feel more like a native Pandas object where you access attributes (like .shape or .index)
          rather than calling functions.

        :return: Pandas Series.
        """
        return pd.Series

    def __init__(self, data=None, name=None, created_at=None, last_updated="Never", realized_pl=0.0, *args, **kwargs):
        """
        Port Object Constructor: called when you want to initialize a 'Port' object.

        :param data: The Data Frame (rows and columns of portfolio info)
        :param names: The name that the user will give to the portfolio.
        :param created_at: Timestamp using 'datetime' that only runs once per portfolio at its creation.
        :param last_updated: Timestamp using 'datetime' that will tell the user the last time the proces were updated.
        :param realized_pl: Running total that keeps track of profit/loss from any sold assets from this portfolio.
        """
        # If no data is provided, initialize with the desired structure below:
        if data is None and not args and not kwargs:
            cols = [
                "SharesOwned", "ActualInvested", "Close", "MarketValue",
                "AverageSharePrice", "UnrealizedGainLoss",
                "UnrealizedGainLossPct", "PortfolioAllocationPct"
            ]
            # Initialize with an empty index named 'Ticker':
            data = pd.DataFrame(columns=cols)
            data.index.name = "Ticker" # set the index to be the 'Ticker' column!!! Very important bc...(how we call
            # .loc[] and .at[] is easier to code and READ) Much easier to say "look for the value in this row for
            # this ticker"!

        super().__init__(data=data, *args, **kwargs) # Why??

        # Metadata assignment:
        self.name = name
        self.last_updated = last_updated
        self.realized_pl = round(float(realized_pl), 2)

        # Set created_at ONLY if it doesn't exist (prevents overwriting on slices):
        if created_at: # if 'created_at' variable has a value (has already been defined):
            self.created_at = created_at # keep it the same
        else:
            # default to current time if no value was provided (is None):
            self.created_at = datetime.now().strftime("%m-%d-%Y %H:%M") # date and time accurate to the minute

    @property
    def total_pl(self):
        """
        • The purpose of this function is to calculate the Total P/L that is displayed in the header of a portfolio:
          Sum of Current Gains + Realized Gains from Sales.

        • The @property decorator turns a method into a "computed attribute". Without it: we'd have to call
          my_portfolio.total_pl(). With it: We can access it like a variable: my_portfolio.total_pl.
          It makes your class feel more like a native Pandas object where you access attributes (like .shape or .index)
          rather than calling functions.

        :return: The Total Profit/Loss which is the sum of the unrealized P/L from portfolio and realized metadata.
        """
        unrealized = self["UnrealizedGainLoss"].sum() if not self.empty else 0 # sum of P/L column in portfolio
        return round(unrealized + self.realized_pl, 2) # adding the sum with the already saved value (if any)

    def __str__(self):
        """
        • The purpose of this function is to override pandas' default __str__, and redefine how we want our object
          to be printed in the console.
            • Default: Printing a DataFrame just shows the table.
            • Override: Added custom 150-character wide header with the Portfolio Name, Realized P/L, etc. By calling
              super().__str__() at the end, we're telling Python: "Print my custom header first, then print the
              standard Pandas table below it."

        :return: Prints the Port object in the console with our custom header first with metadata then the portfolio.
        """

        portfolio_display_name = self.name or "Portfolio"
        header = (f"\n{'=' * 150}\n"
                  f"Portfolio Name: {portfolio_display_name} || Created: {self.created_at} || Last Updated: "
                  f"{self.last_updated} || REALIZED P/L: ${self.realized_pl:,.2f} || TOTAL P/L: ${self.total_pl:,.2f}\n"
                  f"{'=' * 150}\n")
        return header + super().__str__() + "\n"

    # PORTFOLIO OPERATIONS/MUTATORS: -----------------------------------------------------------------------------------

    def buy(self, ticker, shares=None, amount=None):
        """
        • The purpose of this function is to add shares/dollars to an asset (row) of a port object by checking the
          assets current price on Yahoo Finance and using that to calculate how much it would cost to buy the specified
          number of shares or how many shares the user purchased based on the amount in dollars they are choosing
          to spend.

        :param ticker: The abbreviation used to denote the asset in the stock market.
        :param shares: The number of shares that you want to sell.
        :param amount: The amount in dollars that you want to sell.
        """

        # # Check to make sure user/programmer inputs the parameters correctly:
        if (shares is None and amount is None) or (shares is not None and amount is not None):
            raise ValueError("Must provide either shares OR amount, not both.") # raise error and terminate function

        # Initialize a Yahoo Finance Ticker object in order to get the price data for the asset:
        t = yf.Ticker(ticker) # initialization
        price = t.fast_info['last_price'] # fast_info is quicker than download() for a single price point

        if amount is not None: # if the 'amount' parameter is used to buy:
            shares = amount / price # calculate number of shares purchased from amount of money spent
        cost = shares * price # calculate total price paid using shares purchased

        # If ticker exists in the index of your portfolio already, update it:
        # NOTE: .at[] is designed for accessing or setting a single scalar value (a single cell) as fast as possible.
        # It bypasses much of the overhead that Pandas uses to check for slices, lists, or boolean arrays. It's useful
        # to know this because if you are running a 'buy' with a loop with 100,000 iterations for example, using .at[]
        # instead of .loc[] for single values could save you significant execution time.
        if ticker in self.index:
            self.at[ticker, "SharesOwned"] += shares
            self.at[ticker, "ActualInvested"] += cost
            self.at[ticker, "Close"] = price

        # Else it must be a new ticker, just use .loc to create the row:
        # NOTE: .loc[] is label-based, but it is built to handle groups of rows and columns. When you need to select
        # multiple rows, multiple columns, use slices (e.g., df.loc['AAPL':'MSFT']), or use boolean masks
        # (e.g., df.loc[df['Price'] > 100]).
        else:
            self.loc[ticker, "SharesOwned"] = shares
            self.loc[ticker, "ActualInvested"] = cost
            self.loc[ticker, "Close"] = price

        self._recalculate() # after the purchase is completed, recalculate

    def sell(self, ticker, shares=None, amount=None):
        """
        • The purpose of this function is to reduce shares/dollars of an asset (row) of a port object by the
          specified amount of shares/dollars, and to record the realized profit/loss from this sale if any.

        :param ticker: The abbreviation used to denote the asset in the stock market.
        :param shares: The number of shares that you want to sell.
        :param amount: The amount in dollars that you want to sell.
        """

        # Check to make sure user/programmer inputs the parameters correctly:
        if (shares is None and amount is None) or (shares is not None and amount is not None):
            raise ValueError("Must provide either shares OR amount, not both.") # raise error and terminate function

        # Must have the asset in your portfolio in order to sell it:
        if ticker not in self.index:
            print(f"Error: {ticker} not found in portfolio.")
            return # terminate function

        # Initialize a Yahoo Finance Ticker object in order to get the price data for the asset:
        t = yf.Ticker(ticker) # initialization
        price = t.fast_info['last_price'] # fast_info is quicker than download() for a single price point

        # If the 'amount' parameter has a value:
        if amount is not None:
            shares = amount / price

        # Check to ensure that you cannot try to sell more of the asset than you own:
        current_shares = self.at[ticker, "SharesOwned"]
        if shares > current_shares:
            print(f"\n{'*' * 13} ERROR: NOT ENOUGH SHARES OF {ticker} TO SELL. {'*' * 13}") # error message
            return # terminate function

        # Updating the realized Profit/Loss running total, and the 'SharesOwned', 'ActualInvested', and 'Close' columns:
        # 1. Calculate the cost basis of the shares being sold:
        avg_price = self.at[ticker, "ActualInvested"] / current_shares
        cost_of_shares_sold = shares * avg_price

        # 2. Calculate Realized P/L for this specific trade:
        sale_proceeds = shares * price
        trade_realized_pl = sale_proceeds - cost_of_shares_sold

        # 3. Add to the portfolio's running total:
        self.realized_pl += trade_realized_pl

        # Update the position o the portfolio:
        self.at[ticker, "SharesOwned"] -= shares
        self.at[ticker, "ActualInvested"] -= cost_of_shares_sold
        self.at[ticker, "Close"] = price

        # If after a sell you don't own enough shares of an asset, remove that asset's row from the portfolio entirely:
        if self.at[ticker, "SharesOwned"] < 0.0001:
            self.drop(ticker, inplace=True)

        self._recalculate() # after the sell is completed, recalculate

    def _recalculate(self):
        """
        • The purpose of this function is to update all calculated financial columns of a port object. It is meant
          to run after a 'buy()' or 'sell()' is performed, or after a 'refresh_prices()' is called.
        """

        if self.empty:
            return # terminate function

        self["MarketValue"] = self["SharesOwned"] * self["Close"]

        shares_denom = self["SharesOwned"].replace(0, np.nan)
        self["AverageSharePrice"] = self["ActualInvested"] / shares_denom

        self["UnrealizedGainLoss"] = self["MarketValue"] - self["ActualInvested"]

        invested_denom = self["ActualInvested"].replace(0, np.nan)
        self["UnrealizedGainLossPct"] = (self["UnrealizedGainLoss"] / invested_denom) * 100

        total_val = self["MarketValue"].sum()
        if total_val > 0:
            self["PortfolioAllocationPct"] = (self["MarketValue"] / total_val) * 100

        # Global rounding for clean data display in the console:
        numeric_cols = self.select_dtypes(include=[np.number]).columns
        self[numeric_cols] = self[numeric_cols].round(2)

    def refresh_prices(self):
        """
        • The purpose of this function is to update all 'Close' prices using the Ticker index of a port object by
          re-downloading the close information for an asset from Yahoo Finance. This function is ran in the interface
          after a portfolio is loaded from its relative file path, and after a buy or sell is performed on the 
          portfolio.
        """

        if self.empty:
            return # terminate function

        tickers = self.index.tolist()
        # Fetching all tickers at once is much faster than one-by-one
        data = yf.download(tickers, period="1d", interval="1d", progress=False)['Close']

        if len(tickers) > 1:
            # map the last row of downloaded prices to our index
            latest_prices = data.iloc[-1]
            self["Close"] = self.index.map(latest_prices)
        else:
            # yfinance returns a Series if only one ticker is requested
            self["Close"] = data.iloc[-1]

        self._recalculate()

    # DISK OPERATIONS: -------------------------------------------------------------------------------------------------

    @staticmethod
    def delete_portfolio_folder(folder_name):
        """
        • The purpose of this function is to delete a port object by deleting the CSV file in which its data is saved.
          Note: Want to keep this function inside the Port class, so it can be called like:
          Port.delete_portfolio_folder("MySavings")

        • This function uses 'pathlib' (Cross-OS-Compatibility).

        • @staticmethod: Methods like delete_portfolio_folder don't actually need to know anything about a specific
          portfolio's data; they just need to talk to the computer's hard drive. By marking it as a staticmethod, we
          allow the user to call Port.delete_portfolio_folder("MyPortfolio") without having to actually create a
          portfolio object first. It’s a "utility" function that lives inside the class for organization.

        :param folder_name: The name that was given to the portfolio by the user (completes relative file path name).
        """

        target_dir = Path("Portfolios") / folder_name

        if target_dir.exists() and target_dir.is_dir():
            for item in target_dir.iterdir():
                if item.is_file():
                    item.unlink()
            target_dir.rmdir()
            print(f"Portfolio '{folder_name}' has been deleted!")
        else:
            print("Folder not found.")

    def save_to_csv(self, filepath):
        """
        • This purpose of this function is to save a portfolio to a relative file path. Furthermore, this function
          handles the extra attributes of a port objects _metadata by placing it in the header. This is also where the
          'last_updated' _metadata gets timestamped.

        • This function uses 'pathlib' (Cross-OS-Compatibility).

        :param filepath: The relative file path where the portfolio will be stored as a CSV file.
        """

        self.last_updated = datetime.now().strftime("%m-%d-%Y %H:%M") # update the 'last updated' timestamp
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write the metadata as comments at the top of the CSV file
        with open(path, 'w') as f:
            f.write(f"# Name: {self.name}\n")
            f.write(f"# Created: {self.created_at}\n")
            f.write(f"# Last Updated: {self.last_updated}\n")
            f.write(f"# Realized PL: {self.realized_pl}\n")
            self.to_csv(f, index=True)

    @staticmethod
    def load_from_csv(filepath, name=None):
        """
        • The purpose of this function is to load a previously saved 'portfolio.csv' by reading the CSV from its
          saved relative file path and returning the port object with the read data and _metadata.

        • This function uses 'pathlib' (Cross-OS-Compatibility).

        • @staticmethod: Methods like load_from_csv don't actually need to know anything about a specific
          portfolio's data; they just need to talk to the computer's hard drive. By marking it as a staticmethod, we
          allow the user to call Port.load_from_csv("MyPortfolio") without having to actually create a
          portfolio object first. It’s a "utility" function that lives inside the class for organization.

        :param filepath: The relative file path where the desired portfolio stored as a CSV file can be accessed.
        :param name: The name that the user will give to the portfolio.
        :return: Port object.
        """
        meta = {"Name": name, "Created": None, "Last Updated": "Unknown", "Realized PL": 0.0}

        with open(filepath, 'r') as f:
            for line in f:
                if line.startswith("#"):
                    line = line.replace("#", "").strip() # get rid of '#' symbol and leading/trailing spaces
                    if ":" in line:
                        key, val = line.split(":", 1)
                        meta[key.strip()] = val.strip()
                else:
                    break

        df = pd.read_csv(filepath, comment='#', index_col="Ticker")

        # Re-initialize with all metadata restored
        return Port(
            data=df,
            name=meta["Name"],
            created_at=meta["Created"],
            last_updated=meta["Last Updated"],
            realized_pl=float(meta["Realized PL"])
        )
