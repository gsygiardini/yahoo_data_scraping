import bs4
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
#import sys
import os

############################################################
my_url="https://br.financas.yahoo.com/portfolio/p_0/view/v1"

uClient = uReq(my_url)
page_html = uClient.read()
uClient.close()

page_soup = soup(page_html, "html.parser")

stock_names=page_soup.findAll("td",{"class":"Va(m)"})

prices=page_soup.findAll("td",{"class":"Va(m) Fz(s) Ta(end) Pstart(20px) Fw(b) Bxz(bb) Miw(85px) "})

vec_size = len(stock_names)
############################################################
j=0
############################################################
#arq = open("stocks.dat","a")

#for i in range(1, int(vec_size/10)):
#	for j in range(0, 8):
#		k=10*i+j
#		print(f"{stock_names[k].text}", file=arq, end='\t')
#	arq.write("\n")

############################################################



############################################################

while j < int(vec_size / 10) :
        l=10*j
        exists = os.path.isfile(str(stock_names[l].text))

        if exists:
                arq = open(str(stock_names[l].text),"a")
        else:
                arq = open(str(stock_names[l].text),"w")
                #arq.write("#Initials \t Name \t price(intraday) \t change \t change(prcnt) \t volume \t avg vol (3 months)  \t market cap \t PE Ratio \t 52 week range\n")


        for i in range(0,8) :
                k=10*j+i
                print(f"{stock_names[k].text}", file=arq, end='\t')
        arq.write("\n")

        arq.close()

        j=j+1

############################################################
