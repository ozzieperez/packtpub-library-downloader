# PacktPub Library Downloader

Automatically download all your eBooks. 	
(See: [PacktPub Free Daily Book](https://www.packtpub.com/packt/offers/free-learning))


## How to use it:
	python downloader.py -e <email> -p <password> [-f <formats> -d <directory> --include-code]

##### Example: Download PDFs, EPUBs, and source code to my Desktop
	python downloader.py -e 'hello@world.com' -p 'p@ssw0rd' -f 'pdf,epub' -d '~/Desktop' -c

### Options
*-e*, *--email* = Your login email	
*-p*, *--password* = Your login password	
*-f*, *--formats* = File formats to download. Default is "pdf,mobi,epub"	
*-d*, *--directory* = Directory to download into. Default is "packt_ebooks/" in the current directory		
*-c*, *--include-code* = Flag to include code files, if any	

Tested working on Python 2.7.11

## Dependencies:


* [Requests](http://docs.python-requests.org/en/latest/) for HTTP requests:

		pip install requests
	
* [lxml](http://lxml.de/) for HTML parsing:

		pip install lxml
	
