import requests
from bs4 import BeautifulSoup as bs
import sys
import os
import time
import datetime
import json
import csv
import urllib.parse
from source.flica_functions import login_flica,get_proxy
from random import choice

def get_requests(user,password,headers,ot_date):

	(cookies,ret_url,status_code,BCID_DIC,account_type,BCID_DIC_OT)  = login_flica(user,password,headers)

	if cookies == None:
		return {"message":"maximum retrial reached for account %s %s" % (user,password)}
	if "FailedAttempt" in ret_url:
		return {"message":"could_not_login"}
	if account_type == "other":
		return {"message":"unknown_account_type"}

	if ot_date == None or ot_date == "":
		pass
	else:
		try:
			bcid_ot  = BCID_DIC_OT[ot_date]
		except:
			return {"message":"BCID_OT_not_found"}

	if account_type in ["copilot","captain"] and not "bcid_ot" in locals():
		return {"message":"ot_date_is_required_for_pilots_accounts"}

	if account_type == "fa":
		req_url                        = "https://spirit.flica.net/full/otrequest.cgi?BCID=019.000&VC=Yes"
	elif account_type == "copilot":
		req_url                        = "https://spirit.flica.net/full/otrequest.cgi?BCID=020.%s&VC=Yes" % bcid_ot
	elif account_type == "captain":
		req_url                        = "https://spirit.flica.net/full/otrequest.cgi?BCID=002.%s&VC=Yes" % bcid_ot

	while 1:
		proxies      = get_proxy()
		try:
			with requests.Session() as session:
				req_res  = session.get(req_url,proxies=proxies,timeout=10,cookies=cookies)
			break
		except:
			print('retry :',req_url)
	
	if "Unable to retrieve bidclose details" in req_res.text:
		return {"message":"opentime_data_not_available"}
	
	# isBidSubmitOpen = req_res.text.split('isFromTradeBoard;')[1].split('function ready() {')[1].split('}')[0].split('isBidSubmitOpen=')[1].split(';')[0].strip()
	# if isBidSubmitOpen == 'false':
	# 	isOpen = False
	# elif isBidSubmitOpen == 'true':
	# 	isOpen = True
	# else:
	# 	isOpen = None

	isOpen = True
	if "Bidding Opens" in req_res.text:
		isOpen = False
	
	row_dic_list = []
	all_rows     = req_res.text.split(';')
	for row in all_rows:
		if "QAry.push( new Req(" in row:

			row_dic      = {}
			row_parsable = row.split('QAry.push( new Req(')[1].split(') )')[0]
			row_parsable = row_parsable.replace('[','"[').replace(']',']"')
			# print(row_parsable)
			reader       = csv.reader([row_parsable])
			reader_parsed= list(reader)[0]
			# print(reader_parsed)

			request_id    = reader_parsed[0].replace('"','').strip()
			request_date  = reader_parsed[1].replace('"','').strip()
			TYPE          = reader_parsed[2].replace('"','').strip()
			if TYPE == "2":
				request_type = "DROP"
			elif TYPE == "1":
				request_type = "ADD"
			elif TYPE == "4":
				request_type = "SWAP"
			
			if request_type == "SWAP":
				pairings_bloc_schedule  = eval(reader_parsed[3])
				pairings_bloc           = eval(reader_parsed[4])
				pairings_list_schedule  = []
				pairings_list           = []
				for pROW in pairings_bloc:
					pairing_dic = {}
					pairing     = pROW.split(':')[0]
					DATE        = pROW.split(':')[1]
					pairing_dic['pairing'] = pairing
					pairing_dic['DATE']    = DATE
					pairings_list.append(pairing_dic)
				for pROW in pairings_bloc_schedule:
					pairing_dic = {}
					pairing     = pROW.split(':')[0]
					DATE        = pROW.split(':')[1]
					pairing_dic['pairing'] = pairing
					pairing_dic['DATE']    = DATE
					pairings_list_schedule.append(pairing_dic)
			else:
				pairings_list_schedule  = []
				pairings_bloc  = eval(reader_parsed[3])
				pairings_list  = []
				for pROW in pairings_bloc:
					pairing_dic = {}
					pairing     = pROW.split(':')[0]
					DATE        = pROW.split(':')[1]
					pairing_dic['pairing'] = pairing
					pairing_dic['DATE']    = DATE
					pairings_list.append(pairing_dic)
			
			pairings_prio  = reader_parsed[11]
			
			status  = reader_parsed[8]

			if status == "Pending" or status == "Processing":
				request_id = request_id +":0"
			else:
				request_id = request_id +":1"

			comments = reader_parsed[9]
			comments = urllib.parse.unquote(comments)

			status_date = reader_parsed[13].replace("'","").strip()
			
			row_dic["request_id"]             = request_id
			row_dic["request_date"]           = request_date
			row_dic["type"]                   = request_type
			row_dic['pairings']               = pairings_list
			row_dic['pairings_schedule']      = pairings_list_schedule
			row_dic['status']                 = status
			row_dic['comments']               = comments
			row_dic['status_date']            = status_date
			row_dic['priority']               = pairings_prio
			
			row_dic_list.append(row_dic)
	
	response_dic = {'isOpen':isOpen,'requests':row_dic_list}
	
	return response_dic

