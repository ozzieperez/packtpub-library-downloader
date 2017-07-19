# PacktPub Library Downloader

Automatically download all your eBooks and Videos. (See: [PacktPub Free Daily Book](https://www.packtpub.com/packt/offers/free-learning))


## How to use it:
	python downloader.py -e <email> -p <password> [-f <formats> -d <directory>]

##### Example: Download PDFs, EPUBs, and source code to my Desktop
	python downloader.py -e hello@world.com -p p@ssw0rd -f pdf,epub,code -d ~/Desktop

##### Video-Example: Download Videos, Cover-Image and source code to my Desktop
	python downloader.py -e hello@world.com -p p@ssw0rd -f video,jpg,code -d ~/Desktop 


### Options
- *-e*, *--email* = Your login email
- *-p*, *--password* = Your login password
- *-f*, *--files* = File types to download. Default is "pdf,mobi,epub,jpg,code". You can select from: pdf, mobi, epub, code, jpg, video
- *-d*, *--directory* = Directory to download into. Default is "packtpub_media/" in the current directory

## Dependencies:


* [Requests](http://docs.python-requests.org/en/latest/) for HTTP requests:

		pip install requests

* [lxml](http://lxml.de/) for HTML parsing:

		pip install lxml

Tested working on Python 2.7.11 and Python 3.6.0 :: Anaconda 4.3.0 (64-bit)
