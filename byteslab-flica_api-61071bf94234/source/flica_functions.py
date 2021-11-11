import traceback
import requests
from bs4 import BeautifulSoup as bs
import sys
import os
import time
import datetime
import json
from random import choice,randint,random

def get_proxy():
	random_id      = random()
	proxy_string   = "lum-customer-hl_c487542d-zone-zone1-session-%s:hx4xvmm4p0se@zproxy.lum-superproxy.io:22225" % random_id
	proxies        = { "https" : "http://%s" % proxy_string ,"http" : "http://%s" % proxy_string}
	return proxies

def login_flica(user,password,headers):

	new_headers = dict(headers)

	RETRY      = 0
	RETRY_COOK = 0
	while 1:
		
		RETRY      += 1
		RETRY_COOK += 1
		if RETRY == 11:
			return (None,None,None,None,None,None)
		print('> attempt %s : ' % RETRY + str(user))

		with requests.Session() as session:

			# new_headers["Accept"]  = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
			# new_headers["Accept-Encoding"] = "gzip, deflate, br"
			# new_headers["Connection"] = "keep-alive"
			# new_headers["Host"]      = "spirit.flica.net"
			# new_headers["Proxy-Authorization"] = "Basic bHVtLWN1c3RvbWVyLWhsX2M0ODc1NDJkLXpvbmUtem9uZTEtaXAtNDUuNDEuMTc3LjE1MTpoeDR4dm1tNHAwc2U="

			
			session.headers    = new_headers
			home_url           = "https://spirit.flica.net/online/mainmenu.cgi"

			cookies_path       = 'accounts'+os.sep+user.lower()
			cookies_file       = cookies_path+os.sep+"cookies.json"

			if RETRY_COOK == 2:
				try:
					os.remove(cookies_file)
				except:
					pass
				RETRY_COOK = 0

			try:
				with open(cookies_file) as json_file:
					cookies = json.load(json_file)
			except:
				cookies = {}

			# CHECK SESSION ACTIVE OR NOT :
			RETRY_COUNT = 0
			while 1:
				RETRY_COUNT += 1
				if RETRY_COUNT == 11:
					return (None,None,None,None,None,None)
				proxies      = get_proxy()
				try:
					home_res                   = session.get(home_url,proxies=proxies,cookies=cookies,timeout=10)
					break
				except:
					errMsg = traceback.format_exc()
					print('retry home url 1 :',home_url)
					# print(errMsg)
			
			# # DEBUG :
			# print(home_res.headers)
			# print(home_res.request.headers)
			# with open('home_res.html',"w",encoding='utf-8') as DFF:
			# 	DFF.write(home_res.text)

			if "public/login/index" in home_res.text or "FLICA - Session Closed" in home_res.text \
			or "public/login/index" in home_res.url or "Page request failed, please click " in home_res.text:

				# print('logging in ...')

				session            = requests.Session()
				new_headers["Host"]    = "spirit.flica.net"
				new_headers["Referer"] = "https://spirit.flica.net/ui/public/login/index.html"
				
				login              = "https://spirit.flica.net/public/flicaLogon.cgi"
				
				session.headers       = new_headers
				payload               = {}
				payload["UserId"]     = user
				payload["Password"]   = password
				payload["RememberMe"] = "on"

				RETRY_COUNT = 0
				while 1:
					proxies      = get_proxy()
					RETRY_COUNT += 1
					if RETRY_COUNT == 11:
						return (None,None,None,None,None,None)
					try:
						res                   = session.post(login,data=payload,proxies=proxies,timeout=10)
						break
					except:
						print('retry :',login)
				ret_url               = res.url
				status_code           = res.status_code

				# print("ret_url  :",ret_url)
				# print("status_code  :",status_code)
				# print("payload  :",payload)

				# CHECK WHEN LOGIN FAILED :
				if "FailedAttempt" in ret_url:
					cookies            = session.cookies.get_dict()
					return (session,ret_url,status_code,None,None,None)

				# SAVE COOKIES TO JSON FILE :
				cookies            = session.cookies.get_dict()
				cookies_path       = 'accounts'+os.sep+user.lower()
				cookies_file       = cookies_path+os.sep+"cookies.json"
				try:
					os.makedirs(cookies_path)
				except:
					pass
				with open(cookies_file, 'w') as outfile:
					json.dump(cookies, outfile)


				RETRY_COUNT = 0
				while 1:
					proxies      = get_proxy()
					RETRY_COUNT += 1
					if RETRY_COUNT == 11:
						return (None,None,None,None,None,None)
					try:
						home_res                = session.get(home_url,proxies=proxies,timeout=10)
						break
					except:
						print('retry home url 2 :',home_url)

				res_TEXT              = home_res.text
			else:
				session.cookies.update(cookies)
				ret_url               = home_res.url
				status_code           = home_res.status_code
				res_TEXT              = home_res.text

			# # # DEBUG :
			# print('ret_url :',ret_url)
			# TIME = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
			# with open('home_res_%s_%s.html' % (RETRY,TIME),"w",encoding='utf-8') as DFF:
			# 	DFF.write(res_TEXT)

			# GET ACCOUNT TYPE : (Flight Attendant or Copilot or Captain)

			cookies            = dict(session.cookies.get_dict())

			if user.lower() == "nks071690":
				account_type = 'captain'
				break
			else:

				if "?BCID=019." in res_TEXT:
					account_type = 'fa'
					break
				elif "?BCID=020." in res_TEXT:
					account_type = 'copilot'
					break
				elif "?BCID=002." in res_TEXT:
					account_type = 'captain'
					break
				elif "?BCID=001." in res_TEXT:  # NEW FO 
					account_type = 'copilot'
					break
				else:
					account_type = 'other'
					continue




			# if "System Bid(Pilots)" in res_TEXT and not "CAPTAIN" in res_TEXT:
			# 	account_type = 'copilot'
			# 	break
			# elif "System Bid(Pilots)" in res_TEXT and "CAPTAIN" in res_TEXT:
			# 	account_type = 'captain'
			# 	break
			# else:
			# 	if "Trades between Pilots" in res_TEXT:
			# 		if "FIRST OFFICER" in res_TEXT:
			# 			account_type = 'copilot'
			# 			break
			# 		elif "CAPTAIN" in res_TEXT:
			# 			account_type = 'captain'
			# 			break
			# 		else:
			# 			account_type = 'other'
			# 			continue
					
			# 	elif "Trades between FAs" in res_TEXT or "FLIGHT ATTENDANT " in res_TEXT or 'Daily Open Time(FA)' in res_TEXT:
			# 		account_type = 'fa'
			# 		break
			# 	else:
			# 		account_type = 'other'
			# 		continue
		
	if account_type == "other":
		# cookies            = session.cookies.get_dict()
		return (cookies,ret_url,status_code,None,account_type,None)

	months      = ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
	years       = range(2019,2051)
	BCID_DIC    = {}
	BCID_DIC_OT = {}

	bcid_init_ot = 48    # BASED ON OPENTIME BCID OF JANUARY 2019 = XXX.049 (XXX is 020 for copilots or 002 for captains)

	if account_type == "fa":
		bcid_init    = 29   # BASED ON BCID OF JANUARY 2019 = 010.030
		bcid_code    = "010."
	elif account_type == "copilot" or account_type == 'captain':
		bcid_init    = 107   # BASED ON BCID OF JANUARY 2019 = 003.108
		bcid_code    = "003."
		
	for year in years:
		for month in months:
			bcid_init            += 1
			month_year           = month+str(year)
			bcid                 = bcid_code+str(bcid_init).zfill(3)
			BCID_DIC[month_year] = bcid

			bcid_init_ot            += 1
			bcid_ot                 = str(bcid_init_ot).zfill(3)
			BCID_DIC_OT[month_year] = bcid_ot
	# print(BCID_DIC)
	# print(BCID_DIC_OT)
	# cookies            = session.cookies.get_dict()

	return (cookies,ret_url,status_code,BCID_DIC,account_type,BCID_DIC_OT)