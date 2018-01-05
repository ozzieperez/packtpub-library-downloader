#!/usr/bin/python

from __future__ import print_function
import os
import requests
import sys, getopt
import json
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

            # if a file was being downloaded, delete it
            if os.path.exists(filepath):
                    os.remove(filepath)

            # delete directory if it's empty
            directory = os.path.dirname(filepath)
            if not os.listdir(directory):
                os.rmdir(directory)

            # terminate program
            sys.exit(1)
    else:
        print("Skipping download: File already exists.")


# creates a json file with info
def save_book_details(book, title, directory, session, headers):

    # fetch the product page
    product_url = book.xpath(".//div[contains(@class,'product-thumbnail')]//a/@href")
    product_page = session.get("https://www.packtpub.com" + product_url[0], verify=True, headers=headers)
    product_tree = html.fromstring(product_page.content)

    # the book details section
    info = product_tree.xpath("//*[@id='main-book']//div[contains(@class,'book-info-wrapper')]")

    # any details?
    if len(info) > 0:

        # unformatted book title
        original_title = book.xpath("@title")[0]

        # the json elements
        info_dict = {'originalTitle':original_title}
        info_dict['isbn'] = info[0].xpath(".//span[@itemprop='isbn']/text()")[0]
        info_dict['pages'] = info[0].xpath(".//span[@itemprop='numberOfPages']/text()")[0]
        info_dict['description'] = '<br>'.join(info[0].xpath(".//div[@itemprop='description']/p/text()"))

        print ("Saving INFO")

        # save to file
        filename = os.path.join(directory, title + ".json")
        with open(filename, 'w') as outfile:
            json.dump(info_dict, outfile)


# prepares book for download
def download_book(book, directory, assets, session, headers):

    # scrub the title
    title = book.xpath("@title")[0].replace("/","-").replace(" [eBook]","").replace(":", " -").strip()

    # path to save the file
    book_directory = os.path.join(directory, title)

    # create the directory if doesn't exist
    if not os.path.exists(book_directory):
        os.makedirs(book_directory)

    # the title sometimes contains some weird characters that python could not print
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(title.encode(sys.stdout.encoding, errors='replace').decode())

    # get the download links
    pdf = book.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/pdf')]/@href")
    epub = book.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/epub')]/@href")
    mobi = book.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/mobi')]/@href")
    code = book.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/code_download')]/@href")
    image = book.xpath(".//div[contains(@class,'product-thumbnail')]//img/@src")

    # pdf
    if len(pdf) > 0 and 'pdf' in assets:
        filename = os.path.join(book_directory, title + ".pdf")
        print("Downloading PDF")
        download_to_file(filename, pdf[0], session, headers)

    # epub
    if len(epub) > 0 and 'epub' in assets:
        filename = os.path.join(book_directory, title + ".epub")
        print("Downloading EPUB")
        download_to_file(filename, epub[0], session, headers)

    # mobi
    if len(mobi) > 0 and 'mobi' in assets:
        filename = os.path.join(book_directory, title + ".mobi")
        print("Downloading MOBI")
        download_to_file(filename, mobi[0], session, headers)

    # code
    if len(code) > 0 and 'code' in assets:
        filename = os.path.join(book_directory, title + " [CODE].zip")
        print("Downloading CODE")
        download_to_file(filename, code[0], session, headers)

    # cover image
    if len(image) > 0 and 'cover' in assets:
        filename = os.path.join(book_directory, title + ".jpg")
        image_url = "https:" + image[0].replace("/imagecache/thumbview", "", 1)
        print("Downloading IMAGE")
        download_to_file(filename, image_url, session, headers, False)

    # book details
    if 'info' in assets:
        save_book_details(book, title, book_directory, session, headers)

    # delete directory if it's empty
    if not os.listdir(book_directory):
        os.rmdir(book_directory)


# download video
def download_video(video, directory, assets, session, headers):

    # scrub the title
    title = video.xpath("@title")[0].replace("/","-").replace(" [Video]","").replace(":", " -").strip()

    # path to save the file
    video_directory = os.path.join(directory, title)

    # create the directory if doesn't exist
    if not os.path.exists(video_directory):
        os.makedirs(video_directory)

    # the title sometimes contains some weird characters that python could not print
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(title.encode(sys.stdout.encoding, errors='replace').decode())

    # get the download links
    code = video.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/code_download')]/@href")
    image = video.xpath(".//div[contains(@class,'product-thumbnail')]//img/@src")
    video = video.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/video')]/@href")

    # video
    if len(video) > 0 and 'video' in assets:
        filename = os.path.join(video_directory, title + " [VIDEO].zip")
        print("Downloading VIDEO")
        download_to_file(filename, video[0], session, headers)

    # code
    if len(code) > 0 and 'code' in assets:
        filename = os.path.join(video_directory, title + " [CODE].zip")
        print("Downloading CODE")
        download_to_file(filename, code[0], session, headers)

    # cover image
    if len(image) > 0 and 'cover' in assets:
        filename = os.path.join(video_directory, title + ".jpg")
        image_url = "https:" + image[0].replace("/imagecache/thumbview", "", 1)
        print("Downloading IMAGE")
        download_to_file(filename, image_url, session, headers, False)

    # delete directory if it's empty
    if not os.listdir(video_directory):
        os.rmdir(video_directory)

