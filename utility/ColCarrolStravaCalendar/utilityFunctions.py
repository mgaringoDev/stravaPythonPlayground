import polyline

def getLocation(sessionLocation):
    lat = sessionLocation['start_latitude']
    lon = sessionLocation['start_longitude']
    
    return {"lat": lat, "long": lon}

def getRoute(sessionRoute):    
	try:
		coordinates = polyline.decode(sessionRoute['map']['summary_polyline'])
		lat,lon = map(list, zip(*coordinates))    
	except Exception as e:
		print(sessionRoute['start_date'])
		print(sessionRoute['type'])
		lat = 0.0
		lon = 0.0
		print(e)

	return {"lat": lon, "long": lat}

def getImportData(session):
    return {
            "distance": session["distance"],
            "elapsed_time": session["elapsed_time"],
            "start_time": session["start_date"][:-1],
            "sport": session["type"],
            "sub_sport": 'generic',
            "location": getLocation(session),
            "route": getRoute(session),
        }

def getPlotterData(sessionArray):
	importData = []
	for dat in sessionArray:    
	    importData.append(getImportData(dat))   

	myDataPlotter = {'activities':importData}

	return myDataPlotter
