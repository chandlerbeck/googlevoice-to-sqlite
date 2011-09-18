'''
Created on Sep 9, 2011

@author: Arithmomaniac 

'''
import os
import gvoice_parse
import xml.etree.ElementTree
from gvoice_sql import gvoice_sql


def getobjs(path):
    os.chdir(path)
    files = os.listdir('.')
    for fl in files:
        if fl.endswith('.html'):# and fl > 'Y':
            with open(fl, 'r') as f:
                print fl
                tree = xml.etree.ElementTree.fromstring(f.read().replace('<br>', "\r\n<br />"))
                # do indirectly so can handle brs
                record = None
                record = gvoice_parse.process_file(tree, fl)
                if record != None:
                    yield record

def dumpall(generator):
    for i in generator:
        print i.dump()
        raw_input()



if __name__ == '__main__':
    conn = gvoice_sql.wipeconnect('C:\Users\AviLevin\Downloads\gvoice.sqlite')
    with open('initdb.sql', 'r') as initdb:
        conn.executescript(initdb.read())
    for i in getobjs('C:\Users\AviLevin\Downloads\conversations'):
        #print i.dump();
        contactid = gvoice_sql.importcontact(conn, i.contact)
        if isinstance(i, gvoice_parse.TextConversation):
            gvoice_sql.importtext(conn, i, contactid)
        elif isinstance(i, gvoice_parse.Call):
            gvoice_sql.importcall(conn, i, contactid)
        elif isinstance(i, gvoice_parse.Audio):
            gvoice_sql.importaudio(conn, i, contactid)
        conn.commit()
        print '-------------'
    gvoice_sql.fixnullrecords(conn)