import numpy as np 
import pandas as pd # Not sure if we have to do if with pandas or if numpy will be sufficient 

# from bokeh.charts import HeatMap, bins, output_file, show
# from bokeh.palettes import RdYlGn6

# Extend this in the future to work with Bokeh servers in order to stream data 

""" 
class Bokeh_Visualization: 
	def __init__(self, tile_number, tile_height, tile_width, journal_list): 
		if tile_height * tile_width > len(journal_list): 
			raise ValueError("Too much data to work with")

		self.tile_number = tile_number 
		self.tile_height = tile_height 
		self.tile_width = tile_width
		self.journal_list = journal_list

	def visualize_data(self): 
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
"""