def cancel_request(user,password,request_id,headers,ot_date):
	(cookies,ret_url,status_code,BCID_DIC,account_type,BCID_DIC_OT)  = login_flica(user,password,headers)

	if cookies == None:
		return {"message":"maximum retrial reached for account %s %s" % (user,password)}
	if "FailedAttempt" in ret_url:
		return {"message":"could_not_login"}
	if account_type == "other":
		return {"message":"unknown_account_type"}

	if ot_date == None or ot_date == "":
		pass
	else:
		try:
			bcid_ot  = BCID_DIC_OT[ot_date]
		except:
			return {"message":"BCID_OT_not_found"}

	if account_type in ["copilot","captain"] and not "bcid_ot" in locals():
		return {"message":"ot_date_is_required_for_pilots_accounts"}

	cancel_url     = "https://spirit.flica.net/full/otrequest.cgi"

	if account_type == "fa":
		params         = {"BCID":"019.000","isInFrame":"1","GO":"1"}
	elif account_type == "copilot":
		params         = {"BCID":"020.%s" % bcid_ot,"isInFrame":"1","GO":"1"}
	elif account_type == "captain":
		params         = {"BCID":"002.%s" % bcid_ot,"isInFrame":"1","GO":"1"}

	payload        = {
"Requests": "",
"Priorities": "",
"DeletedRequests": request_id,
"Contingencies":""
}
	# print(payload)

	while 1:
		proxies      = get_proxy()
		try:
			with requests.Session() as session:
				cancel_res     = session.post(cancel_url,data=payload,params=params,proxies=proxies,timeout=10,cookies=cookies)
			break
		except:
			print('retry cancel URL :',cancel_url)
		
	if cancel_res.status_code == 200:
		return {"message":"request canceled"}
	else:
		return {"message":"cancel_req_something_went_wrong"}


