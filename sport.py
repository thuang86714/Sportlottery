import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import random
import json
from web3 import Web3
import contract_abi
import contract_abi2
import time

pathProg = 'D:\\'   
os.chdir(pathProg)

USER_AGENTS = []
with open('./user_agents.txt', 'r') as fp:
    line = fp.readline().strip('\n')
    while(line):
        USER_AGENTS.append(line)
        line = fp.readline().strip('\n')

teamlist = []
scorelist1 = []
scorelist2 = []
extendlist = []
winteamlist = []

dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = USER_AGENTS[random.randint(0, len(USER_AGENTS)-1)]
driver = webdriver.PhantomJS(desired_capabilities=dcap)
#url = 'http://tslc.stats.com/nba/scoreboard.asp'
url = 'http://tslc.stats.com/nba/scoreboard.asp?day=20190114'
driver.get(url)

names = driver.find_elements_by_css_selector("td.shsNamD > a")
for name in names:
    teamlist.append(name.text)

scores1 = driver.find_elements_by_css_selector("tr > td > table:nth-child(1) > tbody > tr:nth-child(2) > td:nth-last-child(1)")
del scores1[0]
for score1 in scores1:
	scorelist1.append(score1.text)

scores2 = driver.find_elements_by_css_selector("tr > td > table:nth-child(1) > tbody > tr:nth-child(3) > td:nth-last-child(1)")
del scores2[0]
for score2 in scores2:
	scorelist2.append(score2.text)
driver.quit()

for i in range(len(scorelist1)):
	if int(scorelist1[i]) >  int(scorelist2[i]) :
		winteamlist.append(teamlist[i*2])
	else : 
		winteamlist.append(teamlist[i*2+1])

print(teamlist) #所有球隊
print(winteamlist) # 勝隊

web3 = Web3(Web3.HTTPProvider("https://rinkeby.infura.io/v3/2ff1e61ad7224ad187ce1a351028493e")) #example provider
web3.eth.enable_unaudited_features()
infuraid = "2ff1e61ad7224ad187ce1a351028493e"
infuraproject = "623eb1daf6994a359c61aae915644d9f"

contract_address = "0xE563292c1F8D36d0F410fb53Ed522339aFb30CE7"
contract1 = web3.eth.contract(abi = contract_abi.abi, address = contract_address)

def get_contract_address(number):
    return contract1.functions.eventList(number).call()

dict1 = {'波士頓塞爾提克':7, '布魯克林籃網':8, '曼斐斯灰熊':9, '休士頓火箭':10, '夏洛特黃蜂':11, '聖安東尼奧馬刺':12, '底特律活塞':13, '猶他爵士':14, '波特蘭拓荒者':15, '沙加緬度國王':16, '紐奧良鵜鶘':17, '洛杉磯快艇':18}

teamaddress = []
winteamaddress = []
for i, element in enumerate(winteamlist):
    winteamaddress.append(get_contract_address(int(dict1[element])))

for i, element in enumerate(teamlist):
    teamaddress.append(get_contract_address(int(dict1[element])))

print(winteamaddress)
print(teamaddress)

wallet_address = "0xbA89c6439A4D8815d3116C29ABa1c57776742c13"
wallet_private_key = "240ae83f08c2fe281b5d271dfb2729a19ccf42f7ca13d1a75522dd6ad612aa05"

gp = int(web3.eth.gasPrice * 1.4)

def send_contract_address(winaddress, address, txnonce):

    #contract2 = web3.eth.contract(abi = contract_abi2.abi, address = "0xE563292c1F8D36d0F410fb53Ed522339aFb30CE7")
    contract2 = web3.eth.contract(abi = contract_abi2.abi, address = address)
    txn_dict = contract2.functions.Win(winaddress).buildTransaction({
        'chainId': 4,
        'gas': 1000000,
        'gasPrice': gp,
        'nonce': txnonce,
    })

    signed_txn = web3.eth.account.signTransaction(txn_dict, private_key=wallet_private_key)

    result = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.getTransactionReceipt(result)
    print(tx_receipt)

    count = 0
    while tx_receipt is None and (count < 60):

       tx_receipt = web3.eth.getTransactionReceipt(result)
       print(tx_receipt)
       count = count+1
       time.sleep(1)

    print(contract2.call().isWin())


for i, element in enumerate(winteamaddress):

    send_contract_address(str(element), str(teamaddress[2*i]), web3.eth.getTransactionCount(wallet_address))
    time.sleep(15)
    send_contract_address(str(element), str(teamaddress[2*i+1]), web3.eth.getTransactionCount(wallet_address))

