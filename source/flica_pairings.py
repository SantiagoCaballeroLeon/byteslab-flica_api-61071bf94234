import requests
from bs4 import BeautifulSoup as bs
import sys
import os
import time
import datetime
import json
from source.flica_functions import login_flica,get_proxy
from random import choice


def get_pairing(user,password,pairing,DATE,headers):

	(cookies,ret_url,status_code,BCID_DIC,account_type,BCID_DIC_OT)  = login_flica(user,password,headers)

	if cookies == None:
		return {"message":"maximum retrial reached for account %s %s" % (user,password)}
	if "FailedAttempt" in ret_url:
		return {"message":"could_not_login"}
	if account_type == "other":
		return {"message":"unknown_account_type"}
	
	pairing_url   = "https://spirit.flica.net/full/rbcpair.cgi?PID=%s&DATE=%s" % (pairing,DATE)

	while 1:
		try:
			proxies      = get_proxy()
			with requests.Session() as session:
				pairing_res  = session.get(pairing_url,proxies=proxies,timeout=15,cookies=cookies)
			break
		except:
			print('retry :',pairing_url)

	
	
	pairing_soup = bs(pairing_res.content,"lxml")

	table        = pairing_soup.find_all('table',{'style':'width: 100%; font-size: 8pt;'})[0]

	# TEST FIRST ROW IF IT HAS Pairing Canceled OR EQUIVALENT :
	try:
		line_1        = table.find_all('tr')[0]
		line_1_col_1  = line_1.find_all('td')[0].text
		flight_num    = line_1_col_1.split(':')[0].strip()
		flight_date_0 = line_1_col_1.split(':')[1].strip()
	except IndexError:
		line_1        = table.find_all('tr')[0]
		line_1.extract()

	days_list     = []
	table_dic     = {}
	line_1        = table.find_all('tr')[0]
	line_1_col_1  = line_1.find_all('td')[0].text
	flight_num    = line_1_col_1.split(':')[0].strip()
	flight_date_0 = line_1_col_1.split(':')[1].strip()
	# check_month   =  datetime.datetime.strptime(flight_date_0,'%d%b').strftime('%m')
	check_month   =  str(time.strptime(flight_date_0,'%d%b')[1]).zfill(2)

	year1         = datetime.datetime.strptime(DATE,'%Y%m%d').strftime('%y')

	date_obj      = datetime.datetime.strptime(flight_date_0+'-'+year1, '%d%b-%y')
	base_report   = line_1.find_all('td')[2].text.split(':')[1].strip()
	flight_date   = date_obj.strftime('%Y-%m-%d')
	table_dic['pairing_id']    = flight_num
	table_dic['start_day']     = flight_date
	table_dic['base_report']   = base_report

	legs_list = []
	day_dic   = {}
	all_flights             = table.find_all('tr')[2].find_all('table')[0].find_all('tr')
	total_pairing_row       = table.find_all('tr')[2].find_all('table')[0].find_all('tr',{'class':'bold'})[0].find_all('td')
	
	pairing_total_block     = total_pairing_row[2].text.strip()
	pairing_total_deadHead  = total_pairing_row[3].text.strip()
	pairing_total_credit    = total_pairing_row[5].text.strip()
	pairing_total_duty      = total_pairing_row[6].text.strip()
	table_dic['total_block']    = pairing_total_block
	table_dic['total_credit']   = pairing_total_credit
	table_dic['total_duty']     = pairing_total_duty
	table_dic['total_deadHead'] = pairing_total_deadHead
	
	for FLI in all_flights:
		try:
			FLI_CLASS      = FLI['class'][0]

			if FLI_CLASS == 'nowrap':
				FLI_cols       = FLI.find_all('td')
				leg_dic     = {}
				flight_day     = FLI_cols[0].text.strip()
				if flight_day == 'MO':
					flight_day = 'Monday'
				if flight_day == 'TU':
					flight_day = 'Tuesday'
				if flight_day == 'WE':
					flight_day = 'Wednesday'
				if flight_day == 'TH':
					flight_day = 'Thursday'
				if flight_day == 'FR':
					flight_day = 'Friday'
				if flight_day == 'SA':
					flight_day = 'Saturday'
				if flight_day == 'SU':
					flight_day = 'Sunday'

				flight_day_num = FLI_cols[1].text.strip()
				deadHead       = FLI_cols[2].text.strip()
				airplane_change= FLI_cols[3].text.strip()
				if '*' in airplane_change:
					airplane_change = True
				else:
					airplane_change = False
				flight_number  = FLI_cols[4].text.strip()
				from_to        = FLI_cols[5].text.strip()
				FLI_FROM       = from_to.split('-')[0].strip()
				FLI_TO         = from_to.split('-')[1].strip()
				DEPARTURE      = datetime.datetime.strptime(FLI_cols[6].text.strip(), '%H%M')
				DEPARTURE      = DEPARTURE.strftime('%H:%M')
				ARRIVAL        = datetime.datetime.strptime(FLI_cols[7].text.strip(), '%H%M')
				ARRIVAL        = ARRIVAL.strftime('%H:%M')
				DURATION       = FLI_cols[8].text.strip()
				DURATION       = DURATION[0:2]+':'+DURATION[2:]
				GROUND         = FLI_cols[9].text.strip()
				RLS            = FLI_cols[10].text.strip()

				try:
					total_block         = FLI_cols[-6].text.strip()
					total_deadHead_day  = FLI_cols[-5].text.strip()
					total_credit        = FLI_cols[-3].text.strip()
					total_duty          = FLI_cols[-2].text.strip()
					try:
						layover      = FLI_cols[-1].text.strip().split()[0].strip()
						layover_time = FLI_cols[-1].text.strip().split()[1].strip()
					except:
						layover      = ''
						layover_time = ''
					totals_day_dic = {'total_block':total_block,'total_credit':total_credit,'total_duty':total_duty,"total_deadHead":total_deadHead_day}
				except:
					pass

				leg_dic['flight_day_name']  = flight_day
				leg_dic['flight_day']       = flight_day_num
				leg_dic['flight_number']    = flight_number
				leg_dic['departure']        = DEPARTURE
				leg_dic['arrival']          = ARRIVAL
				leg_dic['departure_city']   = FLI_FROM
				leg_dic['arrival_city']     = FLI_TO
				leg_dic['flight_duration']  = DURATION
				leg_dic['airplane_change']  = airplane_change
				leg_dic['ground_time']      = GROUND
				leg_dic['deadhead']         = deadHead
				leg_dic['release']          = RLS
				legs_list.append(leg_dic)
		# end line:
		except:
			hotel_row_dic  = {}
			rept           = ''
			FLI_cols       = FLI.find_all('td')
			DEND_COL       = FLI_cols[1]
			DEND           = DEND_COL.text.strip()
			if 'TRIP RIG' in DEND:
				strongs     = DEND_COL.find_all('strong')
				for STRONG in strongs:
					if "TRIP RIG" in STRONG.text:
						trip_rig    = STRONG.text.split('TRIP RIG')[1].replace(':','').strip()
				table_dic['trip_rig'] = trip_rig
			if 'T.A.F.B.' in DEND:
				total_tafb  = DEND_COL.find_all('strong')[0].text.split('T.A.F.B.')[1].replace(':','').strip()
				table_dic['total_tafb'] = total_tafb
				DEND        = DEND.split('T.A.F.B.')[0].replace('\n','').strip().split('D-END:')[1].strip()
			if 'REPT:' in DEND:
				rept  = DEND.split('REPT:')[1].strip()
				if '(' in DEND:
					DEND  = DEND.split('REPT:')[0].replace('\n','').strip().split('D-END:')[1].split('(')[0].strip()
				else:
					DEND  = DEND.split('REPT:')[0].replace('\n','').strip().split('D-END:')[1].strip()
			DEND_2 = FLI_cols[2].text.strip()
			try:
				DEND_3 = FLI_cols[3].text.strip()
			except:
				DEND_3 = ''
			hotel_row_dic['hotel_name']    = DEND_2
			hotel_row_dic['hotel_phone']   = DEND_3
			
			day_dic['legs']          = legs_list
			day_dic['hotel_info']    = hotel_row_dic
			day_dic['totals']        = totals_day_dic
			day_dic['layover']       = layover
			day_dic['layover_time']  = layover_time
			day_dic['end']           = DEND
			day_dic['report']        = rept
			days_list.append(dict(day_dic))

			legs_list = []

	# MOVING REPORT TO NEXT DAY :
	days_list_copy    = [dict(II_dic) for II_dic in list(days_list) ]
	for DAY in days_list_copy:
		if days_list.index(DAY) == 0:
			DAY['report'] = ""
		else:
			DAY['report'] = days_list[days_list.index(DAY)-1 ]['report'] 
	
	table_dic['days'] = days_list_copy


	#crew :
	crew_list = []
	all_sub_tables  = table.find_all('table')
	for sub_table in all_sub_tables:
		first_row = sub_table.find_all('tr')[0].text
		if 'Crew:' in first_row:
			crew_line = sub_table.find_all('tr')[-1].find_all('td')
			crew_line_2 = sub_table.find_all('tr')[-2].find_all('td')
			break
	for XX in range(2):
		if XX == 0:
			crew_line_to_use = crew_line
		elif XX == 1:
			crew_line_to_use = crew_line_2
		count    = -1
		count_2  = -1
		crew_dic = {}
		while 1:
			try:
				count   += 1
				count_2 += 1
				if count == 1:
					crew_type = crew_line_to_use[count_2].text.strip()
				elif count == 2:
					crew_id = crew_line_to_use[count_2].text.strip()
				elif count == 3:
					crew_name = crew_line_to_use[count_2].text.strip()
					count = -1
					crew_dic  = {'crew_type':crew_type, 'crew_id':crew_id, 'crew_name':crew_name}
					crew_list.append(crew_dic)
			except:
				break

	table_dic['crew'] = crew_list

	DATA_DIC = {}
	DATA_DIC[flight_num+'_'+flight_date_0]     = table_dic

	return DATA_DIC
		