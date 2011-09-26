-- Table: Contact
CREATE TABLE Contact ( 
    ContactID   INTEGER PRIMARY KEY ASC,
    Name        TEXT,
    PhoneNumber TEXT 
);


-- Table: TextConversation
CREATE TABLE TextConversation ( 
    TextConversationID INTEGER PRIMARY KEY ASC,
    ContactID          INTEGER REFERENCES Contact ( ContactID ) 
);


-- Table: TextMessage
CREATE TABLE TextMessage ( 
    TextMessageID INTEGER PRIMARY KEY ASC,
	TextConversationID INTEGER NOT NULL REFERENCES TextConversation (TextConversationID),
	TimeRecorded  timestamp,
    Incoming      INTEGER NOT NULL,
    Text          TEXT    NOT NULL 
);


-- Table: PhoneCallType
CREATE TABLE PhoneCallType ( 
    PhoneCallTypeID INTEGER PRIMARY KEY,
    PhoneCallType   TEXT NOT NULL UNIQUE 
);
INSERT INTO [PhoneCallType] ([PhoneCallTypeID], [PhoneCallType]) VALUES (1, 'Placed');
INSERT INTO [PhoneCallType] ([PhoneCallTypeID], [PhoneCallType]) VALUES (2, 'Received');
INSERT INTO [PhoneCallType] ([PhoneCallTypeID], [PhoneCallType]) VALUES (3, 'Missed');

-- Table: PhoneCall
CREATE TABLE PhoneCall ( 
    PhoneCallID     INTEGER PRIMARY KEY ASC,
	ContactID	   INTEGER REFERENCES Contact ( ContactID ),	
	PhoneCallTypeID INTEGER NOT NULL
			   REFERENCES PhoneCallType ( PhoneCallTypeID ) ,
	TimeStarted timestamp NOT NULL,
    Duration   INTEGER
);

-- Table: Voicemail
CREATE TABLE Voicemail ( 
    VoicemailID INTEGER PRIMARY KEY ASC,
    ContactID   INTEGER REFERENCES Contact ( ContactID ) 
);

-- Table: Audio
CREATE TABLE Audio ( 
    AudioID     INTEGER PRIMARY KEY ASC,
    PhoneCallID INTEGER REFERENCES PhoneCall ( PhoneCallID ),
    VoicemailID INTEGER REFERENCES Voicemail ( VoicemailID ),
	TimeStarted timestamp NOT NULL,
    Duration    INTEGER,
    Text        TEXT,
    Confidence  NUMERIC,
	FileName	TEXT
);

-- View: flatTextMessage
CREATE VIEW flatTextMessage AS
       SELECT TM.TextMessageID,
              TM.TextConversationID,
              C.ContactID,
              C.Name,
              C.PhoneNumber,
              TM.Incoming,
              TM.TimeRecorded,
              TM.Text
         FROM Contact AS C
              INNER JOIN TextConversation AS TC
                      ON C.ContactID = TC.ContactID
              INNER JOIN TextMessage AS TM
                      ON TC.TextConversationID = TM.TextConversationID
        ORDER BY TM.TimeRecorded;
;

-- View: flatPhoneCall
CREATE VIEW flatPhoneCall AS
       SELECT PC.PhoneCallID,
              C.ContactID,
              C.Name,
              C.PhoneNumber,
              PCT.PhoneCallType,
              PC.TimeStarted,
              PC.Duration
         FROM Contact AS C
              INNER JOIN PhoneCall AS PC
                      ON C.ContactID = PC.ContactID
              INNER JOIN PhoneCallType AS PCT
                      ON PCT.PhoneCallTypeID = PC.PhoneCallTypeID
        ORDER BY PC.TimeStarted;
;

-- View: flatVoicemail
CREATE VIEW flatVoicemail AS
       SELECT V.VoicemailID,
              C.ContactID,
              C.Name,
              C.PhoneNumber,
              A.TimeStarted,
              A.Duration,
              A.Text,
              A.Confidence,
              A.FileName
         FROM Contact AS C
              INNER JOIN Voicemail AS V
                      ON C.ContactID = V.ContactID
              INNER JOIN Audio AS A
                      ON A.VoicemailID = V.VoicemailID
        ORDER BY A.TimeStarted;
;

-- View: flatRecording
CREATE VIEW flatRecording AS
       SELECT PC.PhoneCallID,
              C.ContactID,
              C.Name,
              C.PhoneNumber,
              A.TimeStarted,
              A.Duration,
              A.FileName
         FROM Contact AS C
              INNER JOIN PhoneCall AS PC
                      ON C.ContactID = PC.ContactID
              INNER JOIN Audio AS A
                      ON A.PhoneCallID = PC.PhoneCallID
        ORDER BY A.TimeStarted;
;