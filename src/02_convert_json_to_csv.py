'''
The following script was used to convert the .json files that were created
from the script "01_scrape_subreddit_comments.py" into .csv files.

After each of the nine subreddits were scraped and converted into .csv files,
the files were renamed according to their subreddit.
Example: After scraping the r/lgbt subreddit, the file "comments.json" was 
converted to "comments.csv" and renamed "lgbt_subreddit_comments_all.csv".
'''
# Import pandas library to make use of dataframe features for conversion
import pandas as pd

# Create variables for the input .json file and the output .csv file
input_json_file = 'comments.json'
output_csv_file = 'comments.csv'

# Use pandas to create a dataframe of the .json file
with open( input_json_file ) as inputfile:
    df = pd.read_json(inputfile, lines = True)

# Use pandas to convert dataframe into a .csv file
df.to_csv(output_csv_file, index=False) 