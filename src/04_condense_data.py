"""
@author: Kelsey Corro
Created: 2022-10-14

This script contains the functions to extract the title of a subreddit thread
and to convert epoch time into a human readable date time format.

This script imports the .csv files created from the script 
"02_convert_json_to_csv.py", converts the files into dataframes, then condenses 
the data according to the 8 desired columns: 
    - "author" (User ID)
    - "subreddit" (Subreddit)
    - "body" (Text Comment - information we are most interested in)
    - "created_utc" (Time)
    - "retrieved_utc" (Time)
    - "permalink" (for Thread Title)
    - "link_id" (for Thread Title)
    - parent_id" (for Thread Title)

After condensing the dataframes according to the desired columns, 2 columns
were added using the functions that the script contains:
    - "converted_createdutc": Date & Time in human readable format 
    - "thread_title": Title of thread      

Once the condensed dataframe with the additional columns was obtained, 
the contents of the "thread_title" and "body" column for each instance was 
looked at to see if they contained any terms related to monkeypox or virus.

For the search terms, we want to subset all posts that mention at least one 
of the following words in the comments or titles:
    - monkey pox
    - monkeypox
    - pox
    - orthopox
    - mpx
    - gaypox
    - mpox
    - JYNNEOS
    - ACAM2000

We can use the next five, general search terms as well, but we need to ensure 
are not related solely to COVID-19:
    - virus 
    - CDC
    - vaccine
    - vax
    - vaccinated

Additionally, we made sure that any post related to monkeypox did not have the
term 'epoxy' which was usually related to crafts.

Lastly, once the instances containing monkeypox and virus terms were isolated,
they were exported into .cvs files.

Note: 
    The following subreddits did not contain any terms relating to monkeypox: 
        - r/ftm 
        - r/BisexualTeens 
"""

# import datetime library to convert epoch time into a human readable
# date time format
import datetime

# import pandas library to use dataframes
import pandas as pd

# This function extracts the title of a subreddit thread by using the
# 3 parameters: permalink_id, link_id, and parent_id
def extract_title( permalink_id, link_id, parent_id ):
    
    # Obtain the substring from link_id that occurs right before the desired 
    # title in the permalink_id
    link_id = link_id[3:]

    # Obtain the index of where the title starts by using the link_id substring
    # and utilize the find() function for a substring
    start_index = permalink_id.find( link_id ) + len( link_id ) + 1

    # Obtain the index of where the title ends by using the parent_id substring
    end_index = len( permalink_id ) - len( parent_id[3:] ) - 2

    # With the obtained start index and end index, extract the title
    title = permalink_id[ start_index:end_index ] 
    
    return title

# This function uses the datetime library to convert epoch times into a 
# human readable date time format
# The format will be in yyyy-mm-yy hh:mm:ss 
# This function will return a string in the format specified
def convert_epoch( epoch_time ):
    date_time = datetime.datetime.fromtimestamp( epoch_time )
    return date_time.strftime('%Y-%m-%d %H:%M:%S')

# -------------------------------------------------------------------------- #

# import combined data
# Change the argument for pd.read_csv() accordingly
# lgbt_subreddit_comments_all.csv
# gaymers_subreddit_comments_all.csv
# ainbow_subreddit_comments_all.csv
# askgaybros_subreddit_comments_all.csv
# asktransgender_subreddit_comments_all.csv
# MtF_subreddit_comments_all.csv
# NonBinary_subreddit_comments_all.csv
# ftm_subreddit_comments_all.csv
# BisexualTeens_subreddit_comments_all.csv

data_lgbt = pd.read_csv( "lgbt_subreddit_comments_all.csv" )

data = pd.DataFrame({'author':data_lgbt[ 'author' ], 
                     'body':data_lgbt[ 'body' ], 
                     'subreddit':data_lgbt[ 'subreddit' ],
                     'created_utc':data_lgbt[ 'created_utc' ],
                     'retrieved_utc':data_lgbt['retrieved_utc'],
                     'permalink':data_lgbt['permalink'],
                     'link_id':data_lgbt['link_id'],
                     'parent_id':data_lgbt['parent_id'] })

