import requests
from bs4 import BeautifulSoup as bs
import sys
import os
import time
import datetime
import json
import csv
import urllib.parse
from source.flica_functions import get_proxy
from random import choice
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def parse_flight(result_soup,al,fn,date):

	FLIGHT_DIC      = {}
	# STATUS :
	FlightStatus    = result_soup.find_all('div',{'class':'dataFlightStatus'})[0].find_all('div',{'class':'labelFlightStatusValue'})[0].text.strip()
	
	# PREVIOUS FLIGHT :
	previous_flight_dic   = {}
	try:
		all_blocs_headers = result_soup.find_all('div')
		INDEX = -1
		for BLOC_HEADER in all_blocs_headers:
			INDEX += 1
			BLOC_HEADER_TEXT = BLOC_HEADER.text.strip()
			if BLOC_HEADER_TEXT == "Aircraft's Previous Flight":
				previous_flight_index = INDEX
				break
		previous_flight_bloc = all_blocs_headers[previous_flight_index+1]
		# previous_flight      = previous_flight_bloc.find_all('td',{'class':"FlightTrackerData"})[0].text.strip()
		previous_flight_data = previous_flight_bloc.find_all('form',{'action':'/TravelTools/FlightTrackerQueryResults.asp'})[0]
		pf_al                = previous_flight_data.find_all('input',{'name':'al'})[0]['value']
		pf_fn                = previous_flight_data.find_all('input',{'name':'fn'})[0]['value']
		pf_date              = previous_flight_data.find_all('input',{'name':'whendate'})[0]['value']
		previous_flight_dic  = {"al":pf_al,"fn":pf_fn,"date":pf_date}
	except:
		pass

	# DEPARTURE / ARRIVAL :
	bloc_dic        = {"departure":"tbl_dep","arrival":"tbl_arr"}

	for bloc,b_class in bloc_dic.items():

		dep_dic         = {}
		tbl_dep         = result_soup.find_all('table',{'id':b_class})[0]
		tbl_dep_rows    = tbl_dep.find_all('tr')
		for ROW in tbl_dep_rows:
			try:
				ROW_KEY  = ROW.find_all('td',{'class':'search-results-table-hdr'})[0].text
				ROW_KEY  = ROW_KEY.replace(':','').strip()
			except:
				continue
			ROW_VALUE  = ROW.find_all('td',{'class':'FlightTrackerData'})[0].text.strip()
			if "_fvYyyyMmDdLast" in ROW_VALUE:
				ROW_VALUE  = ROW_VALUE.split('_fvYyyyMmDdLast')[0].replace('\r\n',"").strip()
			dep_dic[ROW_KEY] = ROW_VALUE
			# print(ROW_VALUE)
		
		try:
			del dep_dic["More Airport Info"]
		except:
			pass
		try:
			del dep_dic["Local Services"]
		except:
			pass
		
		# print(dep_dic)

		mod_dep_dic  = {}

		airport_name = None
		airport_code = None
		scheduled_time = None
		scheduled_date = None
		takeoff_time  = None
		takeoff_date   = None
		estimated_time = None
		estimated_date = None
		terminal_gate  = None
		time_remaining = None
		left_gate_time = None
		baggage_claim  = None

		for K,V in dep_dic.items():
			if K == "Airport":
				airport_data  = csv.reader([V.split('ftGetAirport(')[1].split(');')[0]])
				airport_data  = list(airport_data)[0]
				airport_name  = airport_data[1]+", "+ airport_data[2]
				airport_code  = airport_data[0]
			if K == "Scheduled Time":
				# data_f          = datetime.datetime.strptime(V,"%I:%M %p,\xa0%b\xa0%d")
				data_f          = time.strptime(V,"%I:%M %p,\xa0%b\xa0%d")
				# scheduled_time  = data_f.strftime('%H:%M')
				# scheduled_date  = data_f.strftime('%m/%d')
				scheduled_time  = str(data_f[3]).zfill(2) +":"+str(data_f[4]).zfill(2)
				scheduled_date  = str(data_f[1]).zfill(2)+"/"+str(data_f[2]).zfill(2)

			if K == "Takeoff Time":
				# data_f          = datetime.datetime.strptime(V,"%I:%M %p,\xa0%b\xa0%d")
				data_f          = time.strptime(V,"%I:%M %p,\xa0%b\xa0%d")
				# takeoff_time    = data_f.strftime('%H:%M')
				# takeoff_date    = data_f.strftime('%m/%d')
				takeoff_time  = str(data_f[3]).zfill(2)+":"+str(data_f[4]).zfill(2)
				takeoff_date  = str(data_f[1]).zfill(2)+"/"+str(data_f[2]).zfill(2)

			if K == "Estimated Time":
				# data_f            = datetime.datetime.strptime(V,"%I:%M %p,\xa0%b\xa0%d")
				data_f          = time.strptime(V,"%I:%M %p,\xa0%b\xa0%d")
				# estimated_time    = data_f.strftime('%H:%M')
				# estimated_date    = data_f.strftime('%m/%d')
				estimated_time  = str(data_f[3]).zfill(2)+":"+str(data_f[4]).zfill(2)
				estimated_date  = str(data_f[1]).zfill(2)+"/"+str(data_f[2]).zfill(2)
			if K == "Terminal - Gate":
				terminal_gate  = V.strip()

			if K == "Time Remaining":
				time_remaining = V.strip()

			if K == "Left Gate Time":
				left_gate_time = V.strip()

			if K == "Baggage Claim":
				baggage_claim = V.strip()
		
	
		mod_dep_dic['airport_name']    = airport_name
		mod_dep_dic['airport_code']    = airport_code
		mod_dep_dic['scheduled_time']  = scheduled_time
		mod_dep_dic['scheduled_date']  = scheduled_date
		mod_dep_dic['takeoff_time']    = takeoff_time
		mod_dep_dic['takeoff_date']    = takeoff_date
		mod_dep_dic['estimated_time']  = estimated_time
		mod_dep_dic['estimated_date']  = estimated_date
		mod_dep_dic['terminal_gate']   = terminal_gate
		mod_dep_dic['time_remaining']  = time_remaining
		mod_dep_dic['left_gate_time']  = left_gate_time
		mod_dep_dic['baggage_claim']   = baggage_claim

		if bloc == "departure":
			dep_scheduled_time = scheduled_time

		FLIGHT_DIC[bloc] = mod_dep_dic

	FLIGHT_DIC['flightStatus']    = FlightStatus
	FLIGHT_DIC['previous_flight'] = previous_flight_dic
	FLIGHT_DIC['airline']         = al
	FLIGHT_DIC['flightNumber']    = fn
	FLIGHT_DIC['flightDate']      = date
	FID                           = al+fn+'_'+dep_scheduled_time
	FLIGHT_DIC['id']              = FID
	# print(FLIGHT_DIC)
	return (FLIGHT_DIC,FID)




