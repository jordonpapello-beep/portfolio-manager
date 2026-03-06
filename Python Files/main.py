import pandas as pd # for adjusting the console display settings of the portfolio Data Frames
from interface import view_input, create_input # important to do it like this because if we just 'import interface',
# then in this file we would have to call the functions from this file like: 'interface.view_input()'.

# Pandas settings that change the way the data frames are displayed in the console (Clean Look):
pd.set_option('display.max_columns', None) # Shows all columns in a dataframe
pd.set_option('display.max_rows', None) # Shows all rows in a dataframe
pd.set_option('display.precision', 2) # 2 decimal places of precision for elements in a dataframe
pd.set_option('display.max_colwidth', None) # Set maximum column width to None, so it doesn't clip long text in cells
pd.set_option('display.expand_frame_repr', False) # Doesn't clip wide dataframes but putting second half below!!!!

# MAIN CODE:------------------------------------------------------------------------------------------------------------

def main():
    while True: # Run unless a specific call to break the loop is called:
        choice = input("Enter either 'Create', 'View', or 'Exit': ").lower() # initial user input

        # Input Error Checking:
        while choice not in ['create', 'view', 'exit']:
            choice = input("\nINVALID INPUT! INPUT OPTIONS ARE 'Create', 'View', or 'Exit': ")

        # User input menu selection match case ladder:
        match choice:
            # 'Exit':
            case 'exit':
                print("Exiting the program.")
                break  # exit the program

            # 'View':
            case 'view':
                view_input()

            # 'Create':
            case 'create':
                create_input()


if __name__ == "__main__":
    main()