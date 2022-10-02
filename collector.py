import bs4
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from selenium import webdriver
import time
import os
import sqlite3
import numpy as np
import matplotlib
import matplotlib.pyplot as pl
import math

from datetime import date
from datetime import datetime

from tkinter import *
from tkinter.ttk import *

def declaring():
    global incr
    incr = 6

def TkinterGui():
    root = Tk()
    root.title("Bolsa de Valores")
    childWindows = []

    global company
    global entryCompany
    Label(root, text="Digite o Nome da Empresa").grid(row=1, column=1)
    entryCompany = Entry(root, width=30)
    entryCompany.grid(row=1,column=3)
    entryCompany.insert(END, "AMD")
    company = str(entryCompany.get())

    global iniDate
    Label(root, text="Data Inicial (31/04/2020)").grid(row=2, column=1)
    entryIniDate = Entry(root, width=30)
    entryIniDate.grid(row=2,column=3)
    entryIniDate.insert(END, "01/01/2019")
    iniDate = (entryIniDate.get())

    global finDate
    Label(root, text="Data Final (31/06/2020)").grid(row=3, column=1)
    entryFinDate = Entry(root, width=30)
    entryFinDate.grid(row=3,column=3)
    today = date.today()
    today = today.strftime("%d/%m/%Y")
    entryFinDate.insert(END, today)
    finDate = (entryFinDate.get())

    global interval
    Label(root, text="Intervalo Entre Preços").grid(row=4, column=1)
    entryInterval = Entry(root, width=30)
    entryInterval.grid(row=4,column=3)
    entryInterval.insert(END, "1d")
    interval = str(entryInterval.get())

    global frequency
    Label(root, text="Frequência dos Preços").grid(row=5, column=1)
    entryFrequency = Entry(root, width=30)
    entryFrequency.grid(row=5,column=3)
    entryFrequency.insert(END, "1d")
    frequency = str(entryFrequency.get())

    global dataBase
    Label(root, text="Caminho da Base de Dados").grid(row=6, column=1)
    entryDataBase = Entry(root, width=30)
    entryDataBase.grid(row=6,column=3)
    entryDataBase.insert(END, "./DataBase/companies.db")
    dataBase = entryDataBase.get()

    scrapingButton = Button(root, text = "Varrer Internet", command=multiplePagesScraping)
    scrapingButton.grid(row=7, column=3)

    msdButton = Button(root, text = "Obter o MSD", command=msd)
    msdButton.grid(row=8, column=3)

    global companyMSD
    Label(root, text="Coloque a Empresa que Deseja Obter o MSD").grid(row=9, column=1)
    entryCompanyMSD = Entry(root, width=30)
    entryCompanyMSD.grid(row=9, column=3)
    entryCompanyMSD.insert(END, "AMD")
    companyMSD = str(entryCompanyMSD.get())

    markowitzButton = Button(root, text = "Obter a Carteira de Markowitz", command=markowitz)
    markowitzButton.grid(row=10, column=3)

    global expectedReturn
    Label(root, text="Retorno Esperado para o Portifólio de Markowitz").grid(row=11, column=1)
    entryExpectedRet = Entry(root, width=30)
    entryExpectedRet.grid(row=11, column=3)
    entryExpectedRet.insert(END, 0.1)
    expectedReturn = entryExpectedRet.get()

    def updateVariables():
        global iniDate, finDate, interval, frequency, dataBase, companyMSD, expectedReturn
        iniDate = (entryIniDate.get())
        finDate = (entryFinDate.get())
        interval = str(entryInterval.get())
        frequency = str(entryFrequency.get())
        dataBase = entryDataBase.get()
        companyMSD = str(entryCompanyMSD.get())
        expectedReturn = entryExpectedRet.get()

    updateButton = Button(root, text="Atualizar as Variáveis de Entrada", command=updateVariables)
    updateButton.grid(row=12,column=3)

    root.update()
    root.mainloop()

