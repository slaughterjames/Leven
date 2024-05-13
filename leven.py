#! /usr/bin/env python3
'''
Leven v0.1 - Copyright 2024 James Slaughter,
This file is part of Leven v0.1.

Leven v0.1 is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Leven v0.1 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Leven v0.1.  If not, see <http://www.gnu.org/licenses/>.
'''

#python import
import sys
import datetime
import argparse
from Levenshtein import distance as lev
from fastDamerauLevenshtein import damerauLevenshtein
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from collections import defaultdict
from datetime import date
from array import *
from termcolor import colored

#programmer generated imports
from controller import controller


'''
Usage()
Function: Display the usage parameters when called
'''
def Usage():
    print ('Usage: [required] --domains --top100 [optional] --debug --help')
    print ('Example: ./leven.py --domains --top100 --debug')
    print ('Required Arguments:')
    print ('--domains')
    print (' --top100')
    print ('Optional Arguments:')
    print ('--output - Choose where you wish the output to be directed')
    print ('--function - The algorithm to find typosquating.')
    print ('--debug - Prints verbose logging to the screen to troubleshoot issues with a recon installation.')
    print ('--help - You\'re looking at it!')
    sys.exit(-1)
            
'''
Parse() - Parses program arguments
'''
def Parse(args):        
    parser = argparse.ArgumentParser(description='Process some program arguments.')
    
    parser.add_argument('--domains', help='The target to process')
    parser.add_argument('--top100', help='The target folder to process')
    parser.add_argument('--function', help='The algorithm to find typosquating. \'lev\' for Levenshtein. \'dl\' for DamerauLevenshtein (default). \'fuzz\' for FuzzyWuzzy')
    parser.add_argument('--output', help='The output location')    
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--usage', action='store_true', help='Display program usage.')

    args = parser.parse_args()

    print ('[*] Arguments: ')
 
                
    if args.usage:
        return -1                                   

    if args.domains:        
        CON.domains = args.domains
        print ('domains: ', CON.domains)

    if args.top100:
        CON.top100 = args.top100
        CON.singletarget = False
        print ('top100: ', CON.top100) 

    if args.function:
        CON.function = args.function        
        print ('function: ', CON.function)

    if args.output:
        #This is an optional param and needs to be checked at read time
        CON.output = args.output
        print ('output: ', CON.output)
        if (len(CON.output) < 3):
            if not (CON.output == '<>'):
                print (colored('[x] output must be a viable location.', 'red', attrs=['bold']))
                print ('')
                return -1               

    if args.debug:
        CON.debug = True
        print('debug: ', CON.debug)

    if ((len(CON.domains) < 5)):
        print (colored('[x] domains must be a valid file.', 'red', attrs=['bold']))
        print ('')
        return -1

    if ((len(CON.top100) < 5)):
        print (colored('[x] top100 must be a valid file.', 'red', attrs=['bold']))
        print ('')
        return -1
    
    if (not CON.output):
        CON.output = 'leven_' + str(date.today()) + '.txt'

    if (CON.function == ''):
        CON.dameraulevenshtein = True
        print('dameraulevenshtein: ', str(CON.dameraulevenshtein))
    elif (CON.function == 'lev'):
        CON.levenshtein = True
        print('levenshtein: ', str(CON.levenshtein))
    elif (CON.function == 'fuzz'):
        CON.fuzzywuzzy = True
        print('fuzzywuzzy: ', str(CON.fuzzywuzzy))
    else:
        print (colored('[x] Function not recognized! Use \'lev\' for Levenshtein. \'dl\' for DamerauLevenshtein (default). \'fuzz\' for FuzzyWuzzy', 'red', attrs=['bold']))

    print ('')   
    
    return 0

