import pf_area_map
import pf_influence_map
import pf_graph
import pf_shortest_path


class PathFindingData:
	"""
		Holds all the preprocessed data.
	"""
	def __init__(self, raw_map, pass_test, precomputed_hops=1):
		""" pass_test is a function which tests if a tile is unpassable """
		self.raw_map = raw_map
		self.pass_test = pass_test
		self.precomputed_hops = precomputed_hops
		
		self._preprocess_map()
		
	def _preprocess_map(self):
		# create the area map
		self.area_map = pf_area_map.AreaMap(self.raw_map, self.pass_test)
		# create the influence map
		self.influence_map = pf_influence_map.InfluenceMap(self.area_map)
		# create the graph
		self.graph = pf_graph.Graph(self.area_map, self.influence_map)
		# create shortest path search
		self.shortest_path = pf_shortest_path.ShortestPathSearch(self.graph, self.area_map, self.precomputed_hops)
	