def dataScrape(company):
    print("Getting HTML code from web page...")

    standardLink = "https://finance.yahoo.com/quote/COMPANY/history?period1=INITIALDATE&period2=FINALDATE&interval=INTERVAL&filter=history&frequency=FREQUENCY"
    aux = standardLink.replace("COMPANY",company)
    aux = aux.replace("INITIALDATE",str(int(convertDate(iniDate))))
    aux = aux.replace("FINALDATE",str(int(convertDate(finDate))))
    aux = aux.replace("INTERVAL",interval)
    link = aux.replace("FREQUENCY",frequency)

    print(link)

    os.environ['MOZ_HEADLESS'] = '1'
    driver = webdriver.Firefox()
    try:
        driver.get(link)
    except:
        print("Couldn't get company name")
        return False

    currentHeight = driver.execute_script("return window.scrollY")
    while True:
        oldCurrentHeight = currentHeight
        for i in range(1,10):
            driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
        time.sleep(0.5)
        currentHeight = driver.execute_script("return window.scrollY")
        if oldCurrentHeight==currentHeight:
            break

    html = None
    html = driver.page_source

    driver.close()
    driver.quit()

    print("Done...")
    print("Processing obtained HTML code...")

    page_html = html
    page_soup = soup(page_html, "html.parser")

    companyHtmlCode = page_soup.findAll("h1",{"class":"D(ib)"})
    try:
        companyName = companyHtmlCode[0].text
        print(companyName)
    except:
        print("!!!NO DATA FOUND... Input:"+company)
        return False

    date = page_soup.findAll("td",{"class":"Py(10px) Ta(start) Pend(10px)"})
    for i in range(0,len(date)):
        date[i] = date[i].text

    prices = page_soup.findAll("td",{"class":"Py(10px) Pstart(10px)"})

    opn = []
    high = []
    low = []
    close = []
    adjClose = []
    volume = []

    for i in range(0,len(prices),incr):
        aux = str(prices[i].text)
        opn.append(aux.replace(",",""))
        aux = str(prices[i+1].text)
        high.append(aux.replace(",",""))
        aux = str(prices[i+2].text)
        low.append(aux.replace(",",""))
        aux = str(prices[i+3].text)
        close.append(aux.replace(",",""))
        aux = str(prices[i+4].text)
        adjClose.append(aux.replace(",",""))
        aux = str(prices[i+5].text)
        volume.append(aux.replace(",",""))

    print("Done...")
    print("Saving processed data...")

    connection = None
    try:
        connection = sqlite3.connect(dataBase)
        cursor = connection.cursor()
    except:
        print("Couldn't open database...")

    with connection:
        cursor.execute("CREATE TABLE IF NOT EXISTS companies (companyId INTEGER PRIMARY KEY, nome TEXT)")
        fetchCompanies = "SELECT nome FROM companies"
        connection.commit()
        cursor.execute(fetchCompanies)
        connection.commit()
        companies = np.asarray(cursor.fetchall()).flatten()

        print(companies)

        createFile=True
        for i in range(0,len(companies)):
            createFile=True
            if company==companies[i]:
                print("Company already exists in database")
                createFile=False
                cursor.execute("SELECT rowid FROM companies WHERE nome = (?)",[company])
                connection.commit()
                idArray = np.asarray(cursor.fetchall()).flatten()
                companyId = str(idArray[0])
                break

        if createFile==True:
            print("Creating new company table")
            createFile=True
            cursor.execute("INSERT INTO companies(nome) VALUES(?);",[company])
            connection.commit()
            idArray = np.asarray(cursor.lastrowid).flatten()
            companyId = str(idArray[0])

    connection.close()
    connection = None

    companyDbFile = "./DataBase/" + companyId + ".db"
    try:
        connection = sqlite3.connect(companyDbFile)
        cursor = connection.cursor()
    except:
        print("Couldn't open database...")

    with connection:
        cursor.execute("CREATE TABLE IF NOT EXISTS history (data TEXT,open FLOAT,high FLOAT,low FLOAT,close FLOAT,adjClose FLOAT,volume FLOAT)")
        connection.commit()
        lengthList = [len(date),len(opn),len(high),len(low),len(close),len(adjClose),len(volume)]

        for i in range(0,min(lengthList)):
            if opn[i]=="-":
                break
            else:
                cursor.execute(" INSERT INTO history(data,open,high,low,close,adjClose,volume) VALUES (?,?,?,?,?,?,?) ",(date[i],opn[i],high[i],low[i],close[i],adjClose[i],volume[i]))
                connection.commit()

    connection.close()
    print("Done...")

####################################################################################################################################################################################
def multiplePagesScraping():
    company = str(entryCompany.get())

    multipleCompanies = company.find(",")
    if multipleCompanies==-1:
        dataScrape(company)
    else:
        companiesList = company.split(",")

        for i in range(0,len(companiesList)):
            dataScrape(companiesList[i])

####################################################################################################################################################################################
def msd():
    connection = None
    try:
        connection = sqlite3.connect(dataBase)
        cursor = connection.cursor()
    except:
        print("Couldn't open database...")

    with connection:
        print(companyMSD)
        print(dataBase)
        cursor.execute("SELECT rowid from companies WHERE nome=(?)",[companyMSD])
        connection.commit()
        idList = np.asarray(cursor.fetchall()).flatten()
        print(idList)
        try:
            id = str(idList[0])
        except:
            print("Couldn't get data...")
            return False

    connection = None

    fileName = "./DataBase/" + id + ".db"
    try:
        connection = sqlite3.connect(fileName)
        cursor =  connection.cursor()
    except:
        print("Couldn't open database...")

    with connection:
        cursor.execute("SELECT data from history")
        unformatedDate = np.asarray(cursor.fetchall()).flatten()
        cursor.execute("SELECT open from history")
        opn = np.asarray(cursor.fetchall()).flatten()
        cursor.execute("SELECT high from history")
        high = np.asarray(cursor.fetchall()).flatten()
        cursor.execute("SELECT low from history")
        low = np.asarray(cursor.fetchall()).flatten()
        cursor.execute("SELECT close from history")
        close = np.asarray(cursor.fetchall()).flatten()
        cursor.execute("SELECT adjClose from history")
        adjClose = np.asarray(cursor.fetchall()).flatten()
        cursor.execute("SELECT volume from history")
        volume = np.asarray(cursor.fetchall()).flatten()

    date = []
    for i in range(0,len(unformatedDate)):
        date.append((unformatedDate[i]))

    MSD = []
    for i in range(0,len(date)):
        sum = 0
        for j in range(0,len(date)-i):
            sum = sum + (opn[i+j] - opn[j])**2
        MSD.append(sum/len(date))

    connection = None
    try:
        fileName = "./DataBase/" + id + "_msd.db"
        connection = sqlite3.connect(fileName)
        cursor = connection.cursor()
    except:
        print("Couldn't create or connect to database...")

    cursor.execute("CREATE TABLE IF NOT EXISTS meanSquareDisp(timeId INTEGER PRIMARY KEY,t INTEGER,msd FLOAT)")

    for i in range(0,len(date)):
        cursor.execute("INSERT INTO meanSquareDisp(t,msd) VALUES (?,?)",(i,MSD[i]))
        connection.commit()
        #print(i,MSD[i])

    print("Done...")
