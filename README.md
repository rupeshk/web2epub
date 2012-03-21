#web2epub

web2epub is a command line tool to convert html to epub. Given a set of web pages web2epub converts them into an epub. The epub is cleaned up to remove unnecessary parts, retains images and can have an optional cover. web2epub is written in Python.

##Features

* Simple usage
* Convert pages into readable format using python-readability [https://github.com/buriy/python-readability] 
* Create a nice TOC based on web page titles
* Option to add an image for book cover

##Usage

	Usage: web2epub.py [options] url1 url2 ...urln

	Options:
  		-t TITLE, --title=TITLE title of the epub
  		-a AUTHOR, --author=AUTHOR author of the epub
  		-c COVER, --cover=COVER path to cover image
  		-o OUTFILE, --outfile=OUTFILE name of output file

##Credits

* All the hard work of formatting pages is performed by python-readability [https://github.com/buriy/python-readability]
* Code for creation of ebooks came from Manuel Strehl a.k.a Boldewyn http://www.manuel-strehl.de/dev/simple_epub_ebooks_with_python.en.html
