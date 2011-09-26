'''
googlevoice_to_sqlite.py
This file houses the main execution routine

Created on Sep 9, 2011

@author: Arithmomaniac 

'''
import time
from os.path import join
import os.path
import re
import atexit
import gvoice_parse
from xml.etree.ElementTree import fromstring
from gvoice_sql import gvoiceconn

# a generator that returns the gvoice_parse object found in a file
def getobjs(path):
    files = os.listdir(path)
    for fl in files:
        if fl.endswith('.html'): #no mp3 files
            print fl
            with open(join(path, fl), 'r') as f: #read the file
                tree = fromstring(f.read().replace('<br>', "\r\n<br />")) #read properly-formatted html
            record = None #reset the variable
            record = gvoice_parse.process_file(tree, fl) #do the loading
            if record != None:
                yield record

if __name__ == '__main1__':
    start = time.clock()
    conversationlocation = "C:\Users\AviLevin\Downloads\Conversations"
    for i in getobjs(conversationlocation): #load each file into db, depending on type
        pass
    end = time.clock()
    print end - start
    input()

#main execution routine
if __name__ == '__main__':
    #grab location. Allow quoted paths. Default to "brother" conversation directory
    conversationlocation = re.search("[^\"']+", raw_input('Specify the conversations file location: ')).group(0)
    if not conversationlocation:
        conversationlocation = '..\conversations'
    if not os.path.exists('.\output'):
        os.mkdir('.\output')
    gvconn = gvoiceconn('.\output\gvoice.sqlite') #connect to sql database
    atexit.register(gvconn.commit)  #save it exited early by user
    unmatched_audio = []
    try:
        for i in getobjs(conversationlocation): #load each file into db, depending on type
            pass
            if isinstance(i, gvoice_parse.TextConversation): #set of text messages
                gvconn.import_TextConversation(i)
            elif isinstance(i, gvoice_parse.Call): #call
                gvconn.import_Call(i)
            elif isinstance(i, gvoice_parse.Audio): #voicemail/recording
                if gvconn.import_Audio(i, False) == 1: #no contact for audio. Can happen if files have been renamed
                    unmatched_audio += i #save second pass for later
        for i in unmatched_audio: #not make second pass on unmatched audio
            gvconn.import_Audio(i)
            i = None
        gvconn.fixnullrecords() #fixed bad contacts - see there for description
        gvconn.commit()
    except:
        gvconn.commit()
        raise    
    if raw_input('Done creating database.\r\nType anything to export to CSV: ') :
        gvconn.exportcsv()
        raw_input('CSVs created. Press ENTER to exit: ')