# PacktPub Library Downloader

Automatically download all your eBooks and videos. (See: [PacktPub Free Daily Book](https://www.packtpub.com/packt/offers/free-learning))


## Usage:
	python downloader.py -e <email> -p <password> [-d <directory> -b <book assets> -v <video assets>]

##### Example: Download books in PDF and EPUB formats and accompanying source code
	python downloader.py -e hello@world.com -p p@ssw0rd -d ~/Desktop/packt -b pdf,epub,code

##### Example: Download videos, their cover image, and accompanying source code
	python downloader.py -e hello@world.com -p p@ssw0rd -d ~/Desktop/packt -v video,cover,code

##### Example: Download Integrated Courses (Interactive-Ebooks), their cover image, and accompanying source code
	python downloader.py -e hello@world.com -p p@ssw0rd -d ~/Desktop/packt -c course,cover,code

##### Example: Download everything
	python downloader.py -e hello@world.com -p p@ssw0rd -d ~/Desktop/packt -b pdf,epub,mobi,cover,code,info -v video,cover,code -c course,cover,code


## Commandline Options
- *-e*, *--email* = Your login email
- *-p*, *--password* = Your login password
- *-d*, *--directory* = Directory to download into. Default is "packtpub_media/" in the current directory
- *-v*, *--videos* = Assets to download. Options are: *video,cover,code*
- *-b*, *--books* = Assets to download. Options are: *pdf,mobi,epub,cover,code,info*
- *-c*, *--courses* = Assets to download. Options are: *course,cover,code*

**Video Assets**

- *video*: The video file
- *cover*: Cover image
- *code*: Accompanying source code

**Book Assets**

- *pdf*: PDF format
- *mobi*: MOBI format
- *epub*: EPUB format
- *cover*: Cover image
- *code*: Accompanying source code
- *info*: Creates a JSON file with the title, ISBN, # of pages, and description. (note: it slows downloads)

**Course Assets**

- *course*: The interactive ebook (with integrated videos etc.)
- *cover*: Cover image
- *code*: Accompanying source code


## Dependencies:


* [Requests](http://docs.python-requests.org/en/latest/) for HTTP requests:

		pip install requests

* [lxml](http://lxml.de/) for HTML parsing:

		pip install lxml

Tested working on Python 2.7.11 and Python 3.6.0 :: Anaconda 4.3.0 (64-bit)