'''
Levenshtein()
Function: - Does the doing against a string using the Levenshtein distance algorithm
'''
def Levenshtein():
        
    distance = 0

    for top100 in CON.top100list:
        for domain in CON.domainslist:
            if (top100.rstrip()):
                if (CON.debug == True):                    
                    print (colored('[DEBUG] Adding domain ' + domain.strip() + ' to the Word Match list...(' + top100.strip() + ')', 'green', attrs=['bold']))                                
                CON.match.append(domain + ' (' + top100.strip() + ')')
            else:                
                distance = lev(top100, domain)
                if (len(domain) == 0):
                    continue
                elif (distance <= 5):
                    if (CON.debug == True):
                        print ('[DEBUG] ' + domain + ': distance ' + str(distance) + ' (' + top100.strip() + ')')
                        print (colored('[DEBUG] Adding domain ' + domain.strip() + ' to the Confident list...(' + top100.strip() + ')', 'green', attrs=['bold']))
                    CON.confident.append(domain + ' (' + top100.strip() + ')')
                elif ((distance > 5) and (distance <= 7)):
                    if (CON.debug == True):
                        print ('[DEBUG] ' + domain + ': distance ' + str(distance) + ' (' + top100.strip() + ')')
                        print (colored('[DEBUG] Adding domain ' + domain.strip() + ' to the Possible list...(' + top100.strip() + ')', 'green', attrs=['bold']))                     
                    CON.possible.append(domain + ' (' + top100.strip() + ')')
                else:
                  if (CON.debug == True):
                      print (colored('[DEBUG] Domain: ' + domain.strip() + ' is outside the distance boundary.', 'yellow', attrs=['bold'])) 
                  continue                 

    with open(CON.output,'a') as file:                                    
        print (colored('\n\r[*] Word Match Typosquating List', 'green', attrs=['bold']))
        file.write('[*] Word Match Typosquating List\n')
        if (len(CON.match) > 0):
            for domain in CON.match:
                print ('[-] ' + domain.strip())
                file.write(domain.strip() + '\n')
        else:
            print ('[-] No domains in this run...')
            file.write('[-] No domains in this run...')

        print (colored('\n\r[*] Confident Typosquating List', 'green', attrs=['bold']))
        file.write('\n\r[*] Confident Typosquating List\n')
        if (len(CON.confident) > 0):
            for domain in CON.confident:
                print ('[-] ' + domain.strip())
                file.write(domain.strip() + '\n')
        else:
            print ('[-] No domains in this run...')
            file.write('[-] No domains in this run...')

        print (colored('\n\r[*] Possible Typosquating List', 'green', attrs=['bold']))
        file.write('\n\r[*] Possible Typosquating List\n')
        if (len(CON.possible) > 0):
            for domain in CON.possible:
                print ('[-] ' + domain.strip())
                file.write(domain.strip() + '\n')
        else:
            print ('[-] No domains in this run...')
            file.write('[-] No domains in this run...')

    file.close()
                 
    return 0

'''
DamerauLevenshtein()
Function: - Does the doing against a string using the Damerau-Levenshtein algorithm  
'''
def DamerauLevenshtein():
    distance = 0
    count = 0

    for top100 in CON.top100list:
        for domain in CON.domainslist:        
            if (top100.rstrip() in domain):
                if (CON.debug == True):                    
                    print (colored('[DEBUG] Adding domain ' + domain.strip() + ' to the Word Match list...(' + top100.strip() + ')', 'green', attrs=['bold']))                
                CON.match.append(domain + ' (' + top100.strip() + ')')
            else:                
                distance = damerauLevenshtein(top100, domain)
                if (len(domain) == 0):
                    continue
                elif (distance > 0.5):
                    if (CON.debug == True):
                        print ('[DEBUG] ' + domain + ': distance ' + str(distance) + ' (' + top100.strip() + ')')
                        print (colored('[DEBUG] Adding domain ' + domain.strip() + ' to the Confident list...(' + top100.strip() + ')', 'green', attrs=['bold']))                                       
                    CON.confident.append(domain + ' (' + top100.strip() + ')')
                elif ((distance > 0.45) and (distance <= 0.5)):
                    if (CON.debug == True):
                        print ('[DEBUG] ' + domain + ': distance ' + str(distance) + ' (' + top100.strip() + ')')
                        print (colored('[DEBUG] Adding domain ' + domain.strip() + ' to the Possible list...(' + top100.strip() + ')', 'green', attrs=['bold']))                    
                    CON.possible.append(domain + ' (' + top100.strip() + ')')                    
                else:
                  if (CON.debug == True):
                      print (colored('[DEBUG] Domain: ' + domain.strip() + ' is outside the distance boundary.', 'yellow', attrs=['bold'])) 
                  continue

    with open(CON.output,'a') as file:                                    
        print (colored('\n\r[*] Word Match Typosquating List', 'green', attrs=['bold']))
        file.write('[*] Word Match Typosquating List\n')
        if (len(CON.match) > 0):
            for domain in CON.match:
                print ('[-] ' + domain.strip())
                file.write(domain.strip() + '\n')
        else:
            print ('[-] No domains in this run...')
            file.write('[-] No domains in this run...')

        print (colored('\n\r[*] Confident Typosquating List', 'green', attrs=['bold']))
        file.write('\n\r[*] Confident Typosquating List\n')
        if (len(CON.confident) > 0):
            for domain in CON.confident:
                print ('[-] ' + domain.strip())
                file.write(domain.strip() + '\n')
        else:
            print ('[-] No domains in this run...')
            file.write('[-] No domains in this run...')

        print (colored('\n\r[*] Possible Typosquating List', 'green', attrs=['bold']))
        file.write('\n\r[*] Possible Typosquating List\n')
        if (len(CON.possible) > 0):
            for domain in CON.possible:
                print ('[-] ' + domain.strip())
                file.write(domain.strip() + '\n')
        else:
            print ('[-] No domains in this run...')
            file.write('[-] No domains in this run...')

    file.close() 

    return 0

