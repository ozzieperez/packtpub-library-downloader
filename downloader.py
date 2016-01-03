#!/usr/bin/python

import os
import requests
import sys, getopt
from lxml import html

session = requests.Session()

# saves downloaded asset to a directory
def download_to_file(directory, url):
	if not os.path.exists(directory):
			resource = session.get("https://www.packtpub.com" + url)
			target = open(directory, 'w')
			target.write(resource.content)
			target.close()

def main(argv):
   	email = ''
   	password = ''
   	directory = ''
   	formats = ''
   	includeCode = False

   	# get the command line arguments/options
	try:	
  		opts, args = getopt.getopt(argv,"ce:p:d:f:",["email=","pass=","download-directory=","formats=","include-code"])
	except getopt.GetoptError:
  		print 'downloader.py -e <email> -p <password> [-d <download_directory>]'
  		sys.exit(2)

  	# hold the values of the command line options
	for opt, arg in opts:
		if opt in ('-e','--email'):
	 		email = arg
		elif opt in ('-p','--pass'):
	 		password = arg
		elif opt in ('-d','--download_directory'):
			directory = arg
		elif opt in ('-f','--formats'):
			formats = arg
		elif opt in ('-c','--include-code'):
			includeCode = True

	# do we have the minimum required info
	if not email or not password:
		print "Usage: downloader.py -e <email> -p <password> [-d <download_directory>]"
		sys.exit(2)

	# initial request to get the "csrf token" for the login
	print "Attempting to login..."
	url = "https://www.packtpub.com/"
	start_req = session.get(url)

	# extract the "csrf token" (form_build_id) to submit with login POST
	tree = html.fromstring(start_req.content)
	form_build_id = tree.xpath('//form[@id="packt-user-login-form"]//input[@name="form_build_id"]/@id')[0]

	# payload for login
	login_data = dict(
			email=email, 
			password=password, 
			op="Login", 
			form_id="packt_user_login_form",
			form_build_id=form_build_id)

	# login
	session.post(url, data=login_data)

	# get the ebooks page
	books_page = session.get("https://www.packtpub.com/account/my-ebooks")
	books_tree = html.fromstring(books_page.content)

	# login successful?
	if "Register" in books_tree.xpath("//title/text()")[0]:
		print "Invalid login."
	
	# we're in, start downloading
	else:
		print "Logged in successfully!"

		# any books?
		book_nodes = books_tree.xpath("//div[@id='product-account-list']/div[contains(@class,'product-line unseen')]")

		print "Found %s books" % len(book_nodes)

		#loop through the books
		for book in book_nodes:
			
				#strip junk from the title
				title = book.xpath("@title")[0].replace("/","-").replace(" [eBook]","")
				directory = "packt_downloads/" + title
				
				# create the folder if doesn't exist
				if not os.path.exists(directory):
					os.makedirs(directory)

				print '#################################################################'
				print title
				print '#################################################################'
				
				# get the download links
				pdf = book.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/pdf')]/@href")
				epub = book.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/epub')]/@href")
				mobi = book.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/mobi')]/@href")
				code = book.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/code_download')]/@href")
				
				#pdf
				if len(pdf) > 0 and 'pdf' in formats:
					filename = directory + "/" + title + ".pdf"
					print "Downloading PDF:", pdf[0]
					download_to_file(filename, pdf[0])

				#epub
				if len(epub) > 0 and 'epub' in formats:
					filename = directory + "/" + title + ".epub"
					print "Downloading EPUB:", epub[0]
					download_to_file(filename, epub[0])

				#mobi
				if len(mobi) > 0 and 'mobi' in formats:
					filename = directory + "/" + title + ".mobi"
					print "Downloading MOBI:", mobi[0]
					download_to_file(filename, mobi[0])

				#code
				if len(code) > 0 and includeCode:
					filename = directory + "/" + title + " [CODE].zip"
					print "Downloading CODE:", code[0]
					download_to_file(filename, code[0])


if __name__ == "__main__":
   main(sys.argv[1:])