def add(user,password,PAIRING_DATE,headers,prio,ot_date):

	(cookies,ret_url,status_code,BCID_DIC,account_type,BCID_DIC_OT)  = login_flica(user,password,headers)

	if cookies == None:
		return {"message":"maximum retrial reached for account %s %s" % (user,password)}
	if "FailedAttempt" in ret_url:
		return {"message":"could_not_login"}
	if account_type == "other":
		return {"message":"unknown_account_type"}

	if ot_date == None or ot_date == "":
		pass
	else:
		try:
			bcid_ot  = BCID_DIC_OT[ot_date]
		except:
			return {"message":"BCID_OT_not_found"}

	if account_type in ["copilot","captain"] and not "bcid_ot" in locals():
		return {"message":"ot_date_is_required_for_pilots_accounts"}
	
	if account_type == "fa":
		add_url               = "https://spirit.flica.net/full/otadd.cgi?BCID=019.000"
	elif account_type == "copilot":
		add_url               = "https://spirit.flica.net/full/otadd.cgi?BCID=020.%s" % bcid_ot
	elif account_type == "captain":
		add_url               = "https://spirit.flica.net/full/otadd.cgi?BCID=002.%s" % bcid_ot

	while 1:
		proxies      = get_proxy()
		try:
			with requests.Session() as session:
				add_res  = session.get(add_url,proxies=proxies,timeout=10,cookies=cookies)
			break
		except:
			print('retry :',add_url)
	if "This bid close is not ready yet" in add_res.text:
		return {"method":"ADD","pairing":PAIRING_DATE,"message":"Not Ready Yet"}

	START_DATE            = add_res.text.split('&StartDate=')[1].split('&')[0]

	END_DATE              = add_res.text.split('&EndDate=')[1].split('"')[0]

	add_soup              = bs(add_res.content, "lxml")

	pageId                = add_soup.find_all('input',{'id':'pageId'})[0]['value']

	# PIDX                  = add_soup.find_all('input',{'name':'PIDX'})[0]['value']

	otaddURL              = "https://spirit.flica.net/full/otadd.cgi"

	if account_type == "fa":
		params                = {'SubmitBids':'YES','BCID':'019.000'}
	elif account_type == "copilot":
		params                = {'SubmitBids':'YES','BCID':'020.%s' % bcid_ot}
	elif account_type == "captain":
		params                = {'SubmitBids':'YES','BCID':'002.%s' % bcid_ot}

	payload               = [
("btnAdd",""),("StartDate",START_DATE),("EndDate",END_DATE),("OptOrder",""),("OptOrder",""),("OptOrder",""),
("OptOrder",""),("OptOrder",""),("OptOrder",""),("OptOrder",""),("OptOrder",""),("OptOrder",""),("OptOrder",""),
("OptOrder",""),("OptOrder",""),("OptOrder",""),("OptOrder",""),("OptOrder",""),("OptOrder",""),("OptOrder",""),
("OptOrder",""),("OptOrder",""),("OptOrder",""),("ALLR","0"),("PIDX",prio),("WDFD",""),("AOT",""),("pageId",pageId),
("TBReq","0"),("TBResp","0"),("TBBC","0"),("TBCid","0"),("TBSplit",""),("addBid",PAIRING_DATE),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid","")]

	while 1:
		proxies      = get_proxy()
		try:
			with requests.Session() as session:
				rr     = session.post(otaddURL,data=payload,params=params,proxies=proxies,timeout=10,cookies=cookies)
			break
		except:
			print('retry :',otaddURL)

	status_code = rr.status_code

	dic_res = {"method":"ADD","pairing":PAIRING_DATE,"message":"success"}

	return dic_res


def drop(user,password,PAIRING_DATE,headers,prio,ot_date):

	(cookies,ret_url,status_code,BCID_DIC,account_type,BCID_DIC_OT)  = login_flica(user,password,headers)

	if cookies == None:
		return {"message":"maximum retrial reached for account %s %s" % (user,password)}
	if "FailedAttempt" in ret_url:
		return {"message":"could_not_login"}
	if account_type == "other":
		return {"message":"unknown_account_type"}

	if ot_date == None or ot_date == "":
		pass
	else:
		try:
			bcid_ot  = BCID_DIC_OT[ot_date]
		except:
			return {"message":"BCID_OT_not_found"}

	if account_type in ["copilot","captain"] and not "bcid_ot" in locals():
		return {"message":"ot_date_is_required_for_pilots_accounts"}

	if account_type == "fa":
		drop_url  = "https://spirit.flica.net/full/otdrop.cgi?BCID=019.000&GO=1&TRADE=1&PIDX=1&ALLR=1&JUNK=1567477911955"
	elif account_type == "copilot":
		drop_url  = "https://spirit.flica.net/full/otdrop.cgi?BCID=020.%s&GO=1&TRADE=1&PIDX=1&ALLR=1&JUNK=1567477911955" % bcid_ot
	elif account_type == "captain":
		drop_url  = "https://spirit.flica.net/full/otdrop.cgi?BCID=002.%s&GO=1&TRADE=1&PIDX=1&ALLR=1&JUNK=1567477911955" % bcid_ot

	
	while 1:
		proxies      = get_proxy()
		try:
			with requests.Session() as session:
				drop_res  = session.get(drop_url,proxies=proxies,timeout=10,cookies=cookies)
			break
		except:
			print('retry :',drop_url)

	if "This bid close is not ready yet" in drop_res.text:
		return {"message":"Not Ready Yet","method":"DROP","pairing":PAIRING_DATE}


	# drop_soup             = bs(drop_res.content, "lxml")

	# PIDX                  = drop_soup.find_all('input',{'name':'PIDX'})[0]['value']

	otdropURL = "https://spirit.flica.net/full/otdrop.cgi"

	if account_type == "fa":
		params    = {'SubmitBids':'1','BidCloseID':'019.000'}
	elif account_type == "copilot":
		params    = {'SubmitBids':'1','BidCloseID':'020.%s' % bcid_ot}
	elif account_type == "captain":
		params    = {'SubmitBids':'1','BidCloseID':'002.%s' % bcid_ot}

	payload   = [
("CMComments",""),("ALLR","0"),("PIDX",prio),("TXN",""),("AOT",""),("BID",PAIRING_DATE),("foreignId",""),("BID",""),
("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),
("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),
("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),
("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),
("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),
("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),
("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),
("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),
("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),
("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),
("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),
("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),
("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),
("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),
("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),
("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),
("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),
("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),
("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),
("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),
("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),
("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),
("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),
("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),
("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),
("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),
("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),
("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),
("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),
("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),
("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),
("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),
("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),
("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),
("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),
("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),
("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),
("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),
("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),("BID",""),("foreignId",""),
("BID",""),("foreignId",""),("BID",""),("foreignId","")]

	while 1:
		proxies      = get_proxy()
		try:
			with requests.Session() as session:
				rr     = session.post(otdropURL,data=payload,params=params,proxies=proxies,timeout=10,cookies=cookies)
			break
		except:
			print('retry :',otdropURL)

	status_code = rr.status_code
	if "An error has occurred," in rr.text:
		return {"status_code":"Not Ready Yet","method":"DROP","pairing":PAIRING_DATE}

	dic_res = {"method":"DROP","pairing":PAIRING_DATE,"message":"success"}

	return dic_res

def AddFromTB(user,password,PAIRING_DATE,headers,tb_monthyear):
	(cookies,ret_url,status_code,BCID_DIC,account_type,BCID_DIC_OT)  = login_flica(user,password,headers)

	if cookies == None:
		return {"message":"maximum retrial reached for account %s %s" % (user,password)}
	if "FailedAttempt" in ret_url:
		return {"message":"could_not_login"}
	if account_type == "other":
		return {"message":"unknown_account_type"}

	try:
		bcid  = BCID_DIC[tb_monthyear]
	except:
		return {"message":"BCID_not_found"}

	PAIRING        = PAIRING_DATE.split(':')[0]
	DATE           = PAIRING_DATE.split(':')[1]

	tb_all_requests = "https://spirit.flica.net/online/tb_otherrequests.cgi?bcid="+bcid

	while 1:
		proxies      = get_proxy()
		try:
			with requests.Session() as session:
				tb_all_requests_res  = session.get(tb_all_requests,proxies=proxies,timeout=10,cookies=cookies)
			break
		except:
			print('retry :',tb_all_requests)
	
	tb_all_requests_TEXT = tb_all_requests_res.text

	hdnDepDate           = tb_all_requests_TEXT.split('hdnDepDate=')[1].split('&')[0]
	hdnPos               = tb_all_requests_TEXT.split('hdnPos=')[1].split('&')[0]
	hdnType              = tb_all_requests_TEXT.split('&hdnType=')[1].split('&')[0]
	hdnBase              = tb_all_requests_TEXT.split('&hdnBase=')[1].split('&')[0]
	hdnEqp               = tb_all_requests_TEXT.split('&hdnEqp=')[1].split('&')[0]
	

	all_rows             = tb_all_requests_TEXT.split('\n')

	for row in all_rows:
		if "]=new A(" in row:
			row_data = row.split("]=new A(")[1].strip()
			if row_data.endswith(')'):
				row_data = row_data[:-1]
			reader         = csv.reader([row_data])
			reader_parsed  = list(reader)[0]

			row_pairing    = reader_parsed[5]
			if row_pairing == None:
				continue
			row_date       = reader_parsed[8]

			if row_pairing.lower().strip() == PAIRING.lower().strip() and row_date.strip() == DATE.strip():
				matched_thecid  = reader_parsed[3]
				matched_reqId   = reader_parsed[0]
	try:
		X1 = matched_thecid
		Y1 = matched_reqId
	except:
		return {"message":"pairing_not_found","method":"ADD_FROM_TB","pairing":PAIRING}

	add_from_tb_url = "https://spirit.flica.net/online/TB_postrequest.cgi"

	params     = {
"bFromOtherRequest": "1",
"hdnDepDate": hdnDepDate,
"hdnMessages": "1",
"hdnFlicaResponse": "1",
"hdnBase": hdnBase,
"hdnEqp": hdnEqp,
"hdnPos": hdnPos,
"hdnSubmit": "submitting",
"hdnType": hdnType,
"hdnWaiveDaysOff": "0",
"hdnWaiveMinRest": "0",
"thecid": matched_thecid,
"reqId": matched_reqId,
"BCID": bcid,
"treq": "resDrop"
	}
	
	while 1:
		proxies      = get_proxy()
		try:
			with requests.Session() as session:
				add_from_tb_res  = session.get(add_from_tb_url,params=params,proxies=proxies,timeout=10,cookies=cookies)
			break
		except:
			print('retry :',add_from_tb_url)
	
	status_code = add_from_tb_res.status_code
	dic_res     = {"message":"success","method":"ADD_FROM_TB","pairing":PAIRING}
	return dic_res

def DropToTB(user,password,PAIRING_DATE,headers,tb_monthyear):
	(cookies,ret_url,status_code,BCID_DIC,account_type,BCID_DIC_OT)  = login_flica(user,password,headers)

	if cookies == None:
		return {"message":"maximum retrial reached for account %s %s" % (user,password)}
	if "FailedAttempt" in ret_url:
		return {"message":"could_not_login"}
	if account_type == "other":
		return {"message":"unknown_account_type"}

	try:
		bcid  = BCID_DIC[tb_monthyear]
	except:
		return {"message":"BCID_not_found"}

	tb_all_requests = "https://spirit.flica.net/online/tb_otherrequests.cgi?bcid="+bcid

	while 1:
		proxies      = get_proxy()
		try:
			with requests.Session() as session:
				tb_all_requests_res  = session.get(tb_all_requests,proxies=proxies,timeout=10,cookies=cookies)
			break
		except:
			print('retry :',tb_all_requests)
	
	tb_all_requests_TEXT = tb_all_requests_res.text

	hdnDepDate           = tb_all_requests_TEXT.split('hdnDepDate=')[1].split('&')[0]
	hdnPos               = tb_all_requests_TEXT.split('hdnPos=')[1].split('&')[0]
	# hdnType              = tb_all_requests_TEXT.split('&hdnType=')[1].split('&')[0]
	hdnBase              = tb_all_requests_TEXT.split('&hdnBase=')[1].split('&')[0]
	hdnEqp               = tb_all_requests_TEXT.split('&hdnEqp=')[1].split('&')[0]

	
	DATE           = PAIRING_DATE.split(':')[1]
	DATE_OBJ       = datetime.datetime.strptime(DATE,'%Y%m%d')
	YEAR           = DATE_OBJ.strftime('%Y')
	YEARMONTH      = DATE_OBJ.strftime('%Y%m')
	DAY            = DATE_OBJ.strftime('%d')
	PAIRING_DATE_q = urllib.parse.quote(PAIRING_DATE)
	
	drop_to_tb_url = "https://spirit.flica.net/online/TB_postrequest.cgi"

	params         = {'BCID':bcid}
	# print(params)

	payload = """TradeType=D&CommentField=&email=&Phone=&rFLiCA=&FLiCA=&rEMail=&EMail=&rPhone=&
Phone=&Year=%s&Year1=%s&RemPairIndex=-1&RemPairCount=0&Day=%s&Month=%s&reqId=0&treq=&
thecid=0&PAIRDATE=&hdnWaiveDaysOff=&hdnWaiveMinRest=&hdnDeleting=&hdnPairingIndex=&
hdnSubmit=submitting&hdnTripListCount=0&hdnType=D&hdnDepDate=&hdnDays=&hdnDep=&hdnArr=&
hdnBlkHrs=&hdnLayovers=&hdnComments=&hdnFlicaResponse=true&hdnMessages=true&hdnEmail=&
hdnPhone=&hdnBase=%s&hdnEqp=%s&hdnPos=%s&hdnExtraPos=&hdnAutoSubmit=true&hdnPickup=0&
hdnVacPeriodYear=&hdnVacLength=&hdnVacYear=&hdnDayStr=&hdnDayStrLong=&
hdnPairStr=%s&hdnMyDST=&hdnMyBlockDate=&hdnDayLen=&hdnEarlyDepart=&
hdnLateArrive=&hdnLateDepDate=%s&hdnDeleteAfter=%s&hdnSchedulePairings=&
hdnLODO=&hdnSplitStr=&TXN=&hdnPairing=0&hdnDepDate=0&hdnPairing=1&hdnDepDate=1&
hdnPairing=2&hdnDepDate=2&hdnPairing=3&hdnDepDate=3&hdnPairing=4&hdnDepDate=4&
hdnPairing=5&hdnDepDate=5&hdnPairing=6&hdnDepDate=6&hdnPairing=7&hdnDepDate=7&
hdnPairing=8&hdnDepDate=8&hdnPairing=9&hdnDepDate=9""" % (YEAR,YEAR,DAY,YEARMONTH,hdnBase,hdnEqp,hdnPos,PAIRING_DATE_q,DATE,DATE)

	# print(payload)

	while 1:
		proxies      = get_proxy()
		try:
			with requests.Session() as session:
				drop_to_tb_res     = session.post(drop_to_tb_url,data=payload,params=params,proxies=proxies,timeout=10,cookies=cookies)
			break
		except:
			print('retry :',drop_to_tb_url)

	status_code = drop_to_tb_res.status_code 
	dic_res     = {"message":"success","method":"DROP_TO_TB","pairing":PAIRING_DATE}
	
	return dic_res

def swap(user,password,all_PAIRING_DATE,all_to_PAIRING_DATE,headers,prio,ot_date,as_separate_request):

	if as_separate_request.lower() == "no":
		ALLR = "1"
	elif as_separate_request.lower() == "yes":
		ALLR = "0"
	else:
		ALLR = "1"

	MySubmitPairs_list      = []
	MySwapPairs_list        = []
	all_PAIRING_DATE_list   = all_PAIRING_DATE.split('|')
	for PAIRING_DATE in all_PAIRING_DATE_list:
		MySubmitPairs_list.append(PAIRING_DATE)
		DATE                    = PAIRING_DATE.split(':')[1]
		DATE_OBJ                = datetime.datetime.strptime(DATE,'%Y%m%d')
		DATE_FOR_MySwapPairs    = DATE_OBJ.strftime("%d%b")
		DATE_FOR_MySwapPairs    = DATE_FOR_MySwapPairs.upper()
		PAIRING_FOR_MySwapPairs = PAIRING_DATE.split(':')[0]+":"+DATE_FOR_MySwapPairs

		MySwapPairs_list.append(PAIRING_FOR_MySwapPairs)
	
	MySubmitPairs = ",".join(MySubmitPairs_list)
	MySwapPairs   = " and ".join(MySwapPairs_list)

	addBid_list = []
	all_to_PAIRING_DATE_list = all_to_PAIRING_DATE.split('|')
	for to_PAIRING_DATE in all_to_PAIRING_DATE_list:
		addBid_list.append(to_PAIRING_DATE)


	(cookies,ret_url,status_code,BCID_DIC,account_type,BCID_DIC_OT)  = login_flica(user,password,headers)

	if cookies == None:
		return {"message":"maximum retrial reached for account %s %s" % (user,password)}
	if "FailedAttempt" in ret_url:
		return {"message":"could_not_login"}
	if account_type == "other":
		return {"message":"unknown_account_type"}

	if ot_date == None or ot_date == "":
		pass
	else:
		try:
			bcid_ot  = BCID_DIC_OT[ot_date]
		except:
			return {"message":"BCID_OT_not_found"}

	if account_type in ["copilot","captain"] and not "bcid_ot" in locals():
		return {"message":"ot_date_is_required_for_pilots_accounts"}
	
	if account_type == "fa":
		swap_url               = "https://spirit.flica.net/full/otswap.cgi?&GO=1&BCID=019.000"
	elif account_type == "copilot":
		swap_url               = "https://spirit.flica.net/full/otswap.cgi?&GO=1&BCID=020.%s" % bcid_ot
	elif account_type == "captain":
		swap_url               = "https://spirit.flica.net/full/otswap.cgi?&GO=1&BCID=002.%s" % bcid_ot

	while 1:
		proxies      = get_proxy()
		try:
			with requests.Session() as session:
				swap_res  = session.get(swap_url,proxies=proxies,timeout=10,cookies=cookies)
			break
		except:
			print('retry :',swap_url)
	if "This bid close is not ready yet" in swap_res.text:
		return {"method":"SWAP","pairing":PAIRING_DATE,"message":"Not Ready Yet"}

	PAGE_ID            = swap_res.text.split("'&pageId=")[1].split("';")[0]

	swap_url_2         = "https://spirit.flica.net/full/otswap2.cgi"

	if account_type == "fa":
		params_2                = {'BCID':'019.000',"MySwapPairs":MySwapPairs,"MySubmitPairs":MySubmitPairs,
		"PIDX":prio,"Restriction":"0","AOTSValue":"","pageId":PAGE_ID}
	elif account_type == "copilot":
		params_2                = {'BCID':'020.%s' % bcid_ot,"MySwapPairs":MySwapPairs,"MySubmitPairs":MySubmitPairs,
		"PIDX":prio,"Restriction":"0","AOTSValue":"","pageId":PAGE_ID}
	elif account_type == "captain":
		params_2                = {'BCID':'002.%s' % bcid_ot,"MySwapPairs":MySwapPairs,"MySubmitPairs":MySubmitPairs,
		"PIDX":prio,"Restriction":"0","AOTSValue":"","pageId":PAGE_ID}

	while 1:
		proxies      = get_proxy()
		try:
			with requests.Session() as session:
				swap_2_res  = session.get(swap_url_2,params=params_2,proxies=proxies,timeout=10,cookies=cookies)
			break
		except:
			print('retry :',swap_url_2)
	
	swap_2_soup = bs(swap_2_res.content, "lxml")

	StartDate   = swap_2_soup.find_all('input',{"id":"StartDate"})[0]["value"]
	EndDate     = swap_2_soup.find_all('input',{"id":"EndDate"})[0]["value"]

	if account_type == "fa":
		params_submit                = {'BCID':'019.000',"SubmitBids":"YES"}
	elif account_type == "copilot":
		params_submit                = {'BCID':'020.%s' % bcid_ot,"SubmitBids":"YES"}
	elif account_type == "captain":
		params_submit                = {'BCID':'002.%s' % bcid_ot,"SubmitBids":"YES"}

	payload_submit               = [("btnAdd",""),("StartDate",StartDate),("EndDate",EndDate),("OptOrder",""),
("OptOrder",""),("OptOrder",""),("OptOrder",""),("OptOrder",""),("OptOrder",""),("OptOrder",""),("OptOrder",""),("OptOrder",""),
("OptOrder",""),("OptOrder",""),("OptOrder",""),("OptOrder",""),("OptOrder",""),("OptOrder",""),("OptOrder",""),("OptOrder",""),
("OptOrder",""),("OptOrder",""),("OptOrder",""),("ALLR",ALLR),("PIDX",prio),("WDFD",""),("SELREQ","false"),("AOT",""),("ABI",""),
("pageId",PAGE_ID),("TBReq","0"),("TBResp","0"),("TBBC","0"),("TBCid","0"),("TBSplit",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),("addBid",""),
("addBid",""),("Restriction","0"),
("MySubmitPairs",MySubmitPairs),("MySwapPairs",MySwapPairs)]
	for PAIR in MySubmitPairs_list:
		payload_submit.append( ("dropBid",PAIR) )
	
	for PAIR in addBid_list:
		payload_submit.remove( ("addBid","") )
		payload_submit.append( ("addBid",PAIR) )


	while 1:
		proxies      = get_proxy()
		try:
			with requests.Session() as session:
				rr     = session.post(swap_url_2,data=payload_submit,params=params_submit,proxies=proxies,timeout=10,cookies=cookies)
			break
		except:
			print('retry :',swap_url_2)

	status_code = rr.status_code

	dic_res = {"method":"SWAP","pairing":all_PAIRING_DATE,"to_pairing":all_to_PAIRING_DATE,"message":"success"}

	return dic_res