# -------------------------------------------------------------------------- #

# Create a new list that will contain all the converted times from the
# created_utc column
converted_createdutc = []

# Create a for loop that will go through all rows of the 'created_utc' column
# and append the converted time to the list 'converted_createdutc'
for i in range(len(data['created_utc'])):
    # There are some instances that are registered as strings
    # This if statement will check if the instance is a string
    
    if ( isinstance( data['created_utc'][i], str ) ):
        
        # Some of the string instances are the strings "TRUE" or "FALSE"
        # in which case, we will append "nan" or Not A Number to the 
        # converted_createdutc list
        if ( data['created_utc'][i] == 'TRUE' ):
            converted_createdutc.append( 'nan' )
        elif ( data['created_utc'][i] == 'FALSE' ):
            converted_createdutc.append( 'nan' )
        
        # Some of them are a string of numbers that are in epoch format that
        # need to be converted into an integer before being converted by the
        # convert_epoch () function
        else: 
            x = pd.to_numeric( data['created_utc'][i] )
            converted_createdutc.append( convert_epoch( x ) )
    
    # Some instances are 'nan', in which case, we will append 'nan' or
    # Not a Number to the converted_createdutc list
    elif ( pd.isna( data['created_utc'][i] )):
        converted_createdutc.append( data['created_utc'][i] )
    
    # If the instance is not any of the above, then it is safe to assume that
    # it is an integer that can be converted into human readable format
    # using the convert_epoch () function and that value can then be appended
    # to the converted_createdutc list
    else:
        converted_createdutc.append( convert_epoch( data[ 'created_utc' ][ i ]) )

# Append the list as a new column to the data dataframe
data['converted_createdutc'] = converted_createdutc

# -------------------------------------------------------------------------- #

# Create a new list that will contain all the extracted thread titles of each row
thread_title = []

for i in range( len ( data['permalink' ] )):
    if ( pd.isna( data['permalink'][i] ) ):
        thread_title.append( 'nan' )
    else:
        thread_title.append( extract_title( data['permalink'][i], 
                                           data['link_id'][i],
                                           data['parent_id'][i] ))

# Append the list as a new column to the data dataframe
data['thread_title'] = thread_title        

# -------------------------------------------------------------------------- #

'''
Search terms related to monkeypox:
    - term1: monkey pox
    - term2: monkeypox
    - term3: pox
    - term4: orthopox
    - term5: mpx
    - term6: gaypox
    - term7: mpox
    - term8: JYNNEOS
    - term9: ACAM2000

Search terms related to virus:
    - term1: virus 
    - term2: CDC
    - term3: vaccine
    - term4: vax
    - term5: vaccinated
'''

# Create a new list that will contain a classifier that determines whether
# a monkeypox term is found in either the comment or the title thread of an
# instance
contains_monkeypox_term = []

# Go through each instance and identify whether a monkeypox term is found
# If it is found, the integer 1 will indicate that it is found
# If it is not found, the integer 0 will indicate that it is not found
for i in range( len ( data[ 'body' ] )):
    if ( pd.isna( data['body'][i] ) ):
        contains_monkeypox_term.append( 0 )
    elif ( data['body'][i].lower().__contains__('monkey pox') |
           data['thread_title'][i].lower().__contains__('monkey pox') |
         
           data['body'][i].lower().__contains__('monkeypox') |
           data['thread_title'][i].lower().__contains__('monkeypox') |
         
           data['body'][i].lower().__contains__('pox') |
           data['thread_title'][i].lower().__contains__('pox') |
         
           data['body'][i].lower().__contains__('orthopox') |
           data['thread_title'][i].lower().__contains__('orthopox') |
         
           data['body'][i].lower().__contains__('mpx') |
           data['thread_title'][i].lower().__contains__('mpx') |
         
           data['body'][i].lower().__contains__('gaypox') |
           data['thread_title'][i].lower().__contains__('gaypox') |
         
           data['body'][i].lower().__contains__('mpox') |
           data['thread_title'][i].lower().__contains__('mpox') |
         
           data['body'][i].lower().__contains__('jynneos') |
           data['thread_title'][i].lower().__contains__('jynneos') |
         
           data['body'][i].lower().__contains__('acam2000') |
           data['thread_title'][i].lower().__contains__('acam2000') ):
        contains_monkeypox_term.append( 1 )
    else:
        contains_monkeypox_term.append( 0 )

