#!/usr/bin/python

import os
import requests
import sys, getopt
from lxml import html

# saves downloaded asset to a directory
def download_to_file(directory, url, session, headers, prefix_url=True):
        if not os.path.exists(directory):
                # save content in chunks: sometimes got memoryerror
                if prefix_url:
                    url = "https://www.packtpub.com" + url
                resource = session.get(url, verify=True, stream=True, headers=headers)
		target = open(directory, 'wb')
		for chunk in resource.iter_content(chunk_size=1024):
			target.write(chunk)
		target.close()

def main(argv):
	headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 " +
		"(KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}
	email = ''
	password = ''
	directory = 'packtpub_media'
	formats = 'pdf,mobi,epub,jpg'
	includeCode = False
	errorMessage = 'Usage: downloader.py -e <email> -p <password> [-f <formats> -d <directory> --include-code]'

   	# get the command line arguments/options
	try:	
  		opts, args = getopt.getopt(argv,"ce:p:d:f:",["email=","pass=","directory=","formats=","include-code"])
	except getopt.GetoptError:
  		print(errorMessage)
  		sys.exit(2)

  	# hold the values of the command line options
	for opt, arg in opts:
		if opt in ('-e','--email'):
	 		email = arg
		elif opt in ('-p','--pass'):
	 		password = arg
		elif opt in ('-d','--directory'):
			directory = os.path.expanduser(arg) if '~' in arg else os.path.abspath(arg)
		elif opt in ('-f','--formats'):
			formats = arg
		elif opt in ('-c','--include-code'):
			includeCode = True

	# do we have the minimum required info
	if not email or not password:
		print(errorMessage)
		sys.exit(2)

	# create a session
	session = requests.Session()

	print("Attempting to login...")
	
	# initial request to get the "csrf token" for the login
	url = "https://www.packtpub.com/"
	start_req = session.get(url, verify=True, headers=headers)

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
	session.post(url, data=login_data, verify=True, headers=headers)

	# get the ebooks page
	books_page = session.get("https://www.packtpub.com/account/my-ebooks", verify=True, headers=headers)
	books_tree = html.fromstring(books_page.content)

	# login successful?
	if "Register" in books_tree.xpath("//title/text()")[0]:
		print("Invalid login.")
	
	# we're in, start downloading
	else:
		print("Logged in successfully!")

		# any books?
		book_nodes = books_tree.xpath("//div[@id='product-account-list']/div[contains(@class,'product-line unseen')]")

		print("Found %s books" % len(book_nodes))

		# loop through the books
		for book in book_nodes:

			# scrub the title
			# sometimes ends with space but the created directory does not contain, therefore the strip call
			title = book.xpath("@title")[0].replace("/","-").replace(" [eBook]","").strip()
			# title fix: colon is not valid in path (at least on windows) but the title sometimes contain it
			title = title.replace(":", " -")
			# path to save the file
			path = os.path.join(directory,title)
			# create the folder if doesn't exist
			if not os.path.exists(path):
				os.makedirs(path)
				# in this way (the download happens only when the target path does not exist) the whole downloading is continuable
				# the title sometimes contains some weird characters that python could not print
				print('#################################################################')
				print(title.encode(sys.stdout.encoding, errors='replace'))
				print('#################################################################')
				
				# get the download links
				pdf = book.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/pdf')]/@href")
				epub = book.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/epub')]/@href")
				mobi = book.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/mobi')]/@href")
				code = book.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/code_download')]/@href")
                                image = book.xpath(".//div[contains(@class,'product-thumbnail')]//img/@src")
				
				# pdf
				if len(pdf) > 0 and 'pdf' in formats:
					filename = os.path.join(path, title + ".pdf")
					print("Downloading PDF:", pdf[0])
					download_to_file(filename, pdf[0], session, headers)

				# epub
				if len(epub) > 0 and 'epub' in formats:
					filename = os.path.join(path, title + ".epub")
					print("Downloading EPUB:", epub[0])
					download_to_file(filename, epub[0], session, headers)

				# mobi
				if len(mobi) > 0 and 'mobi' in formats:
					filename = os.path.join(path, title + ".mobi")
					print("Downloading MOBI:", mobi[0])
					download_to_file(filename, mobi[0], session, headers)

				# code
				if len(code) > 0 and includeCode:
					filename = os.path.join(path, title + " [CODE].zip")
					print("Downloading CODE:", code[0])
					download_to_file(filename, code[0], session, headers)

                                # Cover-image
                                if len(image) > 0 and 'jpg' in formats:
                                        filename = os.path.join(path, title + " [Cover].jpg")
                                        image_url = "https:" + image[0].replace("/imagecache/thumbview", "", 1)
                                        print("Downloading IMAGE:", image_url)
                                        download_to_file(filename, image_url, session, headers, False)



if __name__ == "__main__":
   main(sys.argv[1:])
