import logging
import math

from misaka import Markdown, HtmlRenderer
from lxml.html import fromstring

def make_logger(logger_name, logfile, loggin_level=logging.DEBUG):
	logger = logging.getLogger(logger_name)
	logger.setLevel(loggin_level)
	
	formatter = logging.Formatter('%(levelname)s - %(name)s - %(asctime)s - %(message)s', '%Y-%m-%d %H:%M:%S')
	
	fh = logging.FileHandler(logfile)
	fh.setLevel(loggin_level)
	fh.setFormatter(formatter)
	ch = logging.StreamHandler()
	ch.setFormatter(formatter)
	
	logger.addHandler(fh)
	logger.addHandler(ch)
	return logger

def get_text_from_markdown(markdown_text):
	renderer = HtmlRenderer()
	markdown = Markdown(renderer, extensions=('tables', 'autolink', 'strikethrough', 'quote', 'superscript', 'fenced-code'))
	html = markdown(markdown_text)
	parsed_html = fromstring(html)
	
	# remove quoted text
	[x.getparent().remove(x) for x in parsed_html.xpath('//blockquote')]
	
	# remove automatically added links 
	for link in parsed_html.xpath('//a'):
		if link.text_content() == link.get('href'):			 
			link.getparent().remove(link)
	
	text = ''.join(parsed_html.text_content()).strip()
	return text

# https://stackoverflow.com/a/3155023
millnames = ['',' thousand',' million',' billion',' trillion']
def human_readable_download_number(download_number_string):
	download_number_string = download_number_string.split("-")[0].replace(',','').replace('+','').strip()
	n = float(download_number_string)
	millidx = max(0,min(len(millnames)-1,
		int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))
	
	return '{:.0f}{}'.format(n / 10**(3 * millidx), millnames[millidx])