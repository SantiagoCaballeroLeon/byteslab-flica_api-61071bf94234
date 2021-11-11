--------------------
FLICA SCHEDULE API :
--------------------

	API URL : http://140.82.27.147:5000/flica?user=[user]&password=[password]&month=[mmdd]

	EXAMPLE : http://140.82.27.147:5000/flica?user=NKS062873&password=Paytrack326&month=0619
--------------------
FLICA OPEN TIME API :
--------------------

	API URL : http://140.82.27.147:5000/opentime?user=[user]&password=[password]&ot_date=[ot_date]

	EXAMPLE : http://140.82.27.147:5000/opentime?user=NKS062873&password=Paytrack326&ot_date=jan2020

		Note : For FA accounts, ot_date could be left empty
--------------------
FLICA PAIRINGS API :
--------------------

	API URL : http://140.82.27.147:5000/pairing?user=[user]&password=[password]&pairing=[pairing]&date=[date]

		Note : [pairing] and [date] should be taken from "FLICA OPEN TIME API"
	
	EXAMPLE : http://140.82.27.147:5000/pairing?user=NKS062873&password=Paytrack326&pairing=F3078B&date=20190609

--------------------
FLICA REQUESTS     :
--------------------

	API URL : http://140.82.27.147:5000/requests?user=[user]&password=[password]&ot_date=[ot_date]

	EXAMPLE : http://140.82.27.147:5000/requests?user=NKS062873&password=Paytrack326&ot_date=jan2020

		Note : For FA accounts, ot_date could be left empty

--------------------
CANCEL REQUEST     :
--------------------

	API URL : http://140.82.27.147:5000/cancel_req?user=[user]&password=[password]&request_id=[request_id]&ot_date=[ot_date]

		Note : [request_id] should be taken from "FLICA REQUESTS"

	EXAMPLE : http://140.82.27.147:5000/cancel_req?user=NKS062873&password=Paytrack326&request_id=01D583BF:EBDA9D27:0&ot_date=jan2020

		Note : For FA accounts, ot_date could be left empty

--------------------
FLICA ADD REQUEST  :
--------------------

	API URL : http://140.82.27.147:5000/add?user=[user]&password=[password]&pairing_date=[pairing_date]&prio=[priority number]&ot_date=[ot_date]

	EXAMPLE : http://140.82.27.147:5000/add?user=NKS062873&password=Paytrack326&pairing_date=F3303:20190903&prio=3&ot_date=dec2019

		Note : For FA accounts, ot_date could be left empty

--------------------
FLICA DROP REQUEST :
--------------------

	API URL : http://140.82.27.147:5000/drop?user=[user]&password=[password]&pairing_date=[pairing_date]&prio=[priority number]&ot_date=[ot_date]

	EXAMPLE : http://140.82.27.147:5000/drop?user=NKS062873&password=Paytrack326&pairing_date=F3381:20190919&prio=2&ot_date=dec2019

		Note : For FA accounts, ot_date could be left empty

--------------------
FLICA SWAP REQUEST :
--------------------

	API URL : http://140.82.27.147:5000/swap?user=[user]&password=[password]&pairing_date=[pairing_date]&to_pairing_date=[to_pairing_date]&prio=[priority number]&ot_date=[ot_date]&as_separate_request=[as_separate_request]

	EXAMPLE : user=NKS066187&password=Ernest1301&pairing_date=O9056:20210421|O9057:20210422&to_pairing_date=O9058:20210411|O9131:20210411&prio=1&ot_date=apr2021&as_separate_request=yes

		Note : For FA accounts, ot_date could be left empty
		as_separate_request : yes/no

------------------------------------
FLICA ADD FROM TRADEBOARD REQUEST  :
------------------------------------

	API URL : http://140.82.27.147:5000/addFromTB?user=[user]&password=[password]&pairing_date=[pairing_date]&tb_monthyear=[tb_monthyear]

	EXAMPLE : http://140.82.27.147:5000/addFromTB?user=NKS062873&password=Paytrack326&pairing_date=F3303:20191018&tb_monthyear=oct2019

-----------------------------------
FLICA DROP TO TRADEBOARD REQUEST  :
-----------------------------------

	API URL : http://140.82.27.147:5000/DropToTB?user=[user]&password=[password]&pairing_date=[pairing_date]&tb_monthyear=[tb_monthyear]

	EXAMPLE : http://140.82.27.147:5000/DropToTB?user=NKS062873&password=Paytrack326&pairing_date=F3261:20190916&tb_monthyear=oct2019

------------------
FLIGHT DATA API  :
------------------

	API URL : http://140.82.27.147:5000/flight_data?al=[airline]&fn=[flight_number]&date=[flight_date]

	EXAMPLE : http://140.82.27.147:5000/flight_data?al=NK&fn=858&date=20191017

-------------------
GET USER INFO API :
-------------------

	API URL : http://140.82.27.147:5000/getUserInfo?user=[user]&password=[password]&ot_date=[ot_date]

	EXAMPLE : http://140.82.27.147:5000/getUserInfo?user=NKS062873&password=Paytrack326&ot_date=jan2020

-----------------------
SPIRIT TEAMTRAVEL API :
----------------------

	API URL : http://140.82.27.147:5000/spirit_teamtravel?user=[user]&password=[password]&from=[from]&to=[to]&from_date=[from_date]&to_date=[to_date]

	EXAMPLE : http://140.82.27.147:5000/spirit_teamtravel?user=62873&password=4$uIqT%UoB2GRPJ&from=FLL&to=BWI&from_date=2021-06-30&to_date=2021-06-30

	ERRORS :
		 {"status":"error","details":"login_error","data" : []}          : in case of wrong password

		 {"status":"error","details":"something_went_wrong","data" : []} : in case of any unknow error

		 {"data":[],"details":"no_seats_available","status":"error"}      : in case when no seats are available for the selected date


**LIST OF POSSIBLE ERRORS :**

	 1. {"message":"could_not_login"}                         : when login fails
	 2. {"message":"unknown_account_type"}                    : when the account is not neither Flight Attendant not Pilot
	 3. {"message":"schedule_not_available"}                  : when no schedule data available
	 4. {"message":"cancel_req_something_went_wrong"}         : something wrong happened when canceling a request
	 5. {"message":"BCID_not_found"}                          : when the bcid was not found when using addFromTB or DropToTB
	 6. {"message":"BCID_OT_not_found"}                       : when the bcid for opentime was not found
	 7. {"message":"ot_date_is_required_for_pilots_accounts"} : when skipping ot_date paramater in a pilot account
	 8. {"message":"opentime_data_not_available"}             : when no opentime data available 
	 9. {"message":"maximum retrial reached for account U P"} : when maximum 10 retrial done without getting data
	10. {"message":"userinfo_data_not_available"}             : when no user info data available 


