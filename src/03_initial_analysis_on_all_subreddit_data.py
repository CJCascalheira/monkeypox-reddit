'''
@author: Kelsey Corro
Created: 2022-10-13

This script imports all the .csv files created from the script
"02_convert_json_to_csv.py" and converts the .csv files into dataframes.

Simple analysis is done on all the dataframes (ie. finding out how many
                                               instances are in each dataframe)

Here is some basic information on the .csv files that were imported:
r_lgbt contains 588141 rows of data
r_gaymers contains 41774 rows of data
r_ainbow contains 14180 rows of data
r_askgaybros contains 680019 rows of data
r_asktransgender contains 287576 rows of data
r_MtF contains 389032 rows of data
r_NonBinary contains 132601 rows of data
r_ftm contains 286635 rows of data
r_BisexualTeens contains 106679 rows of data

Basic description of data collected:
    Each .csv file is titled with the subreddit the comments were obtained 
    from. These comments were extracted on the basis that they were submitted
    after May 01, 2022 @ 12:00 am UTC. The reason why this time frame is
    relavant is because that is when outbreaks of monkeypox started to get 
    reported.
'''
# import pandas library to use dataframes
import pandas as pd

# Import all csv files 
r_lgbt_csv = pd.read_csv( "lgbt_subreddit_comments_all.csv" )
r_gaymers_csv = pd.read_csv( "gaymers_subreddit_comments_all.csv" )
r_ainbow_csv = pd.read_csv( "ainbow_subreddit_comments_all.csv" )
r_askgaybros_csv = pd.read_csv( "askgaybros_subreddit_comments_all.csv" )
r_asktransgender_csv = pd.read_csv( "asktransgender_subreddit_comments_all.csv" )
r_MtF_csv = pd.read_csv( "MtF_subreddit_comments_all.csv" )
r_NonBinary_csv = pd.read_csv( "NonBinary_subreddit_comments_all.csv" )
r_ftm_csv = pd.read_csv( "ftm_subreddit_comments_all.csv" )
r_BisexualTeens_csv = pd.read_csv( "BisexualTeens_subreddit_comments_all.csv" )

# Convert all csv files into dataframes
r_lgbt = pd.DataFrame( r_lgbt_csv )
r_gaymers = pd.DataFrame( r_gaymers_csv )
r_ainbow = pd.DataFrame( r_ainbow_csv )
r_askgaybros = pd.DataFrame( r_askgaybros_csv )
r_asktransgender = pd.DataFrame( r_asktransgender_csv )
r_MtF = pd.DataFrame( r_MtF_csv )
r_NonBinary = pd.DataFrame( r_NonBinary_csv )
r_ftm = pd.DataFrame( r_ftm_csv )
r_BisexualTeens = pd.DataFrame( r_BisexualTeens_csv )

# Add the names off all the subreddits into a list called subreddits
subreddits = [ r_lgbt, r_gaymers, r_ainbow, r_askgaybros, r_asktransgender,
               r_MtF, r_NonBinary, r_ftm, r_BisexualTeens ]
subreddit_str = [ "r_lgbt", "r_gaymers", "r_ainbow", "r_askgaybros", 
                  "r_asktransgender", "r_MtF", "r_NonBinary", "r_ftm", 
                  "r_BisexualTeens" ]

print()
# Find out the number of rows from each subreddit
for x in range(len( subreddits )):
    print( subreddit_str[ x ], "contains", len( subreddits[ x ]),
           "rows of data")