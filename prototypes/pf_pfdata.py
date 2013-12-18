import pf_vector
import pf_area_map
import pf_influence_map
import pf_graph
import pf_graph_shortest_path

class PathFindingData:
	"""
		Holds all the preprocessed data.
	"""
	def __init__(self, raw_map, pass_test):
		""" pass_test is a function which tests if a tile is unpassable """
		self.raw_map = raw_map
		self.pass_test = pass_test
		
		self._preprocess_map()
		self._create_shortest_path_finder()
		
	def _preprocess_map(self):
		# create the area map
		self.area_map = pf_area_map.AreaMap(self.raw_map, self.pass_test)
		# create the influence map
		self.influence_map = pf_influence_map.InfluenceMap(self.area_map)
		# create the graph
		self.graph = pf_graph.Graph(self.area_map, self.influence_map)
	
	def _create_shortest_path_finder(self):
		""" create shortest path finder """
		def get_edges(node):
			return node.directional_edges()
		def exact_eval(path):
			path = sum([edge.opt_path().points for edge in path._edges],[])
			path = pf_vector.PathF(path)
			opt = self.area_map.optimise_path(path)
			return opt.length()
		def range_eval(path):
			c_min = sum(edge._graph_edge._opt_gate_path_length for edge in path._edges)
			c_max = sum(edge._graph_edge._opt_path_length for edge in path._edges)
			return (c_min,c_max)
		
		self.finder = pf_graph_shortest_path.ShortestPathFinder(
		                          self.graph.nodes,
		                          get_edges,
		                          exact_eval,
		                          range_eval)

	def find_path_between_nodes(self, start, end):
		""" find the best path between the two points """
		assert(isinstance(start,pf_graph.GraphNode))
		assert(isinstance(end,pf_graph.GraphNode))
		
		# find the shortest path
		path = self.finder.find_path(start,end)
		
		# convert it to PathF and maximise (not very optimised version)
		opt_path = sum([edge.opt_path().points for edge in path._edges],[])
		opt_path = pf_vector.PathF(opt_path)
		opt_path = self.area_map.optimise_path(opt_path)
		
		# and return it
		return opt_path

	def find_path(self, start, end):
		""" find the best path between the two points """
		assert(isinstance(start,pf_vector.PointF))
		assert(isinstance(end,pf_vector.PointF))
		
		raise NotImplementedError