# download course
def download_course(course, directory, assets, session, headers):

    # scrub the title
    title = course.xpath("@title")[0].replace("/","-").replace(" [course]","").replace(":", " -").strip()

    # path to save the file
    course_directory = os.path.join(directory, title)

    # create the directory if doesn't exist
    if not os.path.exists(course_directory):
        os.makedirs(course_directory)

    # the title sometimes contains some weird characters that python could not print
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(title.encode(sys.stdout.encoding, errors='replace').decode())

    # get the download links
    code = course.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/code_download')]/@href")
    image = course.xpath(".//div[contains(@class,'product-thumbnail')]//img/@src")
    course = course.xpath(".//div[contains(@class,'download-container')]//a[contains(@href,'/video_download')]/@href")

    # course
    if len(course) > 0 and 'course' in assets:
        filename = os.path.join(course_directory, title + " [course].zip")
        print("Downloading COURSE")
        download_to_file(filename, course[0], session, headers)

    # code
    if len(code) > 0 and 'code' in assets:
        filename = os.path.join(course_directory, title + " [CODE].zip")
        print("Downloading CODE")
        download_to_file(filename, code[0], session, headers)

    # cover image
    if len(image) > 0 and 'cover' in assets:
        filename = os.path.join(course_directory, title + ".jpg")
        image_url = "https:" + image[0].replace("/imagecache/thumbview", "", 1)
        print("Downloading IMAGE")
        download_to_file(filename, image_url, session, headers, False)

    # delete directory if it's empty
    if not os.listdir(course_directory):
        os.rmdir(course_directory)

def main(argv):
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 " +
            "(KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}
    email = None
    password = None
    root_directory = 'packtpub_media'
    book_assets = None # 'pdf,mobi,epub,cover,code'
    video_assets = None # 'video,cover,code'
    course_assets = None # 'course,cover,code'
    errorMessage = 'Usage: downloader.py -e <email> -p <password> [-d <directory> -b <book assets>  -v <video assets> -c <course assets>]'

    # get the command line arguments/options
    try:
        opts, args = getopt.getopt(argv,"e:p:d:b:v:c:",["email=","pass=","directory=","books=","videos=","courses="])
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
        elif opt in ('-b','--books'):
            book_assets = arg
        elif opt in ('-v','--videos'):
            video_assets = arg
        elif opt in ('-c','--courses'):
            course_assets = arg


    # do we have the minimum required info?
    if not email or not password:
        print(errorMessage)
        sys.exit(2)

    # create an http session
    session = requests.Session()

    print("Attempting to login...")

    # request to get the "csrf token" for the login
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

    # check if successful login by getting the account page and check if redirected to 'register' page
    account_page = session.get("https://www.packtpub.com/account", verify=True, headers=headers)
    accountpage_tree = html.fromstring(account_page.content)

    # login successful?
    if "Register" in accountpage_tree.xpath("//title/text()")[0]: # redirects to the 'Register' page if login fails
        print("Invalid login.")

    # we're in, start downloading
    else:
        print("Logged in successfully!")

        if book_assets:

            # get the list of books
            books_page = session.get("https://www.packtpub.com/account/my-ebooks", verify=True, headers=headers)
            books_tree = html.fromstring(books_page.content)
            book_nodes = books_tree.xpath("//div[@id='product-account-list']/div[contains(@class,'product-line unseen')]")

            print('###########################################################################')
            print("FOUND {0} BOOKS: STARTING DOWNLOADS".format(len(book_nodes)))
            print('###########################################################################')

            # loop through the books
            for book in book_nodes:

                # download the book
                books_directory = os.path.join(root_directory, "books")
                download_book(book, books_directory, book_assets, session, headers)

        if video_assets:

            # get the list of videos
            videos_page = session.get("https://www.packtpub.com/account/my-videos", verify=True, headers=headers)
            videos_tree = html.fromstring(videos_page.content)
            video_nodes = videos_tree.xpath("//div[@id='product-account-list']/div[contains(@class,'product-line unseen')]")

            print('###########################################################################')
            print("FOUND {0} VIDEOS: STARTING DOWNLOADS".format(len(video_nodes)))
            print('###########################################################################')

            # loop through the videos
            for video in video_nodes:

                # download the book
                videos_directory = os.path.join(root_directory, "videos")
                download_video(video, videos_directory, video_assets, session, headers)

        if course_assets:

            # get the list of videos
            courses_page = session.get("https://www.packtpub.com/account/my-courses", verify=True, headers=headers)
            courses_tree = html.fromstring(courses_page.content)
            course_nodes = courses_tree.xpath("//div[@id='product-account-list']/div[contains(@class,'product-line unseen')]")

            print('###########################################################################')
            print("FOUND {0} INTEGRATED COURSES: STARTING DOWNLOADS".format(len(course_nodes)))
            print('###########################################################################')

            # loop through the videos
            for course in course_nodes:

                # download the book
                courses_directory = os.path.join(root_directory, "courses")
                download_course(course, courses_directory, course_assets, session, headers)


if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf8')
    main(sys.argv[1:])
