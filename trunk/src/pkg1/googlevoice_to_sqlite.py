'''
googlevoice_to_sqlite.py
This file houses the main execution routine

Created on Sep 9, 2011

@author: Arithmomaniac 

'''
import time
import sys
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
            with open(join(path, fl), 'r') as f: #read the file
                tree = fromstring(f.read().replace('<br>', "\r\n<br />")) #read properly-formatted html
            record = None #reset the variable
            record = gvoice_parse.process_file(tree, fl) #do the loading
            if record != None:
                yield (fl, record) #return record and name


#a line-overwriting suite.
class LineWriter(object):
    def __init__(self, outfile=sys.stdout, flush=True):
        self.flush = flush
        self.lastlen = None #the length of the last line
        self.outfile = outfile
        
    def __del__(self):
        self.newline() #make sure that on new line when done

    def write(self, command): #overwrite contents on current line
        currlen = len(command)
        if currlen < self.lastlen: #if we're not going to completely overwrite the last line
            self.wipe() #wipe it
        self.outfile.write('\r%s' % command) #go back to beginning of line and write
        self.lastlen = currlen #then save new value of lastlen
        if self.flush:
            self.outfile.flush()    

    def wipe(self):
        self.write(''.rjust(self.lastlen)) #overwrite with blank values
        self.lastlen = None #no content on line anymore
        
    def newline(self):
        self.lastlen = None #new line, so no need to care about overwriting
        self.write('\r\n') #write the line

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
    listline = LineWriter()
    try:
        for i in getobjs(conversationlocation): #load each file into db, depending on type
            listline.write(i[0]) #write filename to console
            record = i[1]
            if isinstance(record, gvoice_parse.TextConversation): #set of text messages
                gvconn.import_TextConversation(record)
            elif isinstance(record, gvoice_parse.Call): #call
                gvconn.import_Call(record)
            elif isinstance(record, gvoice_parse.Audio): #voicemail/recording
                if gvconn.import_Audio(record, False) == 1: #no contact for audio. Can happen if files have been renamed
                    unmatched_audio += record #save second pass for later
        del listline
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
        print 'CSVs created.'
    raw_input('Press ENTER to exit: ')