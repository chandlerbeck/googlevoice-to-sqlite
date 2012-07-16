'''
gvoice_sql.py
A sql connection that simplifies creating and filling a database of GVoice objects

Created on Sep 17, 2011

@author: AviLevin
'''

import sqlite3
import csv

class gvoiceconn(sqlite3.Connection):
    def __init__(self, path):
        open(path, 'w').close() #wipes file in same path, since old records cannot be relied upon (name changes, etc.)
        sqlite3.Connection.__init__(self, path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        #self = sqlite3.connect() #connect
        with open('initdb.sql', 'r') as initdb:
            self.executescript(initdb.read()) #create data structures needed, ad defined in external file\
        #dictonoary to keep track of rowcount in each table
        self.rowcount = dict.fromkeys(('Contact', 'Audio', 'TextConversation', 'TextMessage', 'PhoneCall', 'Voicemail'), 0)
        self.unmatched_recordings = [] #recordings not matched to audio file
    
    #Returns the maximum primary key from a table
    #TO DO: handle locally as a dictionary instead        
    def getmaxid(self, tablename):
        self.rowcount[tablename] += 1
        return self.rowcount[tablename]
        
    #imports a Contact object into the database
    def import_Contact(self, contact):
        #sees if contact id for contact already exists
        contactid = self.execute('SELECT ContactID FROM Contact \
            WHERE (Name = ? OR COALESCE(Name,?) is NULL) \
            AND  (PhoneNumber = ? OR COALESCE(PhoneNumber,?) is NULL)', 
            (contact.name, contact.name, contact.phonenumber, contact.phonenumber)).fetchone()
        if contactid != None: #if contact exists, that's all we need
            return contactid[0]
        else: #Contact ID will be new row we create
            contactid = self.getmaxid('Contact') 
            self.execute('INSERT INTO Contact (ContactID, Name, PhoneNumber) VALUES (?, ?, ?)', (contactid, contact.name, contact.phonenumber))
            return contactid
    
    #Import text messages in a TextConversation into the database
    def import_TextConversation(self, text_conversation):
        contactid = self.import_Contact(text_conversation.contact) #get contact of conversation
        conversationid = self.getmaxid('TextConversation') #get ID of conversation... and insert it
        self.execute('INSERT INTO TextConversation (TextConversationID, ContactID) VALUES (?, ?)', (conversationid, contactid))
        for textmsg in text_conversation.texts:
            #insert each text Message into the TextMessage database
            self.execute ('INSERT INTO TextMessage (TextMessageID, TextConversationID, TimeRecordedUTC, Incoming, Text) VALUES (?, ?, ?, ?, ?)', (
                          self.getmaxid('TextMessage'),
                          conversationid,
                          textmsg.date,
                          0 if textmsg.contact.name == None else 1, #if None, means self
                          textmsg.text
                          ))
     
    #Import a Call object into the database
    def import_Call(self, callrecord):
        try:
            contactid = self.import_Contact(callrecord.contact)
            self.execute('INSERT INTO PhoneCall (PhoneCallID, ContactID, PhoneCallTypeID, TimeStartedUTC, Duration) VALUES (?, ?, ?, ?, ?)', (
                            self.getmaxid('PhoneCall'),
                            contactid,
                                #Proper type as defined in PhoneCallTypeID
                            self.execute('SELECT PhoneCallTypeID FROM PhoneCallType WHERE PhoneCallType = "%s"' % callrecord.calltype).fetchone()[0],
                            callrecord.date,
                            callrecord.duration
                        ))
        except:
            if callrecord.contact.name == 'Google Voice': #Intro go Google Voice - voicemail with no audio
                pass
            else:
                raise
    
    #imports Audio object into database
    def import_Audio(self, audiorecord, insert_unmatched_audio = True):
        contactid = self.import_Contact(audiorecord.contact)
        #only one of these foreign keys are ever used, but both are inserted. So init to null now
        voicemailid = None
        callid = None
        if(audiorecord.audiotype == 'Voicemail'): #if voicemail, update Voicemailt table and grab resulting ID
            voicemailid = self.getmaxid('Voicemail')
            self.execute('INSERT INTO Voicemail (VoicemailID, ContactID) VALUES (?, ?)', (voicemailid, contactid))
        else: #Guess what Call the recording is associated with. If exists, insert
            callidrow = self.execute(
                'select PhoneCallID from PhoneCall WHERE ContactID = ? and strftime("%s", ?) - strftime("%s", TimeStartedUTC) between 0 and Duration', 
                (contactid, audiorecord.date)                
                )
            if callidrow == None:
                self.unmatched_recordings += audiorecord
                if not insert_unmatched_audio:
                    return 1
            else:
                callid = callidrow.fetchone()[0]
        #Now that have foreign keys, insert audio into db
        self.execute(
            'INSERT INTO Audio (AudioID, PhoneCallID, VoicemailID, TimeStartedUTC, Duration, Text, Confidence, FileName) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (
             self.getmaxid('Audio'),
             callid,
             voicemailid,
             audiorecord.date,
             audiorecord.duration,
             audiorecord.text,
             audiorecord.confidence,
             audiorecord.filename
            ))
        return 0
            
    #Outgoing-only text conversations only display the name, but not the number. This tries to locate the right number
    #For a name from different correspondence
    #TO DO: Work on my-text basis instead of by-contact basis for better precision
    def fixnullrecords(self):
        #Get a list of null-phone-number contacts and the contacts with real phone numbers they match
        execstring = '''SELECT NullContacts.ContactID, CompleteContacts.ContactID FROM (
        SELECT DISTINCT Contact.ContactId, Name, PhoneNumber
        FROM Contact INNER JOIN %s ON Contact.ContactId = %s.ContactId WHERE PhoneNumber IS NOT NULL) AS CompleteContacts 
        INNER JOIN ( SELECT ContactId, Name FROM Contact WHERE PhoneNumber IS NULL ) AS NullContacts 
        ON NullContacts.Name = CompleteContacts.Name'''
        #Update text conversation with good contact, then throw away dud number
        for table in ('TextConversation', 'PhoneCall'): #First match to texts, then if no incoming texts, try calls            
            for row in self.execute(execstring % (table, table)):
                self.executescript(
                    'UPDATE TextConversation SET ContactId = %d WHERE ContactId = %d; DELETE FROM Contact WHERE ContactId = %d;' \
                    % (row[1], row[0], row[0])
                )
                
    def exportcsv(self):
        views = [('contacts.csv', 'Contact')]
        views += ((str.lower(name) + 's.csv', 'flat' + name) for name in ('PhoneCall', 'TextMessage', 'Voicemail', 'Recording'))
        for view in views:
            query = self.execute('SELECT * FROM %s' % view[1])
            with open('.\\output\\' + view[0], 'wb') as csvfile:  
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow([i[0] for i in query.description])
                csvwriter.writerows(query.fetchall())