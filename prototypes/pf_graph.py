import collections

import pf_vector

class Graph:
	"""
		Represents a graph.
	"""
	def __init__(self, area_map, influence_map):
		# set area and influence map
		self.area_map = area_map
		self.influence_map = influence_map

		# initialise attributes
		self.nodes = []
		self.edges = []
		
		# keep track of the positions of all nodes
		self._node_positions = {}

		# create the graph
		self._create_graph()
	
	def _add_node(self, position):
		""" add a node to the graph """
		# create the node
		node = GraphNode( position )
		# add it the list of nodes
		self.nodes.append(node)
		# add it to dictionary position -> node
		self._node_positions[position] = node
	
	def _add_edge(self, path):
		""" add the edge to the graph """
		# get the associated nodes
		node_a = self._node_positions[path.start()]
		node_b = self._node_positions[path.end()]
		# does the edge already exist? if yes skip the process
		for edge in node_a.edges:
			if edge._path == path:
				return
		# create the edge
		edge = GraphEdge( node_a, node_b, path )
		# add it the list of edges
		self.edges.append(edge)
		# announce the existence of the edge (only add once per node)
		node_a._add_edge(edge)
		if node_a != node_b:
			node_b._add_edge(edge)
	
	def _create_graph(self):
		""" create the graph """
		
		print("creating area graph...")
		
		# create the nodes
		self._create_graph_nodes()
		
		# create the edges
		self._create_graph_edges()
		
		# find the gates
		self._find_gates()
		
		# optimise the edges
		self._optimise_graph_edges()
		
		print("done, found %d nodes and %d edges" % (len(self.nodes),len(self.edges),))

	def _create_graph_nodes(self):
		""" create the nodes in the graph """
		
		# point -> set of (grid) edges which originate at the point
		point_to_grid_edges = collections.defaultdict(set)
		for loops in self.influence_map.boundaries.values():
			for loop in loops:
				for edge in loop:
					point_to_grid_edges[edge.a].add(edge)
		
		# find the nodes of the graph, i.e. points with unequal two
		# connected points
		for point, grid_edges in point_to_grid_edges.items():
			if len(grid_edges) != 2: 
				self._add_node( point )
		
		# find loops without node
		for loops in self.influence_map.boundaries.values():
			for loop in loops:
				# if we have a loop without a node, add one
				for edge in loop:
					if edge.a in self._node_positions:
						break
				else:
					# has no node, so add one.
					self._add_node( loop[0].a )

	def _create_graph_edges(self):
		""" create the graph edges """
		
		# point -> set of (grid) edges which originate at the point
		point_to_grid_edges = collections.defaultdict(set)
		for loops in self.influence_map.boundaries.values():
			for loop in loops:
				for edge in loop:
					point_to_grid_edges[edge.a].add(edge)
			
		# for every node find all paths to other nodes
		for start_node in self.nodes:
			# apply a search of all paths which originate at the current position.
			# to do that, extend the path with all possibilites until we find
			# another node
			paths_to_explore = [ pf_vector.GridPath( [start_node.position] ) ]
			
			# extend the path
			while paths_to_explore:
				# next path to extend
				path = paths_to_explore.pop(0)
				
				# find grid edges from the last point of the path
				for grid_edge in point_to_grid_edges[path.end()]:
					# if adding the point would lead to a self intersection, skip it
					if path.has_point(grid_edge.b):
						# except if the adding the point would give a non-trivial loop
						if not (grid_edge.b == start_node.position and path.node_count() > 2):
							continue
					
					# extend the path
					new_path = path.get_path_extended_by( grid_edge.b )

					if grid_edge.b in self._node_positions:
						# if the other point is a node, add it to the edges list
						self._add_edge( new_path )
					else:
						# otherwise mark it for future traversal
						paths_to_explore.append( new_path )

	def _optimise_graph_edges(self):
		"""
			optimise every path between nodes and hence initialises
			GraphEdge.opt_path and GraphEdge.opt_path_length
		"""
		for edge in self.edges:
			path = edge._path.toPathF()
			opt_path = self.area_map.optimise_path(path)
			edge.set_optimal_path(opt_path)

	def _find_gates(self):
		""" find all gates """
		for node in self.nodes:
			d_edges = node.sorted_directional_edges()
			for i in range(len(d_edges)):
				edge_a,edge_b = d_edges[i],d_edges[(i+1)%len(d_edges)]
				path_a,path_b = edge_a.path(),edge_b.path()
				point = self.influence_map.nearest_area_grid_point_in_sector(node.position, path_a, path_b)
				node.gates.append(point)


