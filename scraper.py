from multiprocessing.pool import Pool
import queue
from urllib.request import Request, urlopen
import http
from bs4 import BeautifulSoup
from getSimsa import scraping_simsa_by_serial as getSimsas
import dataprocessing
from collections import OrderedDict
import json
import os
from lxml import html
import codecs
import warnings

PageFlag = 1

warnings.filterwarnings("ignore")


def getListsMultiProcess():

    pp = Pool(processes=10)
    page_idx = 12
    q = queue.Queue()
    result_list = []

    while page_idx >= 1:
        if page_idx - 10 > 0:
            datas = pp.map(getList, list(range(page_idx - 10, page_idx)))
        else:
            datas = pp.map(getList, list(range(1, page_idx)))

        for x in datas:
            if x == None:
                continue
            for xx in x:
                # q.put(xx)
                result_list.append(xx)
        page_idx -= 10

    pp.close()

    # return q
    return result_list

def getLists():
    page_idx = 10
    q = queue.Queue()

    while page_idx >= 1:
        for x in getList(page_idx):
            q.put(x)
        page_idx -= 1
    return q

def getList(page_idx):
    print("[Scraping] 입법예고사이트 page = " + str(page_idx))
    url = 'http://pal.assembly.go.kr/law/endListView.do?tmpAge=20&tmpCurrCommitteeId=&tmpCondition=0&tmpKeyword=&currCommitteeId=&age=20&searchCondition=&searchKeyword=&closedCondition=1&pageNo=' + str(page_idx) if PageFlag == 1 else '"http://pal.assembly.go.kr/law/listView.do?tmpCurrCommitteeId=&tmpCondition=0&tmpKeyword=&currCommitteeId=&searchCondition=&searchKeyword=&closedCondition=0&pageNo='+str(page_idx)
    try:
        source = request_return(url)
    except http.client.HTTPException as e:
        print(e)
        return []

    rows = BeautifulSoup(source).select('tr')[1:-1]

    new_items = []
    for row in rows:
        new_items.append({'id': row.td.text.replace(' ', '').replace('\n', ''),
                          'serial': row.findAll('td')[1].find('a')._attr_value_as_string('onclick')[10:-2]})

    # new_items = soup.get_items_list(0)

    return new_items

def request_return(full_url):
    request = Request(full_url)

    request.get_method = lambda: 'GET'
    response_body = urlopen(request).read()
    response_body = BeautifulSoup(response_body).prettify().encode('utf-8')

    return response_body

#########################

def getOne(serial):

    one = {'serial': serial}
    one['url'] = 'http://pal.assembly.go.kr/law/endReadView.do?lgsltpaId=' + one[
        'serial'] if PageFlag == 1 else 'http://pal.assembly.go.kr/law/readView.do?lgsltpaId=' + one['serial']
    try:
        source = request_return(one['url'])
    except http.client.HTTPException as e:
        print(e)
        return []

    soup = BeautifulSoup(source)

    one['id'] = getId(soup)
    one['title'] = getTitle(soup)
    one['main_footchair'] = getMainfootchair(soup)
    one['proposeday'] = getProposeday(soup)
    one['assos'] = getAssos(soup)
    one['referday'] = getReferday(soup)
    one['pdf'] = getPdf(soup)
    one['hwp'] = getHwp(soup)
    one['summary'] = getSummary(soup)
    one['whocate'] = '의원' if one['main_footchair'] != '정부' else '정부'
    one['status'] = getStatus(one['serial'])
    one['simsas'] = getSimsas(one['serial'])
    one['footchairs'] = getFootchairs(one['serial'])
    one['main_sentence'] = getMainSentence(one['summary'])

    return one

def getId(soup):
    bill_id = soup.select('#con > div.sub_board_w > div.sub_board_title')[0].text

    start = bill_id.find('[') + 1
    end = bill_id.find(']')

    return bill_id[start:end]

def getTitle(soup):
    title = soup.select('#con > div.sub_board_w > div.sub_board_title')[0].text

    start = title.find(']') + 2
    title = title[start:title.find('(') - 1]

    return title

def getMainfootchair(soup):
    mainfootchair = soup.select('#con > div.sub_board_w > table > tr')[1].findAll('td')[0].text.strip()

    if mainfootchair.find('정부') != -1:
        return '정부'

    end = mainfootchair.find(' 등')

    return mainfootchair[:end].replace('의원', '')

