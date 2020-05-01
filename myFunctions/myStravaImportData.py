import requests
import urllib3
import myFunctions.myPickle as myPickle
import myFunctions.myCalendarMap as myCalendarmap
import myFunctions.foliumLeaflet as flmap
import myFunctions.myHeatMap as myHeatmap
import matplotlib as mpl
import matplotlib.pyplot as plt
import datetime as datetime


class stravaInfo:

    """
    Class to contain all the strava data manipulation
    
    Attributes:
        stravaData (list): All strava data
        subsetData (list): Subsets of strava data usually used for manipulation later
    """
    
    stravaData = []
    subsetData = []
    
    def __init__(self,arg,readNewDataFlag=True,pickleFile="./vars/myData.pickle"):
        """
        Initialize the class
        
        Args:
            arg (dict): Dictionary arguments for the payload see example of this in the getAllActivities method.
            readNewDataFlag (bool, optional): Flag to retreave new data
            pickleFile (str, optional): Retreave data from the saved pickle file
        """
        print('Active')
        if readNewDataFlag:
            self.stravaData = self.getAllActivities(arg)
            myPickle.mySavePickle(pickleFile,self.stravaData)
        else:
            self.stravaData = myPickle.myLoadPickle(pickleFile)

    def getAllActivities(self,payload):
        """
        Get all activities from stava using API called to strava server
        
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

    def getActivityByDateRange(self,sessionsData,startDate,endDate,excludeDates=[],includeArea=['Toronto']):
        """        
        Get a subset of activities from a certain date range.
        
        Args:
            sessionsData (dict): All strava activity
            startDate (str): Start date of activity to be obtained
            endDate (str): End date of activity to be obtained
            excludeDates (list, optional): List of dates to be ignored
            includeArea (list, optional): String of areas to be included in the data
        
        Returns:
            dict: Dictionary of the activities between the specified date range
        """
        # get all the dates within the specified start and end dates
        dateRanges = self.allDatesStartEnd(startDate,endDate)

        if len(sessionsData)==0:
            sessionsData=self.stravaData

        # loop through activity and add only if it occurs between the dates
        activityBetweenDates = []
        for ses in sessionsData:
            sesDate = ses['start_date'].split('T')[0]

            if sesDate in excludeDates:
                continue

            if sesDate in dateRanges:
                for area in includeArea:
                    if area in ses['timezone']:
                        activityBetweenDates.append(ses)

        self.subsetData = activityBetweenDates

        return activityBetweenDates


    def allDatesStartEnd(self,sDate,eDate):
        """
        Utility function to get all the dates between two dates.

        Args:
            sDate (str): Start date
            eDate (str): End date
        
        Returns:
            list: List of all dates between the start and end dates.
        """
        allDatesInRange = []
        
        sDate = datetime.datetime.strptime(sDate, "%Y-%m-%d")
        eDate = datetime.datetime.strptime(eDate, "%Y-%m-%d")
        deltaDates = eDate - sDate

        for i in range(deltaDates.days+1):
            dayInRange = sDate+datetime.timedelta(days=i)
            dayInRangeString = dayInRange.strftime("%Y-%m-%d")
            allDatesInRange.append(dayInRangeString)
            
        return allDatesInRange  

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
        """
        Get only a specific type of data. 
        * 'Run' - running data
        * 'Ride' - biking data

        Args:
            activityType (str, optional): String of the activity
        """
        typeData = []

        for activity in self.stravaData:
            if(activity["type"]==activityType):
                typeData.append(activity)

        self.subsetData = typeData


    def drawRoutesMap(self,mapArgs,saveMap=False,saveMapName='./outFile/routeMap.html',sessionsData = []):
        """
        Draws the routes on a map



        Args:
            mapArgs (TYPE): These are the map parameters for drawing the sessesions::

            myMapLinesArgs = {
                'tiles': 'Cartodb Positron',
                'zoom': 3,
                'lineWeight': 3,
                'lineCol':'#3388ff'
                }

            saveMap (bool, optional): 
            saveMapName (str, optional): File name or lacation to save the map ``(.html)``
            sessionsData (list, optional): If no sessions are passed then the subset sessions are used to create the map
        
        Returns:
            folium map: Returns the foloium map of the sessions
        """
        if len(sessionsData)==0:
            sessionsData = self.subsetData

        routeMap = flmap.drawSessions(sessionsData,mapArgs)

        if saveMap:
            flmap.saveMap(routeMap,saveMapName)

        return routeMap

    
    def DrawHeatMap(self,sessionsData = [],heatmap_radius = 5,heatmap_blur = 5,saveMap=False,saveMapName='./outFile/heatMap.html'):
        """

        Draws the heat map of the seesions
        
        Args:
            sessionsData (list, optional): List of the session data
            heatmap_radius (int, optional): Radius of the heat maps
            heatmap_blur (int, optional): Blurring effect of the heat map
            saveMap (bool, optional): Flag to save the map or not
            saveMapName (str, optional): File name or lacation to save the map ``(.html)``
        
        Returns:
            folium map: Returns the foloium map of the sessions
        """
        if len(sessionsData)==0:
            sessionsData = self.subsetData

        heatMap = myHeatmap.getHeatMap(sessionsData,heatmap_radius = 5,heatmap_blur = 5)

        if saveMap:
            myHeatmap.saveMap(heatMap,saveMapName)
        return heatMap



    def drawCalendarmap(self,sessionsData=[],start=None,end=None,edgecolor='black',mean=False,saveImageFlag=False,saveImageName='./outFile/calendarMap.svg'):        
        """
        Creates a calendar map of sessions from the specified start and end dates.

        Args:
            sessionsData (list, optional): List of sessions to be used to draw on the map
            start (None, optional): String for the start date
            end (None, optional): String for the end date
            edgecolor (str, optional): Colour of the edeges
            mean (bool, optional): NEED TO CHECK
            saveImageFlag (bool, optional): Flag to save the map or not
            saveImageName (str, optional): File name or lacation to save the map ``(.html)``

        Todo:
            * Check what I used the mean for.
        """
        # Transform the current data into a series data used for plotting
        if len(sessionsData)==0:
            sessionsData = self.subsetData
            
        seriesData = myCalendarmap.getPandasSeriesData(sessionsData)

        # Create the figure. For the aspect ratio, one year is 7 days by 53 weeks.
        # We widen it further to account for the tick labels and color bar.
        with plt.style.context('dark_background'):
            figsize = plt.figaspect(7 / 56)
            fig = plt.figure(figsize=figsize,dpi=300)
            #inchesPerFeet = 12
            #w = 3*inchesPerFeet
            #h = 2*inchesPerFeet
            #d = 300
            #fig = plt.figure(1,figsize=(w, h), dpi=d)

            divisions = 4

            # Plot the heatmap with a color bar.
            ax = myCalendarmap.date_heatmap(seriesData.div(divisions), 
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
