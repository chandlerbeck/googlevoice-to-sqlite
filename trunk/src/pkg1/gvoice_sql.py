'''
Created on Sep 17, 2011

@author: AviLevin
'''

import sqlite3

class gvoice_sql:
    def importcontact(self, conn, contact):
        contactid = conn.execute('SELECT ContactID FROM Contact \
            WHERE (Name = ? OR COALESCE(Name,?) is NULL) \
            AND  (PhoneNumber = ? OR COALESCE(PhoneNumber,?) is NULL)', 
            (contact.name, contact.name, contact.phonenumber, contact.phonenumber)).fetchone()
        if contactid != None:
            return contactid[0]
        else:
            contactid = self.getmaxid(conn, 'Contact')
            conn.execute('INSERT INTO Contact (ContactID, Name, PhoneNumber) VALUES (?, ?, ?)', (contactid, contact.name, contact.phonenumber))
            return contactid
    
    def getmaxid(self, conn, tablename):
        maxid = conn.execute('SELECT MAX(%sID) + 1 FROM %s' % (tablename, tablename)).fetchone()[0]
        return 1 if maxid == None else maxid
    
    def wipeconnect(self, path):
        open(path, 'w').close() #wipes file in same path
        return sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    
    def importtext(self, conn, text_conversation, contactid):
        conversationid = self.getmaxid(conn, 'TextConversation')
        conn.execute('INSERT INTO TextConversation (TextConversationID, ContactID) VALUES (?, ?)', (conversationid, contactid))
        for textmsg in text_conversation.texts:
            conn.execute ('INSERT INTO TextMessage (TextMessageID, TextConversationID, TimeRecorded, Incoming, Text) VALUES (?, ?, ?, ?, ?)', (
                          self.getmaxid(conn, 'TextMessage'),
                          conversationid,
                          textmsg.date,
                          0 if textmsg.contact.name == None else 1,
                          textmsg.text
                          ))
     
    def importcall(self, conn, callrecord, contactid):
        #print callrecord.calltype
        conn.execute('INSERT INTO PhoneCall (PhoneCallID, ContactID, PhoneCallTypeID, TimeStarted, Duration) VALUES (?, ?, ?, ?, ?)', (
                          self.getmaxid(conn, 'PhoneCall'),
                          contactid,
                          conn.execute('SELECT PhoneCallTypeID FROM PhoneCallType WHERE PhoneCallType = "%s"' % callrecord.calltype).fetchone()[0],
                          callrecord.date,
                          callrecord.duration
                    ))
        
    def importaudio(self, conn, audiorecord, contactid):
        print audiorecord.date
        voicemailid = None
        callid = None
        if(audiorecord.audiotype == 'Voicemail'):
            voicemailid = self.getmaxid(conn, 'Voicemail')
            conn.execute('INSERT INTO Voicemail (VoicemailID, ContactID) VALUES (?, ?)', (voicemailid, contactid))
        else:
            callidrow = conn.execute(
                'select PhoneCallID from PhoneCall WHERE ContactID = ? and strftime("%s", ?) - strftime("%s", TimeStarted) between 0 and Duration', 
                (contactid, audiorecord.date)                
                )
            if callidrow != None:
                callid = callidrow.fetchone()[0]
        conn.execute(
            'INSERT INTO Audio (AudioID, PhoneCallID, VoicemailID, TimeStarted, Duration, Text, Confidence, FileName) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (
             self.getmaxid(conn, 'Audio'),
             callid,
             voicemailid,
             audiorecord.date,
             audiorecord.duration,
             audiorecord.text,
             audiorecord.confidence,
             audiorecord.filename
            ))
            
    
    def fixnullrecords(self, conn):
        execstring = '''SELECT NullContacts.ContactID, CompleteContacts.ContactID FROM (
        SELECT DISTINCT Contact.ContactId, Name, PhoneNumber 
        FROM Contact INNER JOIN %s ON Contact.ContactId = %s.ContactId WHERE PhoneNumber IS NOT NULL
        ) AS CompleteContacts INNER JOIN ( SELECT ContactId, Name FROM Contact WHERE PhoneNumber IS NULL
        ) AS NullContacts ON NullContacts.Name = CompleteContacts.Name'''
        for table in ('TextConversation', 'PhoneCall'):            
            for row in conn.execute(execstring % (table, table)):
                conn.executescript(
                    'UPDATE TextConversation SET ContactId = %d WHERE ContactId = %d; DELETE FROM Contact WHERE ContactId = %d;' \
                    % (row[0], row[1], row[0])
                )
        conn.commit()