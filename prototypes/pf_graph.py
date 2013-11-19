#   - GraphEdge (nodes, gate, raw_path, optimised_path (+length), optimised_gate_path (+length)

import collections

import pf_vector

class Graph:
	"""
		Represents a graph.
	"""
	def __init__(self, influence_map):
		# self influence map
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
		# does the edge already exist, if yes skip the process?
		for edge in node_a.edges:
			if edge.path == path:
				return
		# create the edge
		edge = GraphEdge( node_a, node_b, path )
		# add it the list of edges
		self.edges.append(edge)
		# announce the existence of the edge
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
						if not (grid_edge.b == start_node.position and path.length() > 2):
							continue
					
					# extend the path
					new_path = path.append( grid_edge.b )

					if grid_edge.b in self._node_positions:
						# if the other point is a node, add it to the edges list
						self._add_edge( new_path )
					else:
						# otherwise mark it for future traversal
						paths_to_explore.append( new_path )


class GraphNode:
	"""
		Represents node in the graph.
	"""
	def __init__(self, position):
		self.position = position
		self.edges = []
	
	def _add_edge(self, edge):
		""" add edge to node """
		self.edges.append(edge)
	
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
		self.node_a = node_a
		self.node_b = node_b
		self.path   = path
	
	def nodes(self):
		""" return the nodes which are associated to the edge """
		return {self.node_a,self.node_b}
	
	def __eq__(self, other):
		return self.nodes() == other.nodes()

	def __str__(self):
		""" Generate a string representation of the current object. """
		return "GraphEdge(%s,%s,%s)" % (self.node_a,self.node_b,self.path)

	def __repr__(self):
		""" Generate a string representation of the current object. """
		return "GraphEdge(%r,%r,%r)" % (self.node_a,self.node_b,self.path)
