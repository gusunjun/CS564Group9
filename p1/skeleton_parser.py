
"""
FILE: skeleton_parser.py
------------------
Author: Firas Abuzaid (fabuzaid@stanford.edu)
Author: Perth Charernwattanagul (puch@stanford.edu)
Modified: 04/21/2014

Skeleton parser for CS564 programming project 1. Has useful imports and
functions for parsing, including:

1) Directory handling -- the parser takes a list of eBay json files
and opens each file inside of a loop. You just need to fill in the rest.
2) Dollar value conversions -- the json files store dollar value amounts in
a string like $3,453.23 -- we provide a function to convert it to a string
like XXXXX.xx.
3) Date/time conversions -- the json files store dates/ times in the form
Mon-DD-YY HH:MM:SS -- we wrote a function (transformDttm) that converts to the
for YYYY-MM-DD HH:MM:SS, which will sort chronologically in SQL.

Your job is to implement the parseJson function, which is invoked on each file by
the main function. We create the initial Python dictionary object of items for
you; the rest is up to you!
Happy parsing!
"""

import sys
from json import loads
from re import sub

columnSeparator = "|"

# Dictionary of months used for date transformation
MONTHS = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06',\
        'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}

user = {}
user_table  = []
item_table = []
bid = []
category = []
"""
Returns true if a file ends in .json
"""
def isJson(f):
    return len(f) > 5 and f[-5:] == '.json'

"""
Converts month to a number, e.g. 'Dec' to '12'
"""
def transformMonth(mon):
    if mon in MONTHS:
        return MONTHS[mon]
    else:
        return mon

"""
Transforms a timestamp from Mon-DD-YY HH:MM:SS to YYYY-MM-DD HH:MM:SS
"""
def transformDttm(dttm):
    dttm = dttm.strip().split(' ')
    dt = dttm[0].split('-')
    date = '20' + dt[2] + '-'
    date += transformMonth(dt[0]) + '-' + dt[1]
    return date + ' ' + dttm[1]

"""
Transform a dollar value amount from a string like $3,453.23 to XXXXX.xx
"""

def transformDollar(money):
    if money == None or len(money) == 0:
        return money
    return sub(r'[^\d.]', '', money)

"""
Parses a single json file. Currently, there's a loop that iterates over each
item in the data set. Your job is to extend this functionality to create all
of the necessary SQL tables for your database.
"""
def parseJson(json_file):
    with open(json_file, 'r') as f:
        items = loads(f.read())['Items'] # creates a Python dictionary of Items for the supplied json file
        for item in items:
            """
            TODO: traverse the items dictionary to extract information from the
            given `json_file' and generate the necessary .dat files to generate
            the SQL tables based on your relation design
            """
            item_info(item)
            user_info(item)
            bid_info(item)
            item_category(item)
            pass

    

def item_info(item):
    
    item_ID = item['ItemID']
    s = item['Name'] + '|'
    s += transformDollar(item['Currently']) + '|'
    if 'Buy_Price' in item:
        s += transformDollar(item['Buy_Price']) + '|'
    else:
        s += 'NULL' + '|'
    s += transformDollar(item['First_Bid']) + '|'
    s += item['Number_of_Bids'] + '|'
    location = item['Location'] + '|'
    country = item['Country'] + '|'
    s += transformDttm(item['Started']) + '|'
    s += transformDttm(item['Ends']) + '|'
    if item['Description'] is not None:
        s += item['Description'] + '|'
    else:
        s += 'NULL' + '|'
    s += item["Seller"]["UserID"]
    
    item_table.append(item_ID + '|' + s)
    
    
    

def user_info(item):
    
    if item['Bids'] is not None:
        for b in item['Bids']:
            user_ID = b['Bid']['Bidder']['UserID']
            rating = b['Bid']['Bidder']['Rating']
            if 'Location' not in b['Bid']['Bidder']:
                location = 'NULL'
            else:
                location = b['Bid']['Bidder']['Location']
                
            if 'Country' not in b['Bid']['Bidder']:
                country = 'NULL'
            else:
                country = b['Bid']['Bidder']['Country']
            user[user_ID] = rating + '|' + location + '|' + country
            user_table.append(user_ID + '|' + user[user_ID])

   
    user_ID = item['Seller']['UserID']
    rating = item['Seller']['Rating']
    if user_ID not in user:
        user[user_ID] = rating + '|' + 'NULL' + '|' + 'NULL'
        user_table.append(user_ID + '|' + user[user_ID])

def bid_info(item):
    
    if item['Bids'] is not None:
        for b in item['Bids']:
            item_ID = item['ItemID']
            user_ID = b['Bid']['Bidder']['UserID']
            time = transformDttm(b['Bid']['Time'])
            amount = transformDollar(b['Bid']['Amount'])
            bid.append(item_ID + '|' + user_ID + '|' + time + '|' + amount)


def item_category(item):
    if item['Category'] is not None:
        for i in item['Category']:
            category.append(item['ItemID'] + '|' + i)            
        
        
        
def write():
    with open('item.dat', 'w') as file:  
        file.write('\n'.join(item_table))

    with open('user.dat', 'w') as file:  
        file.write('\n'.join(user_table))

    with open('bid.dat', 'w') as file:  
        file.write('\n'.join(bid))

    with open('category.dat', 'w') as file:  
        file.write('\n'.join(category))
    
    
"""
Loops through each json files provided on the command line and passes each file
to the parser
"""
def main(argv):
    if len(argv) < 2:
        print >> sys.stderr, 'Usage: python skeleton_json_parser.py <path to json files>'
        sys.exit(1)
    # loops over all .json files in the argument
    for f in argv[1:]:
        if isJson(f):
            
            parseJson(f)
            print ("Success parsing " + f)
    write()

if __name__ == '__main__':
    main(sys.argv)
