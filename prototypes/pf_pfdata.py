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
		
		# TODO: optimisations:
		# - do not go to connectivity nodes (i.e. nodes which have exactly
		#   one edge to a non-connectivity node. (this definition is unstable,
		#   (as order depenendant) but in this context OK
		
		n = 3 # number of edges
		self._n_hop_dict = NHopDictionary(self.graph, self.area_map, n)
		
		def get_edges(node):
			return node.directional_edges()
		def exact_eval(path):
			path = sum([edge.opt_path().points for edge in path._edges],[])
			path = pf_vector.PathF(path)
			opt = self.area_map.optimise_path(path)
			return opt.length()
		def range_eval(path):
			c = len(path._edges)
			
			# corresponds to nodes
			if len(path._edges) > 1:
				c_min = path._extended_path.c_min
				c_max = path._extended_path.c_max
			else:
				c_min,c_max = [],[]

			# c_min, c_max have length min(n, c-1)
	
			c_min_cur = 0
			c_max_cur = float("inf")
			
			# consider the estimated lengths taken into account the old ones
			for i in range(1,min(n,len(c_min)+1)+1):
				# find the min/max lengths from node edge[-i] to edge[-1].end
				# for 1 <= i <= n and <= c_min+1
				edges = [path._edges[k] for k in range(-i,0)] #  -i <= k <= -1
				assert(len(edges) == i)
				sub_min,sub_max = self._n_hop_dict.length_estimation(edges)
				if i - 1 < len(c_min):
					c_min_cur = max( c_min_cur, c_min[i-1] + sub_min )
					c_max_cur = min( c_max_cur, c_max[i-1] + sub_max )
				else:
					c_min_cur = max( c_min_cur, sub_min )
					c_max_cur = min( c_max_cur, sub_max )

			path.c_min = [c_min_cur] + (c_min[:-1] if len(c_min) == n else c_min)
			path.c_max = [c_max_cur] + (c_max[:-1] if len(c_max) == n else c_max)
			return (c_min_cur,c_max_cur)
		
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


class NHopDictionary:
	"""
		find all optimal distances/ optimal gate distances
		of nodes which are max n hops apart
	"""
	def __init__(self, graph, area_map, n):
		self.graph = graph
		self.area_map = area_map
		self.n = n
		# saves the min/max length of the path
		self._map_length = {}
		# saves the opt_path for the path
		self._map_opt_path = {}
		
		# build it
		self._build()
	
	def create_key(self, edges):
		"""
			create and canonicalise key,
			the key is the tuple of the edge ids
			and the lower end starts direction """
		for edge in edges:
			assert(isinstance(edge,pf_graph.DirectionalGraphEdge))
		key = tuple(edge._graph_edge.edge_id(self.graph) for edge in edges)
		return key if key[0] <= key[-1] else tuple(reversed(key))

	def _build_helper(self, edges):
		""" helper method: expand nodes """
		
		# if the nodes list is already too long, ignore it
		if len(edges) > self.n:
			return
		
		# get the old optimal path
		if len(edges) != 1:
			old_opt_path = self.optimal_path( edges[:-1] )
		else:
			old_opt_path = pf_vector.PathF([])
		
		# create the key under which we can find the data
		key = self.create_key(edges)
		
		# if this key was already visited, do not skip it, just don't compute anything
		if key not in self._map_opt_path:
			# create an extended path along the new node
			not_opt_path = old_opt_path.points + edges[-1].opt_path().points
			not_opt_path = pf_vector.PathF(not_opt_path)
			# find optimal path
			opt_path = self.area_map.optimise_path(not_opt_path)
			# find optimal gate path
			opt_gate_path = self.graph._opt_gate_path(
											edges[0].start().position,
												edges[0].start_gates(),
											edges[-1].end().position,
												edges[-1].end_gates(),
											opt_path)
			
			# save the optimal path and min/max
			self._map_opt_path[key] = opt_path
			self._map_length[key] = (opt_gate_path.length(),opt_path.length())
		
		# iterate over all edges
		for edge in edges[-1].end().directional_edges():
			# do not allow loops
			if edge.end() == edges[0].start() or edge.end() in [e.end() for e in edges]:
				continue
			
			# now we have an edge with which we can extend our list
			new_edges = edges + [edge]
			
			# add it
			self._build_helper( new_edges )

	def _build(self):
		for node in self.graph.nodes:
			for edge in node.directional_edges():
				self._build_helper([edge])
		print("added %d keys" % len(self._map_opt_path))
		
	def optimal_path(self, edges):
		""" find the optimal path """
		key = self.create_key(edges)
		opt_path = self._map_opt_path[key]
		
		start = edges[0].start().position.toPointF()
		
		# make sure that we return the path in the correct direction
		if start == opt_path.points[0]:
			return opt_path
		elif start == opt_path.points[-1]:
			return opt_path.reversed()
		else:
			raise RuntimeError("Floating point or programming issue: %s = %s,%s"\
				                  % (start,opt_path.points[0],opt_path.points[-1])
								)

	def length_estimation(self, edges):
		""" get a length estimation """
		key = self.create_key(edges)
		return self._map_length[key]