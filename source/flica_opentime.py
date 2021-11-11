import requests
from bs4 import BeautifulSoup as bs
import sys
import os
import time
import datetime
import json
from source.flica_functions import login_flica,get_proxy
from random import choice
import traceback



def open_time_table(user,password,headers,ot_date):


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
		opentime_url     = "https://spirit.flica.net/full/otopentimepot.cgi?BCID=019.000&ViewOT=1"
	elif account_type == "copilot":
		opentime_url     = "https://spirit.flica.net/full/otopentimepot.cgi?BCID=020.%s&ViewOT=1" % bcid_ot
	elif account_type == "captain":
		opentime_url     = "https://spirit.flica.net/full/otopentimepot.cgi?BCID=002.%s&ViewOT=1" % bcid_ot
	
	# print("opentime_url :",opentime_url)
	
	isResponseFull = False
	RETRY_COUNT    = 0
	while 1:
		RETRY_COUNT  += 1
		if RETRY_COUNT == 3:
			break
		proxies      = get_proxy()
		try:
			with requests.Session() as session:
				opentime_res      = session.get(opentime_url,proxies=proxies,timeout=10,cookies=cookies,headers=headers)
			opentime_res_TEXT = opentime_res.text
			if "</html>" in opentime_res_TEXT:
				isResponseFull = True
				break
		except:
			errmsg = traceback.format_exc()
			print('retry :',opentime_url,errmsg)

	# # DEBUG :
	# with open('html/opentime_res_%s.html' % user,"w",encoding='utf-8') as DFF:
	# 	DFF.write(opentime_res_TEXT)
	

	
	if "An error has occurred, please contact Sabre Customer Care for assistance" in opentime_res_TEXT:
		return {"message":"opentime_data_not_available"}
	
	try:
		data_rows     = [eval(I.split('new Task')[1].split(');')[0] + ')') for I in opentime_res_TEXT.split('var TAry=new Array();')[1]\
.split('function getPosString( id )')[0].split('TAry[') if 'new Task(' in I]
		data_lines    = opentime_res_TEXT.split('var TAry=new Array();')[1].split('function getPosString( id )')[0].split(';')
	except:
		return {"message":"opentime_data_not_available"}

	LIST_opentime  = []
	
	for d_row in data_rows:
		d_row_index  = str(data_rows.index(d_row))
		pairing      = d_row[1]
		DATE         = d_row[3]
		dates        = d_row[2]
		days         = d_row[4]
		report       = d_row[5]
		depart       = d_row[6]
		arrive       = d_row[7]
		Blk_Hrs      = d_row[8]
		Credit       = d_row[18]
		Layover      = d_row[9]
		if Layover == "&nbsp;":
			Layover = ""
		isBlocked    = d_row[23]
		# TB :
		is_TB = 0
		for DL in data_lines:
			if "TAry[%s]" % d_row_index in DL and ".TBreq=" in DL:
				is_TB = 1
		
		dic          = {"pairing":pairing,"DATE":DATE,"dates":dates,"days":days,"report":report,"depart":depart,"arrive":arrive,
		"blk_hours":Blk_Hrs,"credit":Credit,"layover":Layover,"is_TB":is_TB,"isBlocked":isBlocked}

		LIST_opentime.append(dic)
	return LIST_opentime