import requests
import urllib3
import myFunctions.myPickle as myPickle
import myFunctions.myHeatmap as myHeatmap
import matplotlib as mpl
import matplotlib.pyplot as plt

class stravaInfo:

	stravaData = []
	subsetData = []
	
	def __init__(self,arg,readNewDataFlag=True,pickleFile="./vars/myData.pickle"):
		print('Active')
		if readNewDataFlag:
			self.stravaData = self.getAllActivities(arg)
			myPickle.mySavePickle(pickleFile,self.stravaData)
		else:
			self.stravaData = myPickle.myLoadPickle(pickleFile)

	def getAllActivities(self,payload):
		"""
		Read a specified .def DECI file into the class.  Note that the .def is the txt file version of the output of DECI.

		Parameters:
			payload (dict): The dictionary for the payload for the API an example can be seen below

		Returns:
			myEntireData (list): A list of dictionaries for each session
		
		Example:
			This is an example on how to use it::
		
				payload = {
					 'client_id': "xxx",
					 'client_secret': 'xxxxx',
					 'refresh_token': 'xxxx',
					 'grant_type': "refresh_token",
					 'f': 'json'
				 }
		
		""" 
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
		Get the date of a given activities

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

	def getTypeData(self,activityType='Run'):
		typeData = []

		for activity in self.stravaData:
			if(activity["type"]==activityType):
				typeData.append(activity)

		self.subsetData = typeData
	

	def drawHeatmap(self,start=None,end=None,edgecolor='black',mean=False,saveImageFlag=False,saveImageName='./outFile/heatmap.svg'):
		# Transform the current data into a series data used for plotting
		seriesData = myHeatmap.getPandasSeriesData(self.subsetData)

		# Create the figure. For the aspect ratio, one year is 7 days by 53 weeks.
		# We widen it further to account for the tick labels and color bar.
		figsize = plt.figaspect(7 / 56)
		fig = plt.figure(figsize=figsize)

		divisions = 4

		# Plot the heatmap with a color bar.
		ax = myHeatmap.date_heatmap(seriesData.div(divisions), 
						  start=start, 
						  end=end,
						  edgecolor=edgecolor)

		# Use a discrete color map with 5 colors (the data ranges from 0 to 4).
		# Extending the color limits by 0.5 aligns the ticks in the color bar.
		cmap = mpl.cm.get_cmap('Blues', divisions)
		plt.set_cmap(cmap)

		#plt.colorbar(ticks=range(divisions), pad=0.02)
		colbar = plt.colorbar(ticks=range(divisions), pad=0.02)
		plt.clim(-0.5, divisions-0.5)
		colbar.ax.set_yticklabels(['Rest', 'Tempo', 'Easy/Track','Long'])

		# Force the cells to be square. If this is set, the size of the color bar
		# may look weird compared to the size of the heatmap. That can be corrected
		# by the aspect ratio of the figure or scale of the color bar.
		ax.set_aspect('equal')

		if saveImageFlag:
			fig.savefig(saveImageName, bbox_inches='tight')