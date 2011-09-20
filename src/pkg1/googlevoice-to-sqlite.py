'''
main.py
This file houses the main execution routine

Created on Sep 9, 2011

@author: Arithmomaniac 

'''
import os
import gvoice_parse
import xml.etree.ElementTree
from gvoice_sql import gvoiceconn

# a generator that returns the gvoice_parse object found in a file
def getobjs(path):
    os.chdir(path) #simplify file handling by moving to the relevant directory
    #TO DO: avoid this; actually use full file names
    files = os.listdir(path)
    for fl in files:
        if fl.endswith('.html'): #no mp3 files
            print fl #lets the user see where we are up to
            with open(fl, 'r') as f: #read the file
                tree = xml.etree.ElementTree.fromstring(f.read().replace('<br>', "\r\n<br />")) #read properly-formatted html
            record = None #reset the variable
            record = gvoice_parse.process_file(tree, fl) #do the loading
            if record != None:
                yield record

#main execution routine
if __name__ == '__main__':
    #grab location. Default to "brother" conversation directory
    conversationlocation = raw_input('Specify the conversations file location: ')
    if conversationlocation == None or len(conversationlocation) == 0:
        conversationlocation = '..\conversations'
    gvconn = gvoiceconn('.\gvoice.sqlite') #connect to sql database
    for i in getobjs(conversationlocation): #load each file into db, depending on type
        if isinstance(i, gvoice_parse.TextConversation): #set of text messages
            gvconn.import_TextConversation(i)
        elif isinstance(i, gvoice_parse.Call): #call
            gvconn.import_Call(i)
        elif isinstance(i, gvoice_parse.Audio): #voicemail/recording
            gvconn.import_Audio(i)
        gvconn.conn.commit()
    gvconn.fixnullrecords() #fixed bad contacts - see there for description
    raw_input('All done. Press ENTER to quit')