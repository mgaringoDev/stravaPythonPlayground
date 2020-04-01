import folium
import numpy as np
from folium.plugins import HeatMap
import polyline

def getHeatMap(sessions,heatmap_radius = 5,heatmap_blur = 5):

	print('Now draw heatmap for {} sessions'.format(len(sessions)))
	allSessionCoords = []

	for session in sessions:
		sessionCoords = polyline.decode(session['map']['summary_polyline'])
		for s in sessionCoords:
			allSessionCoords.append(s)

	# Drawing Parameters for Heatmap	
	heatmap_grad = \
	    {0.0: '#000004',
	     0.1: '#160b39',
	     0.2: '#420a68',
	     0.3: '#6a176e',
	     0.4: '#932667',
	     0.5: '#bc3754',
	     0.6: '#dd513a',
	     0.7: '#f37819',
	     0.8: '#fca50a',
	     0.9: '#f6d746',
	     1.0: '#fcffa4'}

	# get center of the map
	allLat = []
	allLon = []
	for sesCo in allSessionCoords:    
	    allLat.append(sesCo[0])
	    allLon.append(sesCo[1])

	centre = [(min(allLat) + max(allLat))/2,(min(allLon) + max(allLon))/2]

	# Draw the map

	fmap = folium.Map(tiles = 'CartoDB dark_matter', 
                  prefer_canvas = True, 
                  location = centre,
                  zoom_start = 12)
	
	HeatMap(allSessionCoords, 
	        radius = heatmap_radius, 
	        blur = heatmap_blur, 
	        gradient = heatmap_grad, 
	        name = 'Heat Map').add_to(fmap)

	# Tile layer control
	# https://deparkes.co.uk/2016/06/10/folium-map-tiles/
	folium.TileLayer('Stamen Toner').add_to(fmap)
	folium.TileLayer('Cartodb Positron').add_to(fmap)
	folium.TileLayer('Cartodb dark_matter').add_to(fmap)
	folium.LayerControl().add_to(fmap)
	
	return fmap

def saveMap(foliumMap,saveName):
	foliumMap.save(saveName)
