from random import randint
import polyline
import folium
import mplleaflet

def getRandomColour():
    """
    Utility function to get random Hex values

    Returns:
        hex_number (str): A hex string
    
    """ 
    random_number = randint(0,16777215)
    hex_number = str(hex(random_number))
    hex_number ='#'+ hex_number[2:]
    return hex_number

def drawSessions(rSessions,mapLinesArgs):
    """
    The main draw leaflet function to draw one or more sessions.
    Parameters:
        rSessions (list): List of one or more running sessions.  This is what myStravaImportData returns.
        mapLinesArgs (dict): A dictionary for controlling multiple drawing functions in leaflet map.  See examples below

    Returns:
        myMapSessions (obj): Returns a folium map object

    Example:
        This is an example on how to use it::
    
            sessionsToDraw = myData[:10]
            myMapLinesArgs = {
                'tiles': 'Cartodb Positron',
                'zoom': 3,
                'lineWeight': 3,
                'lineCol':'#3388ff'
                }

            drawMap = flmap.drawSessions(sessionsToDraw,myMapLinesArgs)
            drawMap
    
    """ 
    oneCol = False
    keys = mapLinesArgs.keys()
    for k in keys:
        if k == 'lineCol':
            oneCol = True
    
    # Get Data coordinates
    sessionsCoords = []
    allLon = []
    allLat = []
    for ses in rSessions:
        sessionCoords = polyline.decode(ses['map']['summary_polyline'])
        sessionsCoords.append(sessionCoords)

    for sesCo in sessionCoords:    
        allLat.append(sesCo[0])
        allLon.append(sesCo[1])

    centre = [(min(allLat) + max(allLat))/2,(min(allLon) + max(allLon))/2]

    # Create map
    myMapSessions = folium.Map(
        location=centre,
        tiles=mapLinesArgs['tiles'],
        zoom_start=mapLinesArgs['zoom']
    )

    # Add route 
    if oneCol:
        for sesCoord in sessionsCoords:
            folium.PolyLine(
                locations=sesCoord,
                color=mapLinesArgs['lineCol'],
                weight=mapLinesArgs['lineWeight'],
            ).add_to(myMapSessions)
    else:
        for sesCoord in sessionsCoords:
            folium.PolyLine(
                locations=sesCoord,
                color=getRandomColour(),
                weight=mapLinesArgs['lineWeight'],
            ).add_to(myMapSessions)

    # Tile layer control
    # https://deparkes.co.uk/2016/06/10/folium-map-tiles/
    folium.TileLayer('Stamen Toner').add_to(myMapSessions)
    folium.TileLayer('Cartodb Positron').add_to(myMapSessions)
    folium.TileLayer('Cartodb dark_matter').add_to(myMapSessions)
    folium.LayerControl().add_to(myMapSessions)

    return myMapSessions

def saveMap(foliumMap,saveName):
    foliumMap.save(saveName)
