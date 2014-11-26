# -*- coding: utf-8 -*- 
import bs4
import lxml
import lxml.html
import requests
import json

USE_SOUP = False


def parse_func(txt):
	if(USE_SOUP):
		return bs4.BeautifulSoup(txt)
	else:
		return lxml.html.fromstring(txt)


def select_func(self,query):
	#1 [DONE] ogar czy soup dopuszcza select siebie, jeśli nie(najprawdopodobniej), to
	#1 [DONE] trzea zrobić to tak, że opakowujemy go (bierzemy 'parent')
	# 		i potem jedziemy z selectem.
	#2 [DONE] zrobić dobre sel_css(">...")
	#3 [DONE] przepisać i sprawdzić cały kod, żeby się zgadzał z xpathem
	#  [TODO] dodać obsługę senses typu yours, z jakimś ogólnym akapitem na początku
	#  [DONE] dodać support dla dopisków typu infml, fml, etc
	#  [TODO] ogar innych dopisków (offensive, american, british, vulgar,
	#			abbr, euph, etc.) 
	#4 ew. koniec query typu txt i to jakoś jeszcze... (ale raczej nie)
	id_obscure = "asdfgh1234"
	while query[0] == ' ':
		query = query[1:]
	if(USE_SOUP):
		if(query[0] != '>'):
			return self.select(query)
		else:
			tmp_id = None
			if 'id' in self.attrs:
				tmp_id = self.attrs['id']
			self.attrs['id'] = id_obscure
			# tutaj jest "parent", bo wygląda na to, że nie można zaznaczyć samego siebie
			res = self.parent.select("#"+id_obscure+" "+query)
			if tmp_id:
				self.attrs['id'] = tmp_id
			else:
				del self.attrs['id']
			return res
	else:
		#TODO: precompiling queries and caching them in some dict
		if(query[0] != '>'):
			return self.cssselect(query)
		else:
			tmp_id = None
			if 'id' in self.attrib:
				tmp_id = self.attrib['id']
			self.attrib['id'] = id_obscure
			res = self.cssselect("#"+id_obscure+" "+query)
			if tmp_id:
				self.attrib['id'] = tmp_id
			else:
				del self.attrib['id']
			return res


def map_get_text(li):
	def f(el):
		return el.get_text()
	return map(f,li)

def init():
	if(USE_SOUP):
		bs4.BeautifulSoup.sel_css = select_func
		bs4.element.Tag.sel_css = select_func
	else :
		lxml.html.HtmlElement.sel_css = select_func
		def gettextmethod(self):
			return "".join(self.xpath(".//text()"))
		lxml.html.HtmlElement.get_text = gettextmethod

init()


class DictEntrySense(object):
	
	def __from_html(self, element,ks=[],style_lvl=""):
		#element - div.SENSE-BODY | div.SUB-SENSE-CONTENT
		
		'''
		self.definition = element.xpath(
		"span[@class='DEFINITION']//text()")
		'''
		self.definition = "".join(map_get_text(element.sel_css(" > span.DEFINITION")))
		
		'''
		self.keys = element.xpath("./strong/text() | \
		./span[@class='SENSE-VARIANT']//span[@class='BASE']/text() | \
		./span[@class='MULTIWORD']//span[@class='BASE']/text()")
		'''
		self.keys = element.sel_css(" > strong")
		self.keys += element.sel_css(" > span.SENSE-VARIANT span.BASE")
		self.keys += element.sel_css(" > span.MULTIWORD span.BASE")
		self.keys = map_get_text(self.keys)
		self.keys = self.keys + ks
		
		self.style_level = "".join(map_get_text(element.sel_css(" > span.STYLE-LEVEL")))
		self.style_level += style_lvl
		
		def mk_example(el):
			'''
			fst = el.xpath("./strong//text()")
			fst = "".join(fst)
			'''
			fst = map_get_text(el.sel_css(" > strong"))
			fst = "".join(fst)
			'''
			snd = "".join(el.xpath(".//p//text()"))
			'''
			snd = map_get_text(el.sel_css("p"))
			snd = "".join(snd)
			return (fst,snd)
		'''
		self.examples = map(mk_example, element.xpath("./div[@class='EXAMPLES']"))
		'''
		self.examples = map(mk_example, element.sel_css(" > div.EXAMPLES"))
	
	def __init__(self,inp=None,ks=[],style_lvl=""):
		if inp is not None:
			self.__from_html(inp,ks,style_lvl)
	
	def print_txt(self):
		print self.keys
		print self.style_level
		print self.definition
		print self.examples
		print "___________________\n"



