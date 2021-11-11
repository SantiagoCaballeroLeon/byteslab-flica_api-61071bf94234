from gevent import monkey
monkey.patch_all()
from flask import Flask
from flask import jsonify
from flask import request
from gevent import pywsgi
# from waitress import serve
import requests
from bs4 import BeautifulSoup as bs
import sys
import os
import time
import datetime
import json
from source.flica_schedule import scrape_flica
from source.flica_opentime import open_time_table
from source.flica_pairings import get_pairing
from source.flica_opentime_bidding import get_requests,add,drop,DropToTB,AddFromTB,cancel_request,swap
from source.flightview import get_flight_data
from source.flica_user_info import get_user_info
from source.spirit_teamtravel import spirit_teamtravel


app = Flask(__name__)

@app.route('/flica')
def start():
	user  = request.args.get('user', "").strip()
	pswd  = request.args.get('password', "").strip()
	month  = request.args.get('month', None)
	
	SF     = scrape_flica(user,pswd,month,headers)
	if SF == 10:
		res_dic  = {"message":"could_not_login"}
	elif SF == 20:
		res_dic  = {"message":"unknown_account_type"}
	elif SF == 30:
		res_dic  = {"message":"schedule_not_available"}
	elif SF == 40:
		res_dic = {"message":"maximum retrial reached for account %s %s" % (user,pswd)}
	else:
		(ret_url,status_code,DATA_DIC,schedule_list,monthly_totalBlock,monthly_totalCredit,days_off,YTD) =  SF
		res_dic  = {'month':month,'message':"success",'pairings':DATA_DIC,'schedule_view':schedule_list,'monthly_total_block':monthly_totalBlock,\
'monthly_total_credit':monthly_totalCredit,'days_off':days_off,'ytd':YTD}

	return jsonify(res_dic)

@app.route('/opentime')
def start_opentime():
	user    = request.args.get('user', "").strip()
	pswd    = request.args.get('password', "").strip()
	ot_date = request.args.get('ot_date', None)

	LIST_opentime = open_time_table(user,pswd,headers,ot_date)
	return jsonify(LIST_opentime)

@app.route('/pairing')
def start_pairing():
	user    = request.args.get('user', "").strip()
	pswd    = request.args.get('password', "").strip()
	pairing = request.args.get('pairing', None)
	date    = request.args.get('date', None)

	DATA = get_pairing(user,pswd,pairing,date,headers)
	return jsonify(DATA)


@app.route('/requests')
def start_requests():
	user    = request.args.get('user', "").strip()
	pswd    = request.args.get('password', "").strip()
	ot_date = request.args.get('ot_date', None)

	DATA    = get_requests(user,pswd,headers,ot_date)
	return jsonify(DATA)

@app.route('/cancel_req')
def cancel_req():
	user       = request.args.get('user', "").strip()
	pswd       = request.args.get('password', "").strip()
	request_id = request.args.get('request_id', None)
	ot_date    = request.args.get('ot_date', None)

	DATA    = cancel_request(user,pswd,request_id,headers,ot_date)
	return jsonify(DATA)

@app.route('/add')
def start_add():
	user            = request.args.get('user', "").strip()
	pswd            = request.args.get('password', "").strip()
	pairing_date    = request.args.get('pairing_date', None)
	prio            = request.args.get('prio', "")
	ot_date         = request.args.get('ot_date', None)

	DATA            = add(user,pswd,pairing_date,headers,prio,ot_date)
	return jsonify(DATA)

@app.route('/drop')
def start_drop():
	user            = request.args.get('user', "").strip()
	pswd            = request.args.get('password', "").strip()
	pairing_date    = request.args.get('pairing_date', None)
	prio            = request.args.get('prio', "")
	ot_date         = request.args.get('ot_date', None)

	DATA           = drop(user,pswd,pairing_date,headers,prio,ot_date)
	return jsonify(DATA)

@app.route('/swap')
def start_swap():
	user                = request.args.get('user', "").strip()
	pswd                = request.args.get('password', "").strip()
	all_pairing_date    = request.args.get('pairing_date', None)
	all_to_pairing_date = request.args.get('to_pairing_date', None)
	prio                = request.args.get('prio', "")
	ot_date             = request.args.get('ot_date', None)
	as_separate_request = request.args.get('as_separate_request', "no")

	DATA                = swap(user,pswd,all_pairing_date,all_to_pairing_date,headers,prio,ot_date,as_separate_request)
	return jsonify(DATA)

@app.route('/addFromTB')
def start_add_from_tb():
	user                 = request.args.get('user', "").strip()
	pswd                 = request.args.get('password', "").strip()
	pairing_date         = request.args.get('pairing_date', None)
	tb_monthyear         = request.args.get('tb_monthyear', None)

	DATA                 = AddFromTB(user,pswd,pairing_date,headers,tb_monthyear)
	return jsonify(DATA)

@app.route('/DropToTB')
def start_drop_to_tb():
	user            = request.args.get('user', "").strip()
	pswd            = request.args.get('password', "").strip()
	pairing_date    = request.args.get('pairing_date', None)
	tb_monthyear    = request.args.get('tb_monthyear', None)

	DATA            = DropToTB(user,pswd,pairing_date,headers,tb_monthyear)
	return jsonify(DATA)

@app.route('/flight_data')
def flight_data():
	al            = request.args.get('al', None)
	fn            = request.args.get('fn', None)
	date          = request.args.get('date', None)
	
	DATA          = get_flight_data(al,fn,date,headers)
	return jsonify(DATA)

@app.route('/getUserInfo')
def getUserInfo():
	user    = request.args.get('user', "").strip()
	pswd    = request.args.get('password', "").strip()
	ot_date = request.args.get('ot_date', None)
	
	DATA    = get_user_info(user,pswd,headers,ot_date)
	return jsonify(DATA)

@app.route('/spirit_teamtravel')
def spirit_teamtravel_func():
	username    = request.args.get('user', "").strip()
	pwd         = request.args.get('password', "").strip()
	FROM        = request.args.get('from', "")
	TO          = request.args.get('to', "")
	FROM_DATE   = request.args.get('from_date', "")
	TO_DATE     = request.args.get('to_date', "")

	
	DATA    = spirit_teamtravel(username,pwd,FROM,TO,FROM_DATE,TO_DATE)
	return jsonify(DATA)


#enable port using : iptables -I INPUT -p tcp --dport 5000 -j ACCEPT
if __name__ == '__main__':
	headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'}
	## FLASK :
	# app.debug = True
	# app.run(host = '0.0.0.0',threaded=True)
	
	## WAITRESS :
	# serve(app,host ='0.0.0.0',port=5000)
	# # serve(app,host ='localhost',port=5000)   # for testing

	## GEVENT :
	pywsgi.WSGIServer(('0.0.0.0', 5000), app).serve_forever()
	#pywsgi.WSGIServer(('localhost', 5000), app).serve_forever() # LOCAL TEST
	