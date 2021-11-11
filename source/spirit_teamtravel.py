import requests
import datetime
from bs4 import BeautifulSoup as bs
from random import randint, random
import sys,os
import traceback

def get_proxy():
	random_id      = random()
	proxy_string   = "lum-customer-hl_c487542d-zone-zone1-session-%s:hx4xvmm4p0se@zproxy.lum-superproxy.io:22225" % random_id
	proxies        = { "https" : "http://%s" % proxy_string ,"http" : "http://%s" % proxy_string}
	return proxies


def spirit_teamtravel(username,pwd,FROM,TO,FROM_DATE,TO_DATE):

	FROM_DATE_FORMAT_1 = datetime.datetime.strptime(FROM_DATE,"%Y-%m-%d").strftime("%B %d, %Y")
	FROM_DATE_FORMAT_2 = datetime.datetime.strptime(FROM_DATE,"%Y-%m-%d").strftime("%B %d")

	TO_DATE_FORMAT_1 = datetime.datetime.strptime(TO_DATE,"%Y-%m-%d").strftime("%B %d, %Y")
	TO_DATE_FORMAT_2 = datetime.datetime.strptime(TO_DATE,"%Y-%m-%d").strftime("%B %d")

	url  = "https://teamtravel.spirit.com/AjaxEmployeeLogin.aspx"

	payload             = {}
	payload["username"] = username
	payload["pwd"]      = pwd
	payload["type"]     = "NR"
	payload["isNKemp"]  = "true"


	headers  = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"}

	session  = requests.Session()

	RETRY = 0
	while 1:
		RETRY    += 1
		if RETRY == 11:
			return {"status":"error","details":"something_went_wrong","data" : []}
		proxies  = get_proxy()
		try:
			login_res = session.post(url,headers=headers,data=payload,proxies=proxies)
			if login_res.url == url:
				break
			else:
				return {"status":"error","details":"login_error","data" : []}
		except KeyboardInterrupt:
			sys.exit("Bye !")
		except:
			errMsg = traceback.format_exc()
			print('retry :',url,errMsg)

	# print("login_res :",login_res.url)

	# main_page  = "https://teamtravel.spirit.com/EmployeeTravel.aspx"
	# proxies  = get_proxy()
	# main_pags_res = session.get(main_page,headers=headers,proxies=proxies)
	# print("main_pags_res :",main_pags_res)
	# with open("main_pags_res.html","w",encoding="utf-8") as FF:
	# 	FF.write(main_pags_res.text)



	search_url  = "https://teamtravel.spirit.com/EmployeeTravel.aspx?action=search"

	payload = {}
	payload["birthdates"] = ""
	payload["lapoption"] = ""
	payload["awardFSNumber"] = ""
	payload["bookingType"] = "F"
	payload["travelType"] = "nktravel"
	payload["tripType"] = "oneWay"
	payload["businessLeisureSelect"] = "SA"
	payload["from"] = FROM
	payload["to"] = TO
	payload["departDate"] = FROM_DATE_FORMAT_1
	payload["departDateDisplay"] = FROM_DATE_FORMAT_2
	payload["returnDate"] = TO_DATE_FORMAT_1
	payload["returnDateDisplay"] = TO_DATE_FORMAT_2
	payload["travelers"] = "0"
	payload["ADT"] = "1"
	payload["INF"] = "0"
	payload["oaTravelSelect"] = ""
	payload["fromMultiCity1"] = ""
	payload["toMultiCity1"] = ""
	payload["dateMultiCity1"] = ""
	payload["dateMultiCityDisplay1"] = ""
	payload["fromMultiCity2"] = ""
	payload["toMultiCity2"] = ""
	payload["dateMultiCity2"] = ""
	payload["dateMultiCityDisplay2"] = ""
	payload["fromMultiCity3"] = ""
	payload["toMultiCity3"] = ""
	payload["dateMultiCity3"] = ""
	payload["dateMultiCityDisplay3"] = ""
	payload["fromMultiCity4"] = ""
	payload["toMultiCity4"] = ""
	payload["dateMultiCity4"] = ""
	payload["dateMultiCityDisplay4"] = ""


	all_data = []

	RETRY = 0
	while 1:
		RETRY    += 1
		if RETRY == 11:
			return {"status":"error","details":"something_went_wrong","data" : []}
		proxies  = get_proxy()
		try:
			search_res = session.post(search_url,headers=headers,data=payload,proxies=proxies)
			break
		except KeyboardInterrupt:
			sys.exit("Bye !")
		except:
			print('retry :',search_url)


	# with open("search_res.html","w",encoding="utf-8") as FF:
	# 	FF.write(search_res.text)

	if "We're sorry, there are no seats available for the selected date." in search_res.text:
		return {"status":"error","details":"no_seats_available","data" : []}

	search_soup = bs(search_res.content,"lxml",from_encoding="utf-8")

	all_rows    = search_soup.find_all("div",{"class":"rowsMarket1"})

	for row in all_rows:

		contents        = row.find_all("div",{"class":"depart"})[0].find("div").contents
		for CONTENT in contents:
			if "AM" in CONTENT or "PM" in CONTENT:
				depart = CONTENT
				break
		contents        = row.find_all("div",{"class":"arrive"})[0].find("div").contents
		for CONTENT in contents:
			if "AM" in CONTENT or "PM" in CONTENT:
				arrive = CONTENT
				break

		flights       = []

		fligh_numbers = row.find_all("a",{"class":"flightNumberLink"})
		all_routing   = row.find_all("div",{"class":"col-sm-12"})[3].find_all("td")
		all_seats     = row.find_all("div",{"class":"col-sm-12"})[4].find_all("td")

		for (FLIGHT_NUM_BLOC,ROOTING_BLOC, SEATS_BLOC) in zip(fligh_numbers,all_routing,all_seats):

			flight_num = FLIGHT_NUM_BLOC.text.replace(" ","").replace(" ","") .strip()
			rooting    = ROOTING_BLOC.text.replace("\u00a0","").strip()
			seats      = SEATS_BLOC.text.strip()
			# print(flight_num,seats)

			flight_dic = {"flight_number":flight_num,"seats":seats,"route":rooting}
			flights.append(flight_dic)
		
		row_dic = {"depart":depart,"arrive":arrive,"flights":flights}
		all_data.append(row_dic)
	
	print(all_data)



	return {"status":"success","details":None,"data" : all_data}

# username  = "62873"
# pwd       = "4$uIqT%UoB2GRPJ"
# FROM      = "FLL"
# TO        = "BWI"
# FROM_DATE = "2021-06-30"
# TO_DATE   = "2021-06-30"


# RET_DIC = spirit_teamtravel(username,pwd,FROM,TO,FROM_DATE,TO_DATE)

# print(RET_DIC)