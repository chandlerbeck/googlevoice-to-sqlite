README
----------------
gvoice-to-sqlite 
1.0 (2011-09-20)
(c) Arithmomaniac (arithmomaniac@hotmail.com) under LGPL2/GPL2.1/MPL1.1 tri-license
-------------
The gvoice-to-sqlite script takes the Google Voice records you can get from Google Takeout one step further - instead of thousands of tiny files, it produces a SQLite database that you can use to make lists (of past texts within a year, for example) and analyses (such as the people you talk to the most).

This script has no dependencies except for Python 2.7 itself. In the future, even this may be removed (for Windows).

-------------

Basic file structure:
- gvoice-to-sqlite.py			the main executable
	- gvoice_parse.py			a parsing library that returns GVoice objects
	- gvoice_sql.py				the Python-to-SQLite inferface
		- initdb.sql			The SQL that creates the database.

-------------

To use this script:
1) 	Download and unzip your Voice data from Google Takeout.
2) 	Start gvoice-to-sqlite.py
3) 	Provide the location of the "conversations" directory
4) 	Wait until the message says "all done". Then you can exit.
5) 	The results are stored in .\gvoice.sqlite. A database diagram exists on the project homepage.
	If you want to save this database, copy it out of the directory. Due to limitations in Google's contact persistence, the entire database is rewritten every time.

If you need a SQLite client, try SQLite Studio (Windows) or SQLite Manager (Firefox). If you would like to import the data into Excel, Oracle, SQL Server, etc on Windows, use this OLDB file.

--------------

Future Features (in order of priority):

Create views inside the output SQL database
Implement exporting to CSV
Decode the special characters (like '&amp;') inside text messages
Keep track of primary key increments inside the script, rather than through repeated DB calls
Make pairing call recordings with phone calls more robust
Optimize matching of null-phone-number contacts to known equivalents
Make gvoice_sql.gvoiceconn inherit the sqlite connection class