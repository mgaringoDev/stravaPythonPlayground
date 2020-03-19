import requests
import urllib3

class stravaInfo:

	stravaData = []
	
	def __init__(self,arg):
		print('Active')
		self.stravaData = self.getAllActivities(arg)


	def getAllActivities(self,payload):
	    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

	    auth_url = "https://www.strava.com/oauth/token"
	    activites_url = "https://www.strava.com/api/v3/athlete/activities"

	    # payload = {
	    #     'client_id': "xxx",
	    #     'client_secret': 'xxxxx',
	    #     'refresh_token': 'xxxx',
	    #     'grant_type': "refresh_token",
	    #     'f': 'json'
	    # }

	    print("Requesting Token...\n")
	    res = requests.post(auth_url, data=payload, verify=False)
	    access_token = res.json()['access_token']
	    print("Access Token = {}\n".format(access_token))
	    
	    numEntries = 1
	    pageNum = 1
	    myDataSet = []
	    while numEntries!=0:        
	        header = {'Authorization': 'Bearer ' + access_token}
	        param = {'per_page': 200, 'page': pageNum}
	        myDatasetPage = requests.get(activites_url, headers=header, params=param).json()
	        numEntries = len(myDatasetPage)
	        print("On page",str(pageNum),'there were',str(numEntries),'entries')
	        
	        if numEntries==0:
	            continue
	        
	        myDataSet.append(myDatasetPage)
	        
	        pageNum += 1
	    
	    
	    myEntireData = []
	    for myDataPage in myDataSet:
	        for entry in myDataPage:
	            myEntireData.append(entry)
	            
	    print('There are',len(myEntireData),'entries in the database')
	    
	    return myEntireData


	def getDate(activity):
		"""
		Read a specified .def DECI file into the class.  Note that the .def is the txt file version of the output of DECI.

		Parameters:
		    activity (dict): this is a dictionary of a session.  Check strava API for more detail

		Returns:
		    actYear (int): year when the activity took place
		    actMonth (int): month when the activity took place
		    actDay (int): day when the activity took place
		""" 
		actDate = activity["start_date"].split('T')[0]
		actYear = int(actDate.split('-')[0])
		actMonth = int(actDate.split('-')[1])
		actDay = int(actDate.split('-')[2])

		return actYear,actMonth,actDay