# Add this list to the data dataframe
data['contains_monkeypox_term'] = contains_monkeypox_term

# Isolate the data that contains the monkeypox term into another dataframe
mpx_data = data.loc[ data['contains_monkeypox_term'] == 1 ] 

# Re-index the mpx_data
index_list = list(range(0,len(mpx_data)))
mpx_data['index_num'] = index_list
mpx_data = mpx_data.set_index('index_num')

# Some of the instances that 'contain a monkeypox term' actually do not contain
# a monkeypox term
# One of the terms that is also picked up is 'epoxy', so we want to exclude
# those instances that contain 'epoxy' which is not related to monkeypox

# Create a new list that will contain a classifier that determines whether
# the term 'epoxy' is found in either the comment or the title thread of an
# instance
contains_epoxy_term = []

# Go through each instance and identify whether the term 'epoxy' is found
# If it is found, the integer 1 will indicate that it is found
# If it is not found, the integer 0 will indicate that it is not found
for i in range( len ( mpx_data[ 'body' ] )):
    if ( mpx_data['body'][i].lower().__contains__('epoxy') |
         mpx_data['thread_title'][i].lower().__contains__('epoxy') ):
        contains_epoxy_term.append ( 1 )
    else:
        contains_epoxy_term.append( 0 )

# Add this list to the mpx_data dataframe
mpx_data['contains_epoxy_term'] = contains_epoxy_term

# Isolate the data that does not contain the term 'epoxy'
mpx_data = mpx_data.loc[ mpx_data['contains_epoxy_term'] == 0 ]

# Create a new list that will contain a classifier that determines whether
# a virus term is found in either the comment or the title thread of an
# instance
contains_virus_term = []

# Go through each instance and identify whether a virus term is found
# If it is found, the integer 1 will indicate that it is found
# If it is not found, the integer 0 will indicate that it is not found
for i in range( len ( data[ 'body' ] )):
    if ( pd.isna( data['body'][i] ) ):
        contains_virus_term.append( 0 )
    elif ( data['body'][i].lower().__contains__('virus') |
           data['thread_title'][i].lower().__contains__('virus') |
         
           data['body'][i].lower().__contains__('cdc') |
           data['thread_title'][i].lower().__contains__('cdc') |
         
           data['body'][i].lower().__contains__('vaccine') |
           data['thread_title'][i].lower().__contains__('vaccine') |
         
           data['body'][i].lower().__contains__('vax') |
           data['thread_title'][i].lower().__contains__('vax') |
         
           data['body'][i].lower().__contains__('vaccinated') |
           data['thread_title'][i].lower().__contains__('vaccinated') ):
        contains_virus_term.append( 1 )
    else:
        contains_virus_term.append( 0 )

# Add this list to the data dataframe
data['contains_virus_term'] = contains_virus_term

virus_data = data.loc[ data['contains_virus_term'] == 1 ]

# export condensed data
# change the file names according to the subreddit
# lgbt
# gaymers
# ainbow
# askgaybros
# asktransgender
# MtF
# NonBinary
# ftm
# BisexualTeens
data.to_csv('lgbt_subreddit_condensed_data.csv', index=False)
mpx_data.to_csv('lgbt_subreddit_mpx_data.csv', index=False)
virus_data.to_csv('lgbt_subreddit_virus_data.csv', index = False)