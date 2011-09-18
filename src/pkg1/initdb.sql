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
