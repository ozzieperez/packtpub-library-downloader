#!/usr/bin/python

from __future__ import print_function
import os
from os import walk
import requests
import sys, getopt
import shutil
from lxml import html

# saves downloaded asset to a directory
def download_to_file(directory, isDirectoryEmpty, filename, url, session, headers, prefix_url=True):
    path_to_file = os.path.join(directory, filename)
    if not os.path.exists(path_to_file):
        if prefix_url:
            url = "https://www.packtpub.com" + url
            try:
                resource = session.get(url, verify=True, stream=True, headers=headers)

                # open the directory to write to
                target = open(path_to_file, 'wb')

                # save content in chunks: sometimes got memoryerror
                for chunk in resource.iter_content(chunk_size=1024):
                    target.write(chunk)

                # dispose handle to the directory
                target.close()
                print("Saved "+filename)
            except requests.exceptions.ConnectionError as e:
                if isDirectoryEmpty == True:
                    print("The directory was empty to begin with so will delete the whole directory")
                    print("Deleting "+directory)
                    shutil.rmtree(directory)
                    print("Deleted "+directory)
                else:
                    print("The directory was not empty so only removing this failed download if present")
                    if (os.path.exists(path_to_file)):
                        os.remove(path_to_file)
                    else:
                        print("No file was written nothing to delete")

def process_and_trigger_download(title,book,directory,formats,includeCode,session,headers):

    # path to save the file
    path = os.path.join(directory,title)
    # create the folder if doesn't exist
    if not os.path.exists(path):
        os.makedirs(path)
    # in this way (the download happens only when the target path does not exist) the whole downloading is continuable
    # the title sometimes contains some weird characters that python could not print
    print('###########################################################################')
    print(title.encode(sys.stdout.encoding, errors='replace').decode())
    print('###########################################################################')

    files_in_directory = []
    directory_empty = False
    for (_, _, filenames) in walk(path):
        files_in_directory.extend(filenames)
    if not files_in_directory:
        directory_empty = True
    else:
        directory_empty = False

    # get the download links
    pdf = book.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/pdf')]/@href")
    epub = book.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/epub')]/@href")
    mobi = book.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/mobi')]/@href")
    code = book.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/code_download')]/@href")
    image = book.xpath(".//div[contains(@class,'product-thumbnail')]//img/@src")

    # pdf
    if len(pdf) > 0 and 'pdf' in formats:
        filename = title + ".pdf"
        path_to_file = os.path.join(path, filename)
        if not os.path.exists(path_to_file):
            print("Downloading PDF:{0} -> {1}".format(pdf[0],filename))
            download_to_file(path, directory_empty, filename, pdf[0], session, headers)
        else:
            print(filename+" already present not being downloaded.")

    # epub
    if len(epub) > 0 and 'epub' in formats:
        filename = title + ".epub"
        path_to_file = os.path.join(path, filename)
        if not os.path.exists(path_to_file):
            print("Downloading EPUB:{0} -> {1}".format(epub[0],filename))
            download_to_file(path, directory_empty, filename, epub[0], session, headers)
        else:
            print(filename+" already present not being downloaded.")

    # mobi
    if len(mobi) > 0 and 'mobi' in formats:
        filename = title + ".mobi"
        path_to_file = os.path.join(path, filename)
        if not os.path.exists(path_to_file):
            print("Downloading MOBI:{0} -> {1}".format(mobi[0],filename))
            download_to_file(path, directory_empty, filename, mobi[0], session, headers)
        else:
            print(filename+" already present not being downloaded.")

    # code
    if len(code) > 0 and includeCode:
        filename = title + " [CODE].zip"
        path_to_file = os.path.join(path, filename)
        if not os.path.exists(path_to_file):
            print("Downloading CODE:{0} -> {1}".format(code[0],filename))
            download_to_file(path, directory_empty, filename, code[0], session, headers)
        else:
            print(filename+" already present not being downloaded.")

    # Cover-image
    if len(image) > 0 and 'jpg' in formats:
        filename = title + " [Cover].jpg"
        path_to_file = os.path.join(path, filename)
        if not os.path.exists(path_to_file):
            image_url = "https:" + image[0].replace("/imagecache/thumbview", "", 1)
            print("Downloading IMAGE:{0} -> {1}".format(image_url,filename))
            download_to_file(path, directory_empty, filename, image_url, session, headers, False)
        else:
            print(filename+" already present not being downloaded.")


def main(argv):
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 " +
            "(KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}
    email = ''
    password = ''
    ignorelist = False
    path_to_ignore_list = ''
    list_of_ignore_items = []
    directory = 'packtpub_media'
    formats = 'pdf,mobi,epub,jpg'
    includeCode = False
    errorMessage = 'Usage: downloader.py -e <email> -p <password> [-f <formats> -d <directory> --include-code -i]'

    # get the command line arguments/options
    try:
        opts, args = getopt.getopt(argv,"ci:e:p:d:f:",["email=","pass=","directory=","formats=","include-code","ignore-list"])
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
        elif opt in ('-i','--ignore-list'):
            path_to_ignore_list = arg
            ignorelist = True


    # do we have the minimum required info
    if not email or not password:
        print(errorMessage)
        sys.exit(2)

    if ignorelist:
        with  open(path_to_ignore_list,"r") as ignoreFile:
            list_of_ignore_items=ignoreFile.readlines()
        list_of_ignore_items = [x.strip() for x in list_of_ignore_items]

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
            if ignorelist:
                if title in list_of_ignore_items:
                    print('###########################################################################')
                    print ("Skipping {0} as it is present in the ignore list".format(title))
                    print('###########################################################################')
                    continue      
                else:
                    process_and_trigger_download(title,book,directory,formats,includeCode,session,headers)
            else:
                process_and_trigger_download(title,book,directory,formats,includeCode,session,headers)

if __name__ == "__main__":

    reload(sys)  
    sys.setdefaultencoding('utf8')
    main(sys.argv[1:])
