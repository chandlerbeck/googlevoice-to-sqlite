googlevoice-to-sqlite
3.3	(2013-02-04)
(c) Arithmomaniac (arithmomaniac@hotmail.com) under LGPL2

# Update (2013-12-26): Due to a breaking change in the format of the HTML files, this code is deprecated. This project has moved to [GitHub](https://github.com/Arithmomaniac/gvoiceParser). #


---

This script/program takes the Google Voice records you can get from Google Takeout one step further - instead of thousands of tiny files, it produces a SQLite database that you can use to make lists (of past texts within a year, for example) and analyses (such as the people you talk to the most). It also can export the database to CSV.

This comes available as a Python 2.7 script, or a Windows executable. The Windows executable has no dependencies, but the Python script requres dateutil and html5lib to be installed on your machine.

## Usage ##

See READMEs for instructions


---


Changelog:
3.3 (2013-02-04)
> Made independent of user language
> Supports non-ASCII characters in texts
3.2.2 (2012-07-25)
> Bugfix for long contact names causing crash
3.2.1 (2012-07-23)
> Updated to match new Takeout filename formats
3.2	(2012-07-03)
> Updated to match new Takeout time formats
3.1 (2012-01-05)
    * Fixed bug where 'Welcome to Google Voice' message causes crash
    * Clearly labeled time fields as UTC
3.0 (2011-10-04)
    * All file names written on same line
    * EXE Packaging available
    * HTML unescaping inside text messages
2.0 (2011-09-26)
    * CSV exports and SQL views
    * Better file-input name handling
    * Performance enhancements - up to 80% faster
1.0 (2011-09-20)