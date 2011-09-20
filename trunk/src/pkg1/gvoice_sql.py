'''
gvoice_sql.py
A sql connection that simplifies creating and filling a database of GVoice objects

Created on Sep 17, 2011

@author: AviLevin
'''

import sqlite3

class gvoiceconn:
    def __init__(self, path):
        open(path, 'w').close() #wipes file in same path, since old records cannot be relied upon (name changes, etc.)
        self.conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES) #connect
        with open('initdb.sql', 'r') as initdb:
            self.conn.executescript(initdb.read()) #create data structures needed, ad defined in external file
    
    #Returns the maximum primary key from a table
    #TO DO: handle locally as a dictionary instead        
    def getmaxid(self, tablename):
        maxid = self.conn.execute('SELECT MAX(%sID) + 1 FROM %s' % (tablename, tablename)).fetchone()[0]
        return 1 if maxid == None else maxid
        
    #imports a Contact object into the database
    def import_Contact(self, contact):
        #sees if contact id for contact already exists
        contactid = self.conn.execute('SELECT ContactID FROM Contact \
            WHERE (Name = ? OR COALESCE(Name,?) is NULL) \
            AND  (PhoneNumber = ? OR COALESCE(PhoneNumber,?) is NULL)', 
            (contact.name, contact.name, contact.phonenumber, contact.phonenumber)).fetchone()
        if contactid != None: #if contact exists, that's all we need
            return contactid[0]
        else: #Contact ID will be new row we create
            contactid = self.getmaxid('Contact') 
            self.conn.execute('INSERT INTO Contact (ContactID, Name, PhoneNumber) VALUES (?, ?, ?)', (contactid, contact.name, contact.phonenumber))
            return contactid
    
    #Import text messages in a TextConversation into the database
    def import_TextConversation(self, text_conversation):
        contactid = self.import_Contact(text_conversation.contact) #get contact of conversation
        conversationid = self.getmaxid('TextConversation') #get ID of conversation... and insert it
        self.conn.execute('INSERT INTO TextConversation (TextConversationID, ContactID) VALUES (?, ?)', (conversationid, contactid))
        for textmsg in text_conversation.texts:
            #insert each text Message into the TextMessage database
            self.conn.execute ('INSERT INTO TextMessage (TextMessageID, TextConversationID, TimeRecorded, Incoming, Text) VALUES (?, ?, ?, ?, ?)', (
                          self.getmaxid('TextMessage'),
                          conversationid,
                          textmsg.date,
                          0 if textmsg.contact.name == None else 1, #if None, means self
                          textmsg.text
                          ))
     
    #Import a Call object into the database
    def import_Call(self, callrecord):
        contactid = self.import_Contact(callrecord.contact)
        self.conn.execute('INSERT INTO PhoneCall (PhoneCallID, ContactID, PhoneCallTypeID, TimeStarted, Duration) VALUES (?, ?, ?, ?, ?)', (
                          self.getmaxid('PhoneCall'),
                          contactid,
                            #Proper type as defined in PhoneCallTypeID
                          self.conn.execute('SELECT PhoneCallTypeID FROM PhoneCallType WHERE PhoneCallType = "%s"' % callrecord.calltype).fetchone()[0],
                          callrecord.date,
                          callrecord.duration
                    ))
    
    #imports Audio object into database
    def import_Audio(self, audiorecord):
        contactid = self.import_Contact(audiorecord.contact)
        #only one of these foreign keys are ever used, but both are inserted. So init to null now
        voicemailid = None
        callid = None
        if(audiorecord.audiotype == 'Voicemail'): #if voicemail, update Voicemailt table and grab resulting ID
            voicemailid = self.getmaxid('Voicemail')
            self.conn.execute('INSERT INTO Voicemail (VoicemailID, ContactID) VALUES (?, ?)', (voicemailid, contactid))
        else: #Guess what Call the recording is associated with. If exists, insert
            callidrow = self.conn.execute(
                'select PhoneCallID from PhoneCall WHERE ContactID = ? and strftime("%s", ?) - strftime("%s", TimeStarted) between 0 and Duration', 
                (contactid, audiorecord.date)                
                )
            if callidrow != None:
                callid = callidrow.fetchone()[0]
        #Now that have foreign keys, insert audio into db
        self.conn.execute(
            'INSERT INTO Audio (AudioID, PhoneCallID, VoicemailID, TimeStarted, Duration, Text, Confidence, FileName) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (
             self.getmaxid('Audio'),
             callid,
             voicemailid,
             audiorecord.date,
             audiorecord.duration,
             audiorecord.text,
             audiorecord.confidence,
             audiorecord.filename
            ))
            
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
            for row in self.conn.execute(execstring % (table, table)):
                self.conn.executescript(
                    'UPDATE TextConversation SET ContactId = %d WHERE ContactId = %d; DELETE FROM Contact WHERE ContactId = %d;' \
                    % (row[0], row[1], row[0])
                )
                self.conn.commit()