import plotly.plotly as py 
import plotly.offline as py_offline 
import plotly.graph_objs as go 
import numpy as np 
from pprint import pprint 

# Extend in the future to accept a stream of data 
# Also, consider playing around in Dash

class Plotly_Visualization: 
	""" API for visualizing tiles 

	Adapted from code submitted in the spring semester
	Uses heatmapgl instead of the normal heatmap class in an effort to improve performance 

	Better documentation coming later
	""" 
	def __init__(self, tile_number, tile_height, tile_width, journal_list): 
		"""
		Parameters:
			tile_number : Tile number in the overall image
			tile_height, tile_width : Tile size
			data_list: List of tuples of the form (page_id, count)
		"""
		if tile_height * tile_width > len(journal_list): 
			raise ValueError("Too much data to work with")

		self.tile_number = tile_number 
		self.tile_height = tile_height 
		self.tile_width = tile_width
		self.journal_list = journal_list

	def visualize_data(self): 
		""" Creates a tile_height * tile_width heatmap of the journal data """ 
		x = np.arange(self.tile_width)
		y = np.arange(self.tile_height)
		hovertext = []

		journal_ids = np.empty(len(self.journal_list), dtype = "object")
		page_counts = np.zeros(len(self.journal_list))

		for index, journal in enumerate(self.journal_list): 
			journal_ids[index] = journal.title
			page_counts[index] = journal.num_pages

		journal_ids = journal_ids.reshape((self.tile_width, self.tile_height))
		page_counts = page_counts.reshape((self.tile_width, self.tile_height))

		for yi, yy in enumerate(y):
			hovertext.append(list())
			for xi, xx in enumerate(x):
				hovertext[-1].append("Journal name : {}<br />Count: {}".format(np.flipud(journal_ids)[self.tile_height -1 -yi][xi], np.flipud(page_counts)[self.tile_height - 1 - yi][xi]))

		trace = go.Heatmapgl(z = page_counts, x = x, y = y, hoverinfo = "text", text = hovertext, colorscale = "Viridis")
		data = [trace]
		py_offline.plot(data, filename = "../Tiles/tile" + str(self.tile_number) + ".html", auto_open = False)
		print("Done")