README
----------------
googlevoice-to-sqlite 
3.1	(2012-01-05)
(c) Arithmomaniac (arithmomaniac@hotmail.com) under LGPL2+/GPL2.1+/MPL1.1+ tri-license
-------------
The gvoice-to-sqlite script takes the Google Voice records you can get from Google Takeout one step further - instead of thousands of tiny files, it produces a SQLite database that you can use to make lists (of past texts within a year, for example) and analyses (such as the people you talk to the most). It also can export the database to CSV.

This script has no dependencies except for Python 2.7 itself. If this is too much for you, download the win32 package from the website.

This project is similar to GV Mirror [http://freshmeat.net/projects/gv-mirror] - you may want to check that out instead.

-------------

Basic file structure (all in root directory):
- googlevoice_to_sqlite.py			the main executable
	- gvoice_parse.py			a parsing library that returns GVoice objects
	- gvoice_sql.py				the Python-to-SQLite inferface
		- initdb.sql			The SQL that creates the database.

-------------

To use this script:
1) 	Download and unzip your Voice data from Google Takeout.
2) 	Start googlevoice_to_sqlite.py
3) 	Provide the location of the "conversations" directory
4) 	Follow the directions
5) 	The results are stored in .\bin\output. A database diagram exists on the project homepage.
	If you want to save the results, copy it out of the directory. Due to limitations in Google's contact persistence, the entire database is rewritten every time.

If you need a SQLite client, try SQLite Studio (Windows) or SQLite Manager (Firefox). If you would like to import the data into Excel, Oracle, SQL Server, etc on Windows, use OLDEB, or export the tables to CSV and import manually.

--------------

Changelog:
3.1 (2012-01-05)
	Fixed bug where 'Welcome to Google Voice' message causes crash
	Clearly labeled time fields as UTC
3.0	(2011-10-04)
	All file names written on same line
	EXE Packaging available
	HTML unescaping inside text messages
2.0 (2011-09-26)
	CSV exports and SQL views
	Better file-input name handling
	Performance enhancements - up to 80% faster
1.0 (2011-09-20)

---------------

Performance Notes

Since several thousand objects are created during execution, this script can take a while to run. here's an approximate performance breakdown for the main routine.

10% - File Reading
50% - XML tree creation
30% - Object parsing/creation
10% - Database insertion/processing