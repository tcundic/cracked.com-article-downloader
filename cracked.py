#!/usr/bin/env python
# coding=utf-8

__author__ = 'Tomislav Cundić'

import re
import urllib2
import sys
from bs4 import BeautifulSoup
import os
from urllib2 import Request, URLError, HTTPError
import codecs
import shutil


class Cracked(object):
    __style = None

    def __init__(self, articleurl):
        # http url to article
        self.url = articleurl
        #
        self.header = None
        # Metadata about article, for epub
        self.authors = ""
        # authors
        self.auth = None
        # BeautifulSoup object for editing pages
        self.page = None
        # url to first/second page of article
        self.page1 = None
        # boolean, if article consist of one or two pages
        self.page2 = None
        # BeautifulSoup object for editing article's 1st page
        self.html = None
        # BeautifulSoup object for editing article's 2nd page
        self.html2 = None
        # remove title of article (on 2nd page)
        self.naslov = None
        # first element of article's body
        self.h1 = None
        # name of article
        self.name = None
        # directory for saving articles
        self.dir = None
        # relative path to html images
        self.dir3 = None
        # for converting html to epub (name of article + epub extension)
        self.epub = None
        # save web page locally
        self.output = None
        # arguments for command line
        self.convertArg = None

        # after download put style to html
        Cracked.__style = """
        <style>
            .body {
                text-align:justify;
                margin-left: 5%;
                margin-right: 5%;
                }

            h1, h2, h3 	{text-align:center;}
            footer	{text-align:center;}

            img	{
            display:block;
            margin-left: auto;
            margin-right: auto;
            margin-bottom: 0px;
            margin-top: 30px;
            }
        </style>"""

    def fetch_webpage(self):
        self.page1 = urllib2.urlopen(self.url)
        # first script assume that article have two web pages
        self.page2 = True
        self.page = BeautifulSoup(self.page1)

        # try to find link to article second page
        try:
            self.page1 = urllib2.urlopen(self.page.find("a", {"class": "next"}).get('href'))
        except AttributeError:
            self.page2 = False  # article is one page (blog or quick-fix)

    @staticmethod
    def remove_elements(pagination, social, iframe, _object, meta=None):
        """
        This function remove unnecessary elements from article
        @type pagination: BeautifulSoup object
        @param pagination: next/prev pagination element:
        @type social: BeautifulSoup object
        @param social: share elements
        @type iframe: BeautifulSoup object
        @param iframe: video elements
        @type _object: BeautifulSoup object
        @param _object: video elements
        @type meta: BeautifulSoup object
        @param meta: metadata on 2nd page
        """
        if pagination is not None:
            pagination.decompose()

        if social is not None:
            for s in social:
                s.decompose()

        if iframe is not None:
            for v in iframe:
                v.decompose()

        if _object is not None:
            for v in _object:
                v.decompose()

        if meta is not None:
            meta.decompose()

    def format_page(self):
        # if article is on two pages
        if self.page2:
            # find title of article
            self.h1 = self.page.find('h1')
            # after that find parent of h1 tag, that mean find body of article
            self.html = self.h1.find_parent(attrs={"class": "body"})

            ''' script will merge two paged article in one html
            so remove html element with links to article
            next/prev page(just see any cracked.com article) '''
            # remove all elements with class that have "social" in name
            # remove (add to favorites, share on twitter, facebook etc.)
            # remove any video from article
            # remove any video from article
            self.remove_elements(self.html.find(class_=re.compile("Pagination")),
                                 self.html.find_all(class_=re.compile("social")),
                                 self.html.find_all('iframe'),
                                 self.html.find_all('object'))

            # get article name
            self.name = self.html.find('h1').get_text()

            # get article second page
            self.page = BeautifulSoup(self.page1)

            self.h1 = self.page.find('h1')
            self.html2 = self.h1.find_parent(attrs={"class": "body"})

            # remove article title so it doesn't repeat
            self.naslov = self.html2.find('h1').decompose()

            self.remove_elements(self.html2.find(class_=re.compile("Pagination")),
                                 self.html2.find_all(class_=re.compile("social")),
                                 self.html2.find_all('iframe'),
                                 self.html2.find_all('object'),
                                 # remove metadata of article(author, date, views so it doesn't repeat)
                                 self.html2.find(class_=re.compile("meta")))

            self.html.prettify("utf-8")
            self.html2.prettify("utf-8")

        if not self.page2:
            # if article have only one page
            self.h1 = self.page.find('h1')
            self.html = self.h1.find_parent(attrs={"class": "body"})

            self.remove_elements(self.html.find(class_=re.compile("pagin")),
                                 self.html.find_all(class_=re.compile("social")),
                                 self.html.find_all('iframe'),
                                 self.html.find_all('object'))

            self.name = self.html.find('h1').get_text()
            # self.name = re.escape(self.name)

    def __fetchimages(self, datoteka, link):
        # get image url
        self.__url = link
        if self.__url is not None:
            self.__req = Request(self.__url)

            # save image locally from url
            try:

                os.system("wget -O " + datoteka + " " + link)

            except HTTPError, e:
                print "HTTP Error:", e.code, self.__url
            except URLError, e:
                print "URL Error:", e.reason, self.__url

    def __format_relative_path(self, image):
        # get url for each image
        self.url = image
        # get each image's name
        self.imeSlike = image.rsplit('/', 1)
        self.imeSlike = self.imeSlike[1]
        self.s = self.imeSlike
        # write in html each image url as local path (relative)
        # self.dir2 = "file:///"
        self.dir2 = self.dir3
        self.dir2 += "\\"
        self.dir2 = self.dir2.replace("\\", "/")
        self.dir2 += self.s
        self.s = self.dir2
        # cut extension from image name
        self.s = self.s.split('.')

    def __relative_path(self, image):
        if ('jpg' in self.s[1]) or ('jpeg' in self.s[1]):
            self.s = self.s[0]
            self.s += '.jpg'
            # put local path with image name to html as tag source of image
            image['src'] = self.s
            # same as above, slice any text after extension
            self.imeSlike = self.imeSlike.rsplit('jpg', 1)
            self.imeSlike = self.imeSlike[0]
            self.imeSlike += 'jpg'
            # save image to local folder
            # self.__fetchImages(str(self.imeSlike), self.url, "b")
            self.__fetchimages(str(self.imeSlike), self.url)

        # if image is gif format
        elif 'gif' in self.s[1]:
            self.s = self.s[0]
            self.s += '.gif'
            # put local path with image name to html as tag source of image
            image['src'] = self.s
            # same as above, slice any text after extension
            self.imeSlike = self.imeSlike.rsplit('gif', 1)
            self.imeSlike = self.imeSlike[0]
            self.imeSlike += 'gif'
            # save image to local folder
            # self.__fetchImages(str(self.imeSlike), self.url, "b")
            self.__fetchimages(str(self.imeSlike), self.url)

    def __saveimg(self, stranica, num):
        # search for images in html
        for image in stranica.find_all('img'):
            if ((image.get('data-img') is not None and image.get('data-img') != "") and (num == 1)) or (
                (image.get('data-img') is not None and image.get('data-img') != "") and (
                    image.get('data-img') != self.header.get('data-img')) and (num == 2)):
                # remove description of each image
                self.desc = image.find_next_siblings('font')
                if len(self.desc) == 2:
                    self.desc[0].decompose()

                self.__format_relative_path(image.get('data-img'))
                self.__relative_path(image)

            elif ((image.get('src') is not None) and (num == 1)) or (
                    (image.get('src') is not None) and (image.get('src') != self.header.get('src')) and (
                        num == 2)):
                # remove description of each image
                self.desc = image.find_next_siblings('font')
                if len(self.desc) == 2:
                    self.desc[0].decompose()

                self.__format_relative_path(image.get('src'))
                self.__relative_path(image)

        # remove header image
        if num == 2:
            self.img = stranica.find('img')
            if self.img is not None:
                self.img.decompose()

    def __fetch_authors(self, authors):
        for author in authors:
            # if string authors don't have apostrophe add opening
            if self.authors.find('"') == -1:
                self.authors += '"'
            # concate each author following with comma
            self.authors += author.get_text()
            # if that's last author, add closing apostrophe
            if author.get_text().find(',') == -1:
                self.authors += '"'

        if self.authors.count('"') == 1:
            self.authors += '"'

    def __create_directory(self):
        # get working directory and add backslash to it
        self.dir = os.getcwd() + '/'
        # in the name of the article replace spaces with _
        self.dir += str(self.name.replace(" ", "_"))
        # create folder in the working dir with the name of article
        os.makedirs(self.dir)
        # change working dir to newly created folder
        os.chdir(self.dir)

    def save_images(self):
        self.__create_directory()

        # create relative path to directory for html src images tag
        self.dir3 = str(self.name.replace(" ", "_"))

        # get header picture so it can be removed on second page
        self.header = self.html.find('img')

        # get authors of article
        # authors
        # each author is element with byline class
        self.__fetch_authors(self.html.find(class_=re.compile("meta"))
                             .findAll(class_=re.compile("byline")))

        self.__saveimg(self.html, 1)

        if self.page2:
            self.__saveimg(self.html2, 2)

    def save_webpage(self):
        # return up one folder
        os.chdir(os.path.dirname(self.dir))
        self.epub = self.name
        # join epub format to article name
        self.epub += '.epub'
        # join html format to article name
        self.name += '.html'
        # save html file locally
        self.output = open(self.name, "a")
        self.output.write((str(self.html)))

        codecs.register(lambda name: codecs.lookup('utf-8') if name == 'cp65001' else None)

        if self.page2:
            self.output.write(str(self.html2))

        self.output.write(Cracked.__style)
        self.output.close()

        print ('\n' + self.name + '\n')

    def converttoepub(self):
        # command line arguments
        # self.convertArg =
        # '"' + self.name + '"' + ' ' + '"'
        # + self.epub + '"' + ' --toc-threshold 50
        # --max-toc-links 0 --level1-toc //h:h1 --level2-toc //h:h2
        # --no-default-epub-cover --language English
        # --authors ' + self.authors + ' --extra-css stylesheet.css''
        self.convertArg = '"' + self.name + '"' + ' ' + '"' + self.epub + '"' + \
                          ' --toc-threshold 50 --max-toc-links 0 ' \
                          '--level1-toc //h:h1 --level2-toc //h:h2 ' \
                          '--no-default-epub-cover --language English --authors ' + self.authors
        # run ebook converter with arguments in command line
        os.system("ebook-convert" + " " + self.convertArg.encode('utf8'))
        # remove html
        os.remove(self.name)
        # remove folder with article images
        shutil.rmtree(self.dir)

# if you don't send argument article url on script running you can paste it after from command line
if len(sys.argv) < 2:
    url = raw_input("Unesi web adresu clanka: ")
else:
    url = sys.argv[1]

new_article = Cracked(url)

new_article.fetch_webpage()
new_article.format_page()
new_article.save_images()
new_article.save_webpage()
new_article.converttoepub()