'''
FuzzyWuzzy()
Function: - Does the doing against a string using the fuzzywuzzy library  
'''
def FuzzyWuzzy():

    distance = 0

    for top100 in CON.top100list:
        for domain in CON.domainslist:        
            if (top100.rstrip() in domain):
                if (CON.debug == True):                    
                    print (colored('[DEBUG] Adding domain ' + domain.strip() + ' to the Word Match list...(' + top100.strip() + ')', 'green', attrs=['bold']))                
                CON.match.append(domain + ' (' + top100.strip() + ')')
            else:
                distance = fuzz.ratio(top100, domain)
                if (CON.debug == True):
                    print (colored('[DEBUG] distance:' + str(distance), 'green', attrs=['bold']))
                if (len(domain) == 0):
                    continue
                elif (distance > 65):
                    if (CON.debug == True):
                        print ('[DEBUG] ' + domain + ': distance ' + str(distance) + ' (' + top100.strip() + ')')
                        print (colored('[DEBUG] Adding domain ' + domain.strip() + ' to the Confident list...(' + top100.strip() + ')', 'green', attrs=['bold']))                                       
                    CON.confident.append(domain + ' (' + top100.strip() + ')')
                elif ((distance > 55) and (distance <= 65)):
                    if (CON.debug == True):
                        print ('[DEBUG] ' + domain + ': distance ' + str(distance) + ' (' + top100.strip() + ')')
                        print (colored('[DEBUG] Adding domain ' + domain.strip() + ' to the Possible list...(' + top100.strip() + ')', 'green', attrs=['bold']))                    
                    CON.possible.append(domain + ' (' + top100.strip() + ')')                    
                else:
                  if (CON.debug == True):
                      print (colored('[DEBUG] Domain: ' + domain.strip() + ' is outside the distance boundary.', 'yellow', attrs=['bold'])) 
                  continue

    with open(CON.output,'a') as file:                                    
        print (colored('\n\r[*] Word Match Typosquating List', 'green', attrs=['bold']))
        file.write('[*] Word Match Typosquating List\n')
        if (len(CON.match) > 0):
            for domain in CON.match:
                print ('[-] ' + domain.strip())
                file.write(domain.strip() + '\n')
        else:
            print ('[-] No domains in this run...')
            file.write('[-] No domains in this run...')

        print (colored('\n\r[*] Confident Typosquating List', 'green', attrs=['bold']))
        file.write('\n\r[*] Confident Typosquating List\n')
        if (len(CON.confident) > 0):
            for domain in CON.confident:
                print ('[-] ' + domain.strip())
                file.write(domain.strip() + '\n')
        else:
            print ('[-] No domains in this run...')
            file.write('[-] No domains in this run...')

        print (colored('\n\r[*] Possible Typosquating List', 'green', attrs=['bold']))
        file.write('\n\r[*] Possible Typosquating List\n')
        if (len(CON.possible) > 0):
            for domain in CON.possible:
                print ('[-] ' + domain.strip())
                file.write(domain.strip() + '\n')
        else:
            print ('[-] No domains in this run...')
            file.write('[-] No domains in this run...')

    file.close() 


    return 0    

'''
Terminate()
Function: - Attempts to exit the program cleanly when called  
'''
     
def Terminate(exitcode):
    sys.exit(exitcode)

'''
This is the mainline section of the program and makes calls to the 
various other sections of the code
'''

if __name__ == '__main__':
    
    ret = 0

    #Stores our args
    CON = controller()            

    #Parses our args
    ret = Parse(sys.argv)

    #Something bad happened
    if (ret == -1):
        Usage()
        Terminate(ret)

    #Open the top100 file
    try:
        with open(CON.top100, "r+") as read_file:
            CON.top100list = read_file.readlines()                        
    except Exception as e:
        print (colored('[x] Unable to open top100 file: ' + str(e), 'red', attrs=['bold']))
        Terminate(-1)        


    #Open the domains file
    line = ''
    try:
        with open(CON.domains, 'r', encoding='UTF-8') as read_file:
            while line := read_file.readline():
                line.rstrip()                
                CON.domainslist.append(line.rstrip())
    except Exception as e:
        print (colored('[x] Unable to open domains file: ' + str(e), 'red', attrs=['bold']))
        Terminate(-1)     

    #Do the doing
    if (CON.levenshtein == True):
        print (colored('[*] Using the Levenshtein distance to determine matches...', 'green', attrs=['bold']))
        Levenshtein()

    if (CON.dameraulevenshtein == True):
        print (colored('[*] Using the Damerau-Levenshtein distance to determine matches...', 'green', attrs=['bold']))
        DamerauLevenshtein()
    
    if (CON.fuzzywuzzy == True):
        print (colored('[*] Using FuzzyWuzzy to determine matches...', 'green', attrs=['bold']))
        FuzzyWuzzy()

    print ('')
    print ('[*] Program Complete')

    Terminate(0)
'''
END OF LINE
'''