#!/usr/bin/python

from __future__ import print_function
import os
import requests
import sys, getopt
from lxml import html

# saves downloaded asset to a directory
def download_to_file(filepath, url, session, headers, prefix_url=True):

    # skip if the file already exists
    if not os.path.exists(filepath):

        # append the domain
        if prefix_url:
            url = "https://www.packtpub.com" + url

        try:
            # the request object
            resource = session.get(url, verify=True, stream=True, headers=headers)

            # open the directory to write to
            target = open(filepath, 'wb')

            # save content in chunks: sometimes got memoryerror
            for chunk in resource.iter_content(chunk_size=1024):
                target.write(chunk)

            # dispose handle to the directory
            target.close()

        # handle an error when downloading
        except requests.exceptions.RequestException as e:

            print("Error downloading: " + filepath)
            print(e)

            # get the directory path
            directory = os.path.dirname(filepath)

            # delete directory if it's empty
            if not os.listdir(directory):
                os.rmdir(directory)
            # if not empty, remove the current file being downloaded
            elif os.path.exists(filepath):
                    os.remove(filepath)

            # terminate program
            sys.exit(1)
    else:
        print("Skipping download, since file is already present.")


# prepares book for download
def download_book(book, root_directory, formats, includeCode, session, headers):

    # scrub the title
    # sometimes ends with space, therefore the strip call
    title = book.xpath("@title")[0].replace("/","-").replace(" [eBook]","").replace(":", " -").strip()

    # path to save the file
    book_directory = os.path.join(root_directory, title)

    # create the directory if doesn't exist
    if not os.path.exists(book_directory):
        os.makedirs(book_directory)

    # in this way (the download happens only when the target path does not exist) the whole downloading is continuable
    # the title sometimes contains some weird characters that python could not print
    print('###########################################################################')
    print(title.encode(sys.stdout.encoding, errors='replace').decode())
    print('###########################################################################')

    # get the download links
    pdf = book.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/pdf')]/@href")
    epub = book.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/epub')]/@href")
    mobi = book.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/mobi')]/@href")
    code = book.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/code_download')]/@href")
    image = book.xpath(".//div[contains(@class,'product-thumbnail')]//img/@src")

    # pdf
    if len(pdf) > 0 and 'pdf' in formats:
        filename = os.path.join(book_directory, title + ".pdf")
        print("Downloading PDF: {0}".format(filename))
        download_to_file(filename, pdf[0], session, headers)

    # epub
    if len(epub) > 0 and 'epub' in formats:
        filename = os.path.join(book_directory, title + ".epub")
        print("Downloading EPUB: {0}".format(filename))
        download_to_file(filename, epub[0], session, headers)

    # mobi
    if len(mobi) > 0 and 'mobi' in formats:
        filename = os.path.join(book_directory, title + ".mobi")
        print("Downloading MOBI: {0}".format(filename))
        download_to_file(filename, mobi[0], session, headers)

    # code
    if len(code) > 0 and includeCode:
        filename = os.path.join(book_directory, title + " [CODE].zip")
        print("Downloading CODE: {0}".format(filename))
        download_to_file(filename, code[0], session, headers)

    # cover image
    if len(image) > 0 and 'jpg' in formats:
        filename = os.path.join(book_directory, title + ".jpg")
        image_url = "https:" + image[0].replace("/imagecache/thumbview", "", 1)
        print("Downloading IMAGE: {0}".format(filename))
        download_to_file(filename, image_url, session, headers, False)

    # delete directory if it's empty
    if not os.listdir(book_directory):
        os.rmdir(book_directory)


def main(argv):
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 " +
            "(KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}
    email = ''
    password = ''
    root_directory = 'packtpub_media'
    formats = 'pdf,mobi,epub,jpg'
    includeCode = False
    errorMessage = 'Usage: downloader.py -e <email> -p <password> [-f <formats> -d <directory> --include-code]'

    # get the command line arguments/options
    try:
        opts, args = getopt.getopt(argv,"ci:e:p:d:f:",["email=","pass=","directory=","formats=","include-code"])
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
            root_directory = os.path.expanduser(arg) if '~' in arg else os.path.abspath(arg)
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
            # download the book
            download_book(book, root_directory, formats, includeCode, session, headers)

if __name__ == "__main__":
    reload(sys)  
    sys.setdefaultencoding('utf8')
    main(sys.argv[1:])
