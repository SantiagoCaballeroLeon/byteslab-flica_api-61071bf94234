import requests
from bs4 import BeautifulSoup as bs
import sys
import os
import time
import datetime
import json
from source.flica_functions import login_flica,get_proxy
from random import choice



def get_user_info(user,password,headers,ot_date):


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
		user_info_url     = "https://spirit.flica.net/full/ottitle.cgi?BCID=019.000&ViewOT=1"
	elif account_type == "copilot":
		user_info_url     = "https://spirit.flica.net/full/ottitle.cgi?BCID=020.%s&ViewOT=1" % bcid_ot
	elif account_type == "captain":
		user_info_url     = "https://spirit.flica.net/full/ottitle.cgi?BCID=002.%s&ViewOT=1" % bcid_ot
	
	isResponseFull = False
	RETRY_COUNT    = 0
	while 1:
		RETRY_COUNT  += 1
		if RETRY_COUNT == 3:
			break
		proxies      = get_proxy()
		try:
			with requests.Session() as session:
				user_info_res      = session.get(user_info_url,proxies=proxies,timeout=10,cookies=cookies)
			user_info_res_TEXT = user_info_res.text
			if "</html>" in user_info_res_TEXT:
				isResponseFull = True
				break
		except:
			print('retry :',user_info_url)


	if "An error has occurred, please contact Sabre Customer Care for assistance" in user_info_res_TEXT:
		return {"message":"userinfo_data_not_available"}
	
	
	user_info_soup = bs(user_info_res.content, "lxml")

	all_string     = user_info_soup.find_all('strong')

	NAME           = all_string[0].text.strip()

	fname          = NAME.split(",")[1].strip()
	lname          = NAME.split(",")[0].strip()

	BASE_ROW       = all_string[1].text.strip()

	# print(BASE_ROW)

	BASE_ROW_LIST  = BASE_ROW.split("\xa0")

	# print(BASE_ROW_LIST)

	employee_number = BASE_ROW_LIST[0]

	BASE           = BASE_ROW_LIST[3]

	equipment      = BASE_ROW_LIST[-4]

	position       = BASE_ROW_LIST[-1]

	DATA           = {"last_name":lname,"first_name":fname,"position":position,"employee_number":employee_number,
	"base":BASE,"equipment":equipment}

	return DATA

