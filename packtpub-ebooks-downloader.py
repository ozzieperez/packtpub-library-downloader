import requests
import os
from lxml import html

# saves downloaded asset to a directory
def download_resource(directory, url):
	if not os.path.exists(directory):
			resource = c.get("https://www.packtpub.com" + url)
			target = open(directory, 'w')
			target.write(resource.content)
			target.close()

with requests.Session() as c:
	url = "https://www.packtpub.com/"
	email = raw_input("Login email: ") 
	password = raw_input("Password: ")

	# initial request to get the "csrf token" for the login
	start_req = c.get(url)

	# extract the "csrf token" (form_build_id) to submit with login POST
	tree = html.fromstring(start_req.content)
	form_build_id = tree.xpath('//form[@id="packt-user-login-form"]//input[@name="form_build_id"]/@id')[0]

	# payload for login
	login_data = dict(
			email=email, 
			password=password, 
			op="Login", 
			form_id="packt_user_login_form",
			form_build_id=form_build_id
		)

	# login
	c.post(url, data=login_data, headers= {"Referer":"https://www.packtpub.com/"})

	# get the ebooks page
	books_page = c.get("https://www.packtpub.com/account/my-ebooks")
	books_tree = html.fromstring(books_page.content)

	# login successful?
	if "Register" in books_tree.xpath("//title/text()")[0]:
		print "Invalid login."
	
	# we're in, start downloading
	else:
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
				
				# get the links
				pdf = book.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/pdf')]/@href")
				epub = book.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/epub')]/@href")
				mobi = book.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/mobi')]/@href")
				code = book.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/code_download')]/@href")
				
				#pdf
				if len(pdf) > 0:
					filename = directory + "/" + title + ".pdf"
					print "Downloading PDF", pdf[0]
					download_resource(filename, pdf[0])

				#epub
				if len(epub) > 0:
					filename = directory + "/" + title + ".epub"
					print "Downloading EPUB", epub[0]
					download_resource(filename, epub[0])

				#mobi
				if len(mobi) > 0:
					filename = directory + "/" + title + ".mobi"
					print "Downloading MOBI", mobi[0]
					download_resource(filename, mobi[0])

				#code
				if len(code) > 0:
					filename = directory + "/" + title + " [CODE].zip"
					print "Downloading CODE", code[0]
					download_resource(filename, code[0])