def get_flight_data(al,fn,date,headers):



	
	query_url       = "https://www.flightview.com/TravelTools/FlightTrackerQueryResults.asp"


	payload         = {
"qtype": "sfi",
#"sfw": "/FV/TravelTools/Main",
"sfw": "/FV/Home/Main",
"whenArrDep": "dep",
"namal": al,
"al": al,
"fn": fn,
"whenDate": date,
"input": "Track Flight"
	}

	# print("payload :",payload)
	# print("query_url :",query_url)
	
	# print("headers :",headers)

	RETRY = 0
	while 1:
		RETRY += 1
		if RETRY == 11:
			return []
		proxies      = get_proxy()
		try:
			with requests.Session() as session:
				query_res       = session.post(query_url,headers=headers,data=payload,timeout=15,proxies=proxies,verify=False)
			break
		except:
			print("retry :",query_url)

	# # DEBUG :
	# with open('res.html','w',encoding="utf-8") as FFFF:
	# 	FFFF.write(query_res.text)

	query_soup      = bs(query_res.content, "lxml")
	
	# [s.extract() for s in query_soup('script')]
	for hidden in query_soup.body.find_all(style='display:none'):
		hidden.decompose()
	for hidden in query_soup.body.find_all(class_='ftResultIndividualFlightViewLive'):
		hidden.decompose()

	searchResults   = query_soup.find_all('div',{'id':'search-results'})

	if len(searchResults) > 0:
		# ONE RESULT PAGE :
		RESULT_SOUP                               = searchResults[0]
		FLIGHT_FULL_LIST                          = []
		(FLIGHT_DIC,FID)                          = parse_flight(RESULT_SOUP,al,fn,date)
		FLIGHT_FULL_LIST.append(FLIGHT_DIC)
		
	else:
		# MULTIPLE RESULTS PAGE :

		FLIGHT_FULL_LIST  = []
		try:
			FlightTrackerList = query_soup.find_all('table',{"class":"FlightTrackerList"})[0].find_all('tr',{"class":["FlightTrackerListRowOdd","FlightTrackerListRowEven"]})
		except:
			return {"message":"no_results"}
		for FLIGHT in FlightTrackerList:

			qtype         = FLIGHT.find_all('input',{'name':'qtype'})[0]['value']
			whenArrDep    = FLIGHT.find_all('input',{'name':'whenArrDep'})[0]['value']
			depap         = FLIGHT.find_all('input',{'name':'depap'})[0]['value']
			whenDate      = FLIGHT.find_all('input',{'name':'whenDate'})[0]['value']

			payload_f         = {
		"qtype": qtype,
		"whenArrDep": whenArrDep,
		"depap": depap,
		"whenDate": whenDate,
		"al": al,
		"fn": fn
			}

			RETRY = 0
			while 1:
				RETRY += 1
				if RETRY == 11:
					return []
				proxies      = get_proxy()
				try:
					with requests.Session() as session:
						query_res_f       = session.post(query_url,headers=headers,data=payload_f,timeout=15,proxies=proxies,verify=False)
					break
				except:
					print('retry :',query_url)

			query_soup_f      = bs(query_res_f.content, "lxml")

	
			# [s.extract() for s in query_soup('script')]
			for hidden in query_soup_f.body.find_all(style='display:none'):
				hidden.decompose()
			for hidden in query_soup_f.body.find_all(class_='ftResultIndividualFlightViewLive'):
				hidden.decompose()

			searchResults_f   = query_soup_f.find_all('div',{'id':'search-results'})


			RESULT_SOUP_f                             = searchResults_f[0]
			(FLIGHT_DIC,FID)                          = parse_flight(RESULT_SOUP_f,al,fn,date)
			FLIGHT_FULL_LIST.append(FLIGHT_DIC)
			
	
	return FLIGHT_FULL_LIST