####################################################################################################################################################################################
def markowitz():
    connection = sqlite3.connect(dataBase)
    cursor = connection.cursor()

    cursor.execute("SELECT companyId FROM companies")
    connection.commit()
    companyIds = np.asarray(cursor.fetchall()).flatten()
    cursor.execute("SELECT nome FROM companies")
    connection.commit()
    companies = np.asarray(cursor.fetchall()).flatten()


    print(companyIds)

    opn = []
    for i in range(0,len(companyIds)):
        opn.append([])
        fileName = "./DataBase/" + str(companyIds[i]) + ".db"
        auxConnection = sqlite3.connect(fileName)
        auxCursor = auxConnection.cursor()

        auxCursor.execute("SELECT open FROM history")
        opn[i] = (np.asarray(auxCursor.fetchall()).flatten())
    opn = np.asarray(opn)

    timeSpan = []
    for i in range(0,len(companyIds)):
        timeSpan.append(len(opn[i]))

    minimalTimeSpan = min(timeSpan)
    returns = []
    for i in range(0,len(companyIds)):
        returns.append([])
        for j in range(1,minimalTimeSpan-1):
            try:
                returns[i].append((float(opn[i][j])-float(opn[i][j-1]))/float(opn[i][j-1]))
            except:
                print(i)
            #print((float(opn[i][j])-float(opn[i][j-1]))/float(opn[i][j-1]))
        returns[i] = np.asarray(returns[i])

    m = 0
    alpha0 = float(expectedReturn)
    # alpha0 = 0.1
    returns = np.asarray(returns)
    M = [[],[]]

    S = np.cov(returns)
    print(S)
    I = np.ones((len(returns),1))

    invS = np.linalg.inv(S)

    alpha = []
    for i in range(0,len(returns)):
        alpha.append(sum(returns[i]))

    m_11 = float(np.matmul(np.matmul(alpha,np.linalg.inv(S)),np.transpose(alpha)))
    m_12 = float(np.matmul(np.matmul(alpha,np.linalg.inv(S)),I))
    m_21 = m_12
    m_22 = float(np.matmul(np.matmul(np.transpose(I),np.linalg.inv(S)),I))

    M[0].append(m_11)
    M[0].append(m_12)
    M[1].append(m_21)
    M[1].append(m_22)

    lamb = (M[0][0]-M[0][1]*alpha0)*(1.0/(M[0][0]*M[1][1] - M[0][1]*M[1][0]))
    mu   = (M[1][1]*alpha0-M[0][1])*(1.0/(M[0][0]*M[1][1] - M[0][1]*M[1][0]))

    w0 = lamb*np.matmul(np.linalg.inv(S),I).flatten() + mu*np.matmul(np.linalg.inv(S),alpha)
    sigma = np.matmul(np.matmul(np.transpose(w0),S),w0)

    stockRisk = np.matmul(S,I)
    stockReturn = np.matmul(alpha,w0)

    x = np.arange(-100,100)
    y = (M[1][1]*x**2 - 2.0*M[0][1]*x + M[0][0])*(1.0/(M[0][0]*M[1][1] - M[0][1]*M[1][0]))

    pl.xlabel('$\\sigma^2$')
    pl.ylabel('$\\alpha_0$')

    pl.plot(y,x,label='Fronteira Eficiente')

    for m in range(0,len(returns)):
        pl.plot(stockRisk[m], alpha[m] ,'o',  label=companies[m], markersize='10')
    pl.legend()
    pl.show()

    pl.xlabel('t')
    pl.ylabel('$\\alpha_0$')
    #pl.xscale("log")
    #pl.yscale("log")

    for m in range(0,len(returns)):
        pl.plot(returns[m], label=companies[m])
        pl.legend()
    pl.show()

    print("Done...")



def convertDate(date):
    firstDate = datetime(1970,1,1).date()
    date = str(date)
    date = date.replace(",","")
    date = datetime.strptime(str(date),"%d/%m/%Y").date()
    return (date-firstDate).total_seconds()

declaring()
TkinterGui()
