# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

def request_return(full_url):
    request = Request(full_url)

    request.get_method = lambda: 'GET'
    response_body = urlopen(request).read()
    response_body = BeautifulSoup(response_body).prettify().encode('utf-8')

    return response_body

def scraping_simsa_by_serial(bill_id):
    # 의안의 심사정보를 갖고온다

    url = "http://likms.assembly.go.kr/bill/billDetail.do?billId="+ bill_id

    source = request_return(url)
    soup = BeautifulSoup(source, 'html.parser')

    Raw_SoGawnSimList = soup.find_all('table', attrs={"summary": " 소관위 심사정보"})
    Raw_SoGawnHList = soup.find_all('table', attrs={"summary": "소관위 회의정보"})
    Raw_BupSaSimList = soup.find_all('table', attrs={"summary": "법사위 체계자구심사정보"})
    Raw_BupSaHList = soup.find_all('table', attrs={"summary": "법사위 회의정보"})
    # Raw_BonSimList = soup.find_all('table', attrs={"summary": "본회의 심의정보"})
    # Raw_JungBuMoveList = soup.find_all('table', attrs={"summary": "정부이송정보"})
    # Raw_GongPoList = soup.find_all('table', attrs={"summary": "공포정보의 공포일자, 공포번호, 공포법률 정보"})
    sogawnsimdictlist = SoGawnSim(Raw_SoGawnSimList)
    sogawnhdictlist = SoGawnH(Raw_SoGawnHList)
    bupsasimdictlist = BupSaSim(Raw_BupSaSimList)
    bupsahdictlist = BupSaH(Raw_BupSaHList)

    y = [ ]
    y.append(sogawnsimdictlist)
    y.append(sogawnhdictlist)
    y.append(bupsasimdictlist)
    y.append(bupsahdictlist)

    return (bill_id, y)[1]

def SoGawnSim(Raw_SoGawnSim):
    #print Raw_SoGawnSim

    SoGawnSimList = []

    # Raw_SoGawnSim
    for data in Raw_SoGawnSim:
        trs = data.tbody.find_all("tr")
        for tr in trs:

            tdata = tr.find_all("td")

            name = tdata[0].get_text().replace("\n", "").strip(" ")
            submitdt = tdata[1].get_text().replace("\n", "").strip(" ")
            presentdt = tdata[2].get_text().replace("\n", "").strip(" ")
            procdt = tdata[3].get_text().replace("\n", "").strip(" ")
            procresultcd = tdata[4].get_text().replace("\n", "").strip(" ")

            atags = tdata[5].find_all('a')

            #files = []
            #for atag in atags:
            #    url = get_atag_inSoGawnSim(atag)
            #    print url
            #    files.append(url)

            one = {
                "committeename": "", "docname1": "", "docname2": "", "hwpurl1": "", "hwpurl2": "", "pdfurl1": "",
                "pdfurl2": "",
                "presentdt": "", "procdt": "", "procresultcd": "", "submitdt": "", "title": "소관위심사정보"
            }

            one["committeename"] = name
            one["submitdt"] = submitdt
            one["presentdt"] = presentdt
            one["procdt"] = procdt
            one["procresultcd"] = procresultcd

            SoGawnSimList.append(one)
    return SoGawnSimList
def get_atag_inSoGawnSim(atag):
    atag_str = str(atag)

    startp = atag_str.find("http://")
    endp = atag_str.find("FileGate") + 8

    base = atag_str[startp:endp]

    bookId = atag_str[endp + 3:]
    bookIde = bookId.find("'")
    book_type = bookId[bookIde + 3:bookIde + 4]
    bookId = bookId[:bookIde]

    url = base + "?bookId=" + bookId + "&type=" + book_type

    return url
def SoGawnH(Raw_SogawnH):

    SoGawnHList = []

    # Raw_SoGawnSim
    for data in Raw_SogawnH:
        trs = data.tbody.find_all("tr")
        for tr in trs:
            tdata = tr.find_all("td")

            name = tdata[0].get_text().replace("\n", "").strip(" ")
            confdt = tdata[1].get_text().replace("\n", "").strip(" ")
            confresult = tdata[2].get_text().replace("\n", "").strip(" ")

            one = {"confdt": "", "confname": "", "confresult": "", "fileurl": "", "title": "소관위회의정보"}

            one["confname"] = name
            one["confdt"] = confdt
            one["confresult"] = confresult
            one["fileurl"] = ""

            SoGawnHList.append(one)

    return SoGawnHList
def BupSaSim(Raw_Bupsasim):

    bupsimList = []

    # Raw_SoGawnSim
    for data in Raw_Bupsasim:
        trs = data.tbody.find_all("tr")
        for tr in trs:
            tdata = tr.find_all("td")

            submitdt = tdata[0].get_text().replace("\n", "").strip(" ")
            presentdt = tdata[1].get_text().replace("\n", "").strip(" ")
            procdt = tdata[2].get_text().replace("\n", "").strip(" ")
            procresultcd = tdata[3].get_text().replace("\n", "").strip(" ")

            one = {"hwpurl": "", "pdfurl": "", "presentdt": "", "procdt": "", "procresultcd": "", "submitdt": "",
                   "title": "법사위심사정보"}

            one["presentdt"] = presentdt
            one["procdt"] = procdt
            one["procresultcd"] = procresultcd
            one["submitdt"] = submitdt

            bupsimList.append(one)

    return bupsimList
def BupSaH(Raw_Bupsah):

    buphList = []

    # Raw_SoGawnSim
    for data in Raw_Bupsah:
        trs = data.tbody.find_all("tr")
        for tr in trs:
            tdata = tr.find_all("td")

            confname = tdata[0].get_text().replace("\n", "").strip(" ")
            confdt = tdata[1].get_text().replace("\n", "").strip(" ")
            confresult = tdata[2].get_text().replace("\n", "").strip(" ")

            one = {"confdt": "", "confname": "", "confresult": "", "fileurl": "", "title": "법사위회의정보"}

            one["confdt"] = confdt
            one["confname"] = confname
            one["confresult"] = confresult

            buphList.append(one)
    return buphList
def BonSim(soup):
    pass
def BonH(soup):
    pass