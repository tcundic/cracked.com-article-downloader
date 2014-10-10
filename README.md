Cracked.com_article_downloader
==============================

Python script that use BeautifulSoup library to scrap article from input cracked.com url

Requirement:

1. Installed Python 2.7
2. Installed BeautifulSoup library for python
3. (Optional) Installed Calibre for conversion to epub


This script is programmed to scrap article from cracked.com to html and convert it to epub,
but it can be easily modified for other web sites or used as example for own scripts.
If you don't want htmls to be converted to epub, just put last line of code in comment (#new_article.convert())
If you want to batch download multiple articles and/or print output to log file, 
just create bat file like this next example:

(i put directory to python in enviroment variable so i don't need to write whole path to download.bat)


Download.bat

python.exe cracked.py http://www.cracked.com/article_20308_5-insane-strategies-that-won-elections-and-changed-history.html
python.exe cracked.py http://www.cracked.com/blog/6-bizarre-things-that-make-your-memory-worse-than-you-think/


and after that just run that bat from command prompt this way:

C:\Users\userName\download.bat 1> log.txt 2>&1