def getProposeday(soup):
    proposeday = soup.select('#con > div.sub_board_w > table > tr')[1].findAll('td')[1].text

    return proposeday.replace('\n', '').replace(' ', '')

def getAssos(soup):
    assos = soup.select('#con > div.sub_board_w > table > tr')[1].findAll('td')[2].text

    return assos.replace(' ', '').replace('\n', '')

def getReferday(soup):
    referday = soup.select('#con > div.sub_board_w > table > tr')[1].findAll('td')[3].text

    return referday.replace(' ', '').replace('\n', '')

def getPeriod(soup):
    period = soup.select('#con > div.sub_board_w > table > tr')[1].findAll('td')[4].text

    return period.replace(' ', '').replace('\n', '')

def getPdf(soup):
    try:
        pdf = soup.select('#con > div.sub_board_w > table > tr')[1].findAll('td')[5].findAll('a')[1]._attr_value_as_string('href')
    except:
        pdf = ''

    return pdf

def getHwp(soup):
    try:
        hwp = soup.select('#con > div.sub_board_w > table > tr')[1].findAll('td')[5].findAll('a')[0]._attr_value_as_string('href')
    except:
        hwp = ''

    return hwp

def getSummary(soup):
    return soup.select('#con > div.sub_board_w > div.board_comment > p')[1].text.strip().replace('\n', '<br>')

def getMainSentence(summary):
    subSummaryList = []

    subSummaryList = summary.split('.')

    for targetStr in subSummaryList:
        if targetStr.find('것임') != -1:
            return targetStr

    for targetStr in subSummaryList:
        if targetStr.find('하고자') != -1:
            return targetStr

    return ''

def getStatus(serial):
    url = "http://likms.assembly.go.kr/bill/billDetail.do?billId=" + serial
    response_body = []

    i = 0
    while True:
        if i > 30:
            print("Request Error")
            break
        i += 1

        try:
            request = Request(url)
            request.get_method = lambda: 'GET'
            response_body = urlopen(request).read()
            response_body = BeautifulSoup(response_body)
            response_body = response_body.find_all('span', 'on')
            break
        except Exception as ex:
            response_body = []
            print(ex)
            print("debuging...")
            print(url)

    if response_body == []:
        return (serial, "no status")

    return (serial, response_body[0].get_text())[1]

def getFootchairs(serial):
    url = "http://likms.assembly.go.kr/bill/coactorListPopup.do?billId=" + serial
    try:
        content = BeautifulSoup(request_return(url))
    except http.client.HTTPException as e:
        print(e)
        return []
    members = content.find_all('a')

    res = []
    for member in members:
        data_of_member = member.get_text().strip()
        name = data_of_member[:data_of_member.find("(")]
        party = data_of_member[data_of_member.find("(")+1:data_of_member.find("/")]
        hjname = data_of_member[data_of_member.find("/")+1:-1]
        res.append({"name":name, "party":party, "hjname":hjname})

    return res
#######################

def makeData(target):
    data = getOne(target['serial'])
    data = OrderedDict(data)
    with open((os.getcwd()) + "/result/" + str(data['id']) + ".json", "w", encoding='UTF-8') as make_file:
        json.dump(data, make_file, ensure_ascii=False, indent=3)
    print("[scrap " + str(target['id']) + ' success]')

    return data

def files_bulk():
    ts = []
    for root, dirs, files in os.walk('result/'):
        ts = files
    ts.remove('1.txt')

    o = []
    for ttt in ts:
        s = codecs.open('result/' + ttt, 'r', 'utf-8')
        f = json.loads(s.read())
        jso = OrderedDict(f)
        o.append(jso)
    print("[bulk start]")
    dataprocessing.bulk_insert(o)

def main():
    targets = getListsMultiProcess()
    outputs = []

    print("[Make Json files]")

    pp = Pool(processes=10)
    while len(targets) != 0:
        print(len(targets))
        datas = []
        if len(targets) == 1:
            data = makeData(targets[0])
            outputs.append(data)
            break

        if len(targets) - 10 > 0:
            datas = pp.map(makeData, targets[:10])
            t = targets[:10]
            for target in t:
                targets.remove(target)
        else:
            datas = pp.map(makeData, targets[:-1])
            t = targets[:-1]
            for target in t:
                targets.remove(target)

        outputs.extend(datas)

    pp.close()

    print("[Bulk Insert Start]")
    dataprocessing.bulk_insert(outputs)