class DictEntry(object):
	
	def from_url(self,url):
		self.senses = []
		page_text = requests.get(url).text
		page_tree = parse_func(page_text)
		#senses:
		'''
		sense_bodies = page_tree.xpath("//ol[@class='senses']//div[@class='SENSE-BODY'] |\
		//ol[@class='senses']//div[@class='SUB-SENSE-CONTENT']")
		'''
		''' nested_sbodies = page_tree.sel_css("ol.senses div.SUB-SENSE-CONTENT") '''
		
		sense_bodies = page_tree.sel_css("ol.senses div.SENSE-BODY")
		
		def get_nested(a):
			return a.sel_css("div.SUB-SENSE-CONTENT")
		nsense_bodies = [ [i]+get_nested(i) for i in sense_bodies]
		# flatten sense_bodies
		sense_bodies = [item for sublist in nsense_bodies for item in sublist]
		self.senses = map(lambda a: DictEntrySense(a) , sense_bodies)
		#related:
		'''
		self.related = page_tree.xpath( \
		"//div[@class='entrylist']//ul//a[@title]")
		'''
		self.related = page_tree.sel_css("div.entrylist ul a[title]")
		def mk_related(el):
			'''
			li = el.xpath(".//span[@class!='PART-OF-SPEECH']/text()")
			return "".join(li)
			'''
			if USE_SOUP:
				return el.attrs['title']
			else:
				return el.attrib['title']
		self.related = map(mk_related, self.related)
		#phrases:
		'''
		phr_list = page_tree.xpath("//div[@id='phrases_container']/ul/li")
		'''
		phr_list = page_tree.sel_css("div#phrases_container > ul > li")
		self.phrases = []
		def mk_phrase(el):
			'''
			phr_names = map(lambda s: "".join(s.xpath(".//text()")) , \
			el.xpath(".//span[@class='BASE']"))
			'''
			# FIXME: może być czasem strong zamiast span.base
			phr_names = map_get_text(el.sel_css("span.BASE"))
			phr_style_level = "".join(map_get_text(el.sel_css(" span.STYLE-LEVEL")))
			'''
			sbodies = el.xpath(".//div[@class='SENSE-BODY']")
			'''
			sbodies = el.sel_css("div.SENSE-BODY")
			sbodies += el.sel_css("div.SUB-SENSE-CONTENT")
			phr_senses = map(lambda a: DictEntrySense(a, phr_names, phr_style_level)
				, sbodies)
			self.phrases = self.phrases + phr_senses
		map(mk_phrase, phr_list)
	
	def __init__(self,url):
		self.from_url(url)
	
	def print_txt(self):
		print "	[[[ self.senses ]]]"
		for i in self.senses:
			i.print_txt()
		print len(self.senses)
		print "	[[[ self.related ]]]"
		print self.related
		print len(self.related)
		print "	[[[ self.phrases ]]]"
		for i in self.phrases:
			i.print_txt()
		print len(self.phrases)

def main():
	words = [
		'take-on', # multiple keys in last sense
		'yours', # big error
		'take off', # informal
		'air', # plural, singular, nested senses
		'reference', # american nested, [only before noun] nested, cntable, uncntable,
		# phrase formal
	]
	page_url = 'http://www.macmillandictionary.com/dictionary/british/reference'
	DictEntry(page_url).print_txt()

main()

'''
interfejs:

class DictEntrySense
	
	keys :: [string]
		dodatkowe uszczegółowienia słowa: np. yours -> Sincerely yours
	
	style_level :: string
		'formal' albo 'informal' albo ''
	
	definition :: string
		definicja słowa w stringu
	
	examples :: [(key :: string, ex :: string)]
		przykłady użycia słowa
		key - dodatkowo uszczegółowione słowo na potrzeby przykładu
		ex - treść przykładu


class DictEntry
	
	senses :: [DictEntrySense]
		znaczenia słowa (bez fraz)
	
	phrases :: [DictEntrySense]
		znaczenia fraz zrobionych z tego słowa
		(jak jakaś fraza ma kilka znaczeń, to każde z
		nich jest na tej liście)
	
	related :: [string]
		slowa/frazy powiązane z danym słowem
	
'''


