"""
Pulling fire data from NASA website.

Data from current fires is on the page:
https://firms.modaps.eosdis.nasa.gov/active_fire/#firms-txt

"""
import os, pandas as pd, numpy as np, logging, scipy.stats as stats, re, matplotlib.pyplot as plt, math, datetime as dt,statsmodels.api as sm, requests, logging

from io import StringIO
from bs4 import BeautifulSoup as bs

logging.basicConfig(level=logging.INFO)


def process(start_data=r'https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_USA_contiguous_and_Hawaii_24h.csv'):
	"""
	start_data to be sourced from the current fire data on website: https://firms.modaps.eosdis.nasa.gov/active_fire/#firms-txt
	"""
	df=pd.read_csv(StringIO(requests.get(start_data).text))
	return(df)

def coord(raw_val):
	"""
	Take deg min sec and return decimal floating point represenation
	"""
	cleaner=re.split("°|′|″", raw_val)
	clean=0
	for i,j in enumerate(cleaner):
		try:
			if i==0:
				clean+=int(j)
			elif i>0:
				clean+=int(j)/(i*60)
		except ValueError:
			if j==('W' or 'S'):
				clean*=-1
	return(clean)

def cities(number=10):
	"""
	Source data from wikipedia
	Returns a table of top n largest cities in North America with lat and long
	"""
	asd=requests.get(r'https://en.wikipedia.org/wiki/List_of_North_American_cities_by_population')
	example=bs(asd.text, 'html.parser')
	tables=example.find('table',{'class':'wikitable sortable'})
	
	rows=tables.findAll('tr')
	header=[th.text.rstrip() for th in rows[0].find_all('th')]
	header.extend(['url','lat','long'])
	
	list_data=[]
	for row in rows[1:number+1]:
		data=[d.text.rstrip() for d in row.select('td')]
		#logging.info(data)
		asdf=row.find('a')
		if asdf==None:
			data.append('')
		else:
			data.append(asdf['href'])
		#todo follow href and pull coordiantes
		base_page=requests.get(f"http://www.wikipedia.org{asdf['href']}")
		for i in ['latitude','longitude']:
			#logging.info(bs(base_page.text,'html.parser').find('span',{'class':i}).text)
			data.append(coord(bs(base_page.text,'html.parser').find('span',{'class':i}).text))
			#logging.info(data[-1])
		list_data.append(data)
	
	df=pd.DataFrame(list_data, columns=header)
	return(df)

def plotting(df,df_cities):
	plt.scatter(x=df['longitude'],y=df['latitude'],alpha=.4,label='Fire locations')
	plt.scatter(y=df_cities['lat'],x=df_cities['long'],marker='+',color='red',label='Major Cities')
	plt.show(block=False)

if __name__=='__main__':
	df=process()
	df_cities=cities()
	
	plotting(df,df_cities)