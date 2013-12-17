import pf_area_map
import pf_influence_map
import pf_graph

class PathFindingData:
	"""
		Holds all the preprocessed data.
	"""
	def __init__(self, raw_map, pass_test):
		""" pass_test is a function which tests if a tile is unpassable """
		self.raw_map = raw_map
		self.pass_test = pass_test
		
		self._preprocess_map()
	
	def _preprocess_map(self):
		# create the area map
		self.area_map = pf_area_map.AreaMap(self.raw_map, self.pass_test)
		# create the influence map
		self.influence_map = pf_influence_map.InfluenceMap(self.area_map)
		# create the graph
		self.graph = pf_graph.Graph(self.area_map, self.influence_map)