class GraphNode:
	"""
		Represents node in the graph.
	"""
	def __init__(self, position):
		self.position = position
		self.edges = []

		# slots for results of deferred calculations
		self.gates = []               # init by Graph._find_gates
	
	def _add_edge(self, edge):
		""" add edge to node """
		self.edges.append(edge)

	def directional_edges(self):
		""" get all the directional edges """

		# list all directional edges
		directional_edges = []
		for edge in self.edges:
			# if node a is self, add a -> b
			if edge.node_a == self:
				directional_edges.append(DirectionalGraphEdge(edge,True))
			# if node b is self, add b -> a
			# especially, if node a == b, we have added both directions
			if edge.node_b == self:
				directional_edges.append(DirectionalGraphEdge(edge,False))
		
		return directional_edges
	
	def sorted_directional_edges(self):
		""" get the directional edges in a sorted manner """
		directional_edges = self.directional_edges()
		directional_edges.sort(key=lambda e: e._sort_key())
		return directional_edges
	
	def __eq__(self, other):
		return self.position == other.position

	def __hash__(self):
		return hash(self.position)

	def __str__(self):
		""" Generate a string representation of the current object. """
		return "GraphNode(%s)" % (self.position)

	def __repr__(self):
		""" Generate a string representation of the current object. """
		return "GraphNode(%r)" % (self.position)


class GraphEdge:
	"""
		Represents an edge in the graph.
	"""
	def __init__(self, node_a, node_b, path):
		# save the path
		self._node_a = node_a
		self._node_b = node_b
		self._path  = path
		
		# slots for results of deferred calculations
		self._opt_path = None              # init by Graph._optimise_graph_edges
		self._opt_path_length = None       # init by Graph._optimise_graph_edges
		
		self._opt_gate_path = None         # TODO
		self._opt_gate_path_length = None  # TODO
	
	@property
	def node_a(self):
		return self._node_a
		
	@property
	def node_b(self):
		return self._node_b
	
	def nodes(self):
		""" return the nodes which are associated to the edge """
		return {self.node_a,self.node_b}
	
	def set_optimal_path(self, opt_path):
		""" set the optimal path between node a and node b"""
		self._opt_gate_path = opt_path
		self._opt_path_length = self._opt_gate_path.length()

	def __eq__(self, other):
		raise NotImplementedError()

	def __str__(self):
		""" Generate a string representation of the current object. """
		return "GraphEdge(%s,%s,%s)" % (self.node_a,self.node_b,self._path)

	def __repr__(self):
		""" Generate a string representation of the current object. """
		return "GraphEdge(%r,%r,%r)" % (self.node_a,self.node_b,self._path)

class DirectionalGraphEdge:
	"""
		Represents an edge in the graph with a direction
	"""
	def __init__(self, graph_edge, a_to_b):
		# save
		self._graph_edge = graph_edge
		self._a_to_b = a_to_b
	
	def path(self):
		""" get the path """
		if self._a_to_b:
			# return the original one
			return self._graph_edge._path
		else:
			# return the reversed one
			return self._graph_edge._path.reversed()
	
	def start(self):
		""" get the start point """
		return self._graph_edge.a if self._a_to_b else self._graph_edge.b

	def end(self):
		""" get the end point """
		return self._graph_edge.b if self._a_to_b else self._graph_edge.a

	def _sort_key(self):
		"""
			sort the edges such that they are clock-wise ordered, i.e.
			place  diff
			1th    (1,0)
			2th    (0,-1)
			3th    (-1,0)
			4th    (0,1)
		"""
		path = self.path()
		v = path.points[1] - path.points[0]
		if v.x == 1:    return 1
		elif v.y == -1: return 2
		elif v.x == -1: return 3
		elif v.y == 1:  return 4
		else: raise RuntimeError
