"""
@author: Kelsey Corro, Cory J. Cascalheira
Created: 2022-10-18
Updated: 2022-10-29

This script imports .csv files that were created from "04_condense_data.py"
that contain monkeypox data and combines them into one file.
It does the same with the .csv files that contain virus data and also shows
some simple analysis that was done on all files.

Here's some info I found for the data:
r_lgbt contained 743 rows of data that had a term relating to monkeypox.
r_gaymers contained 5 rows of data that had a term relating to monkeypox.
r_ainbow contained 9 rows of data that had a term relating to monkeypox.
r_askgaybros contained 8077 rows of data that had a term relating to monkeypox.
r_asktransgender contained 26 rows of data that had a term relating to monkeypox.
r_MtF contained 44 rows of data that had a term relating to monkeypox.
r_NonBinary contained 5 rows of data that had a term relating to monkeypox.

There were a total of 8909 comments from the top 9 lgbt subreddits that contained a term relating to monkeypox.

r_lgbt contained 335 rows of data that had a term relating to virus.
r_gaymers contained 36 rows of data that had a term relating to virus.
r_ainbow contained 11 rows of data that had a term relating to virus.
r_askgaybros contained 4729 rows of data that had a term relating to virus.
r_asktransgender contained 209 rows of data that had a term relating to virus.
r_MtF contained 246 rows of data that had a term relating to virus.
r_NonBinary contained 24 rows of data that had a term relating to virus.

There were a total of 5590 comments from the top 9 lgbt subreddits that contained a term relating to virus.

"""

# import pandas library to use dataframes
import pandas as pd

# Import all csv files that contain the monkeypox data
lgbt_mpx_csv = pd.read_csv( "lgbt_subreddit_mpx_data.csv" )
gaymers_mpx_cvs = pd.read_csv( "gaymers_subreddit_mpx_data.csv" )
ainbow_mpx_cvs = pd.read_csv( "ainbow_subreddit_mpx_data.csv" )
askgaybros_mpx_csv = pd.read_csv( "askgaybros_subreddit_mpx_data.csv" )
asktransgender_mpx_csv = pd.read_csv( "asktransgender_subreddit_mpx_data.csv" )
MtF_mpx_csv = pd.read_csv( "MtF_subreddit_mpx_data.csv" )
NonBinary_mpx_csv = pd.read_csv( "NonBinary_subreddit_mpx_data.csv" )

# Convert all csv files into dataframes
lgbt_mpx = pd.DataFrame( lgbt_mpx_csv )
gaymers_mpx = pd.DataFrame( gaymers_mpx_cvs )
ainbow_mpx = pd.DataFrame( ainbow_mpx_cvs )
askgaybros_mpx = pd.DataFrame( askgaybros_mpx_csv )
asktransgender_mpx = pd.DataFrame( asktransgender_mpx_csv )
MtF_mpx = pd.DataFrame( MtF_mpx_csv )
NonBinary_mpx = pd.DataFrame( NonBinary_mpx_csv )

# -------------------------------------------------------------------------- #

# Import all csv files that contain the virus data
lgbt_virus_csv = pd.read_csv( "lgbt_subreddit_virus_data.csv" )
gaymers_virus_cvs = pd.read_csv( "gaymers_subreddit_virus_data.csv" )
ainbow_virus_cvs = pd.read_csv( "ainbow_subreddit_virus_data.csv" )
askgaybros_virus_csv = pd.read_csv( "askgaybros_subreddit_virus_data.csv" )
asktransgender_virus_csv = pd.read_csv( "asktransgender_subreddit_virus_data.csv" )
MtF_virus_csv = pd.read_csv( "MtF_subreddit_virus_data.csv" )
NonBinary_virus_csv = pd.read_csv( "NonBinary_subreddit_virus_data.csv" )

# Convert all csv files into dataframes
lgbt_virus = pd.DataFrame( lgbt_virus_csv )
gaymers_virus = pd.DataFrame( gaymers_virus_cvs )
ainbow_virus = pd.DataFrame( ainbow_virus_cvs )
askgaybros_virus = pd.DataFrame( askgaybros_virus_csv )
asktransgender_virus = pd.DataFrame( asktransgender_virus_csv )
MtF_virus = pd.DataFrame( MtF_virus_csv )
NonBinary_virus = pd.DataFrame( NonBinary_virus_csv )

# -------------------------------------------------------------------------- #

# Add the names off all the subreddits into a list called subreddits
subreddits_mpx = [ lgbt_mpx, gaymers_mpx, ainbow_mpx, askgaybros_mpx, 
               asktransgender_mpx, MtF_mpx, NonBinary_mpx ]
subreddit_str = [ "r_lgbt", "r_gaymers", "r_ainbow", "r_askgaybros", 
                  "r_asktransgender", "r_MtF", "r_NonBinary" ]

print()
# Find out the number of rows from each subreddit that contained a term
# relating to monkeypox
for x in range(len( subreddits_mpx )):
    print( subreddit_str[ x ], "contained", len( subreddits_mpx[ x ]),
           "rows of data that had a term relating to monkeypox.")
print()

# Add the names off all the subreddits into a list called subreddits
subreddits_virus = [ lgbt_virus, gaymers_virus, ainbow_virus, askgaybros_virus, 
               asktransgender_virus, MtF_virus, NonBinary_virus ]
subreddit_str = [ "r_lgbt", "r_gaymers", "r_ainbow", "r_askgaybros", 
                  "r_asktransgender", "r_MtF", "r_NonBinary" ]

print()
# Find out the number of rows from each subreddit that contained a term
# relating to monkeypox
for x in range(len( subreddits_virus )):
    print( subreddit_str[ x ], "contained", len( subreddits_virus[ x ]),
           "rows of data that had a term relating to virus.")
print()

# Combine all subreddit dataframes together
mpx_data = pd.concat( subreddits_mpx )
virus_data = pd.concat( subreddits_virus )

print( "There were a total of", len(mpx_data), 
      "comments from the top 9 lgbt subreddits that contained a term relating to monkeypox." )
print( "There were a total of", len(virus_data), 
      "comments from the top 9 lgbt subreddits that contained a term relating to virus." )

# Create a .csv file that contains all the data
mpx_data.to_csv('all_subreddits_mpx_data.csv', index=False)
virus_data.to_csv('all_subreddits_virus_data.csv', index = False)

#region MANUAL CALCULATIONS

# Get total comments from 03_initial_analysis file
total_comments = 588141 + 41774 + 14180 + 680019 + 287576 + 389032 + 132601 + 286635 + 106679

# Get MPX-specific comments from current file
mpx_comments = 8909

# Percent related to MPX
mpx_comments / total_comments

#endregion
