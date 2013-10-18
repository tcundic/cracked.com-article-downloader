#!/usr/bin/env python

import re
import urllib2
import sys
from bs4 import BeautifulSoup
from weasyprint import HTML
import os
from urllib2 import Request, urlopen, URLError, HTTPError
import codecs

class Cracked(object):
	def __init__(self, url):
		
		self.url = url
		
		#after download put style to html
		Cracked.__style = """
		<style>
			.body {text-align:justify;
					margin-left: 5%;
					margin-right: 5%;
					}

			h1, h2, h3 	{text-align:center;}
			footer	{text-align:center;}
			img	{display:block;
				margin-left: auto;
				margin-right: auto;
				margin-bottom: 30px;
				margin-top: 30px;
				}
		</style>"""

	def fetch_webPage(self):
		self.page1 = urllib2.urlopen(self.url)
		#first script asume that arcticle have two web pages
		self.page2 = True
		self.page = BeautifulSoup(self.page1)
		
		#try to find link to article second page
		try:
			self.page1 = urllib2.urlopen(self.page.find("a", {"class" : "next"}).get('href'))
		except:
			self.page2 = False #article is one page (blog or quick-fix)

	def format_page(self):
		#if article is on two pages
		if(self.page2):
			#find title of article
			self.h1 = self.page.find('h1')
			#after that find parent of h1 tag, that mean find body of article
			self.html = self.h1.find_parent(attrs={"class": "body"})
			
			#remove all elements with class that have "social" in name
			#remove (add to favorites, share on twitter, facebok etc.)
			for social in self.html.find_all(class_=re.compile("social")):
				social.decompose()
			
			#script will merge two paged article in one html so remove html element with links to article next/prev page(just see any cracked.com article)
			self.pagination = self.html.find(class_=re.compile("Pagination"))
			if (self.pagination != None):
				self.pagination.decompose()
			
			#remove any video from article
			for video in self.html.find_all('iframe'):
				video.decompose()
			
			#remove any video from article
			for video in self.html.find_all('object'):
				video.decompose()
			
			#get article name
			self.name = self.html.find('h1').get_text()
			
			#get article second page
			self.page = BeautifulSoup(self.page1)
			
			self.h1 = self.page.find('h1')
			self.html2 = self.h1.find_parent(attrs={"class": "body"})
			
			#remove article title so it doesn't repeat
			self.naslov = self.html2.find('h1').decompose()
			
			#same as before
			for social in self.html2.find_all(class_=re.compile("social")):
				social.decompose()
				
			self.pagination = self.html2.find(class_=re.compile("Pagination"))
			if (self.pagination != None):
				self.pagination.decompose()
			
			#remove metadata of article(author, date, views so it doesn't repeat)
			self.meta = self.html2.find(class_=re.compile("meta"))
			if (self.meta != None):
				self.meta.decompose()
			
			for video in self.html2.find_all('iframe'):
				video.decompose()

			for video in self.html2.find_all('object'):
				video.decompose()

			self.html.prettify("utf-8")
			self.html2.prettify("utf-8")

		if(self.page2 == False):
			#if article have only one page
			self.h1 = self.page.find('h1')
			self.html = self.h1.find_parent(attrs={"class": "body"})
			
			for social in self.html.find_all(class_=re.compile("social")):
				social.decompose()
			
			self.pagination = self.html.find(class_=re.compile("pagin"))
			if (self.pagination != None):
				self.pagination.decompose()
			
			for video in self.html.find_all('iframe'):
				video.decompose()

			for video in self.html.find_all('object'):
				video.decompose()
						
			self.name = self.html.find('h1').get_text()
			
	def __fetchImages(self, datoteka, link, mode):
		#get image url
		self.__url = link
		self.__req = Request(self.__url)
		
		#save image locally from url
		try:
			self.dat = urlopen(self.__req)
			self.lokalna_slika = open(datoteka, "w" + mode)
			self.lokalna_slika.write((self.dat.read()))
			self.lokalna_slika.close()

		except HTTPError, e:
			print "HTTP Error:", e.code, self.__url
		except URLError, e:
			print "URL Error:", e.reason, self.__url

	def save_images(self):
		#get working directory and add backslash to it
		self.dir = os.getcwd() +'\\'
		#in the name of the article replace spaces with _
		self.dir += str(self.name.replace(" ", "_"))
		#create folder in the working dir with the name of article
		os.makedirs(self.dir)
		
		#change working dir to newly created folder
		os.chdir(self.dir)
	
		#search for images in html
		for image in self.html.findAll('img'):
			if(image.get('src') != ""):
				#get url for each image
				self.url = image.get('src')
				#get each image's name
				self.imeSlike = image.get('src').rsplit('/', 1)
				self.imeSlike = self.imeSlike[1]
				self.s = self.imeSlike
				#write in html each image url as local path
				self.dir2 = "file:///"
				self.dir2 += self.dir
				self.dir2 += "\\"
				self.dir2 = self.dir2.replace("\\", "/")
				self.dir2 += self.s
				self.s = self.dir2
				#cut extension from image name
				self.s = self.s.split('.')
				if ('jpg' in self.s[1]) or ('jpeg' in self.s[1]):
					self.s = self.s[0]
					self.s += '.jpg'
					#put local path with image name to html as tag source of image
					image['src'] = self.s
					#same as above, slice any text after extension
					self.imeSlike = self.imeSlike.rsplit('jpg',1)
					self.imeSlike = self.imeSlike[0]
					self.imeSlike += 'jpg'
					#save image to local folder
					self.__fetchImages(str(self.imeSlike), self.url, "b")
				
				#if image is gif format
				elif 'gif' in self.s[1]:
					self.s = self.s[0]
					self.s += '.gif'
					#put local path with image name to html as tag source of image
					image['src'] = self.s
					#same as above, slice any text after extension
					self.imeSlike = self.imeSlike.rsplit('gif',1)
					self.imeSlike = self.imeSlike[0]
					self.imeSlike += 'gif'
					#save image to local folder
					self.__fetchImages(str(self.imeSlike), self.url, "b")

		if (self.page2):
			for image in self.html2.findAll('img'):
				if(image.get('src') != ""):
					self.url = image.get('src')
					#get each image's name
					self.imeSlike = image.get('src').rsplit('/', 1)
					self.imeSlike = self.imeSlike[1]
					self.s = self.imeSlike
					#write in html each image url as local path
					self.dir2 = "file:///"
					self.dir2 += self.dir
					self.dir2 += "\\"
					self.dir2 = self.dir2.replace("\\", "/")
					self.dir2 += self.s
					self.s = self.dir2
					self.s = self.s.split('.')
					if ('jpg' in self.s[1]) or ('jpeg' in self.s[1]):
						self.s = self.s[0]
						self.s += '.jpg'
						#put local path with image name to html as tag source of image
						image['src'] = self.s
						#same as above, slice any text after extension
						self.imeSlike = self.imeSlike.rsplit('jpg',1)
						self.imeSlike = self.imeSlike[0]
						self.imeSlike += 'jpg'
						#save image to local folder
						self.__fetchImages(str(self.imeSlike), self.url, "b")

					elif 'gif' in self.s[1]:
						self.s = self.s[0]
						self.s += '.gif'
						#put local path with image name to html as tag source of image
						image['src'] = self.s
						#same as above, slice any text after extension
						self.imeSlike = self.imeSlike.rsplit('gif',1)
						self.imeSlike = self.imeSlike[0]
						self.imeSlike += 'gif'
						#save image to local folder
						self.__fetchImages(str(self.imeSlike), self.url, "b")

	def save_WebPage(self):
		#return up one folder
		os.chdir(os.path.dirname(self.dir))
		self.epub = self.name
		#join epub format to article name
		self.epub += '.epub'
		#join html format to article name
		self.name += '.html'
		#save html file locally
		self.output = open(self.name, "a")
		self.output.write((str(self.html)))

		codecs.register(lambda name: codecs.lookup('utf-8') if name == 'cp65001' else None)

		if(self.page2):
			self.output.write(str(self.html2))

		self.output.write(Cracked.__style)
		self.output.close()

		print ('\n' + self.name + '\n')
	
	def convertToEpub(self):
		#command line arguments
		self.convertArg = '"' + self.name + '"' + ' ' + '"' + self.epub + '"' + ' --embed-font-family calibri --toc-threshold 50 --max-toc-links 0 --level1-toc //h:h1 --level2-toc //h:h2 --no-default-epub-cover --language English'
		#run ebook converter with arguments in command line
		os.system("ebook-convert.exe" + " " + self.convertArg)

#if you don't send argument article url on script running you can paste it after from command line
if(len(sys.argv) < 2):
	url = raw_input("Unesi web adresu clanka: ")
else:
	url = sys.argv[1]

new_article = Cracked(url)

new_article.fetch_webPage()
new_article.format_page()
new_article.save_images()
new_article.save_WebPage()
new_article.convertToEpub()
