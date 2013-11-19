import collections

import pf_vector
import pf_map


class AreaMap(pf_map.Map):
	"""
		Creates a map where every tile is assigned to either its area_id
		or self.no_area_id if no area could be found. Furthermore,
		representatives is dictionary of lists which contain representatives
		of each area, i.e a random point in the area and edges is a dictionary
		of lists too, containing the edges which constitute the border of the area
	"""
	no_area_id = -1
	
	def __init__(self, raw_map, pass_test):
		self.raw_map = raw_map
		self.pass_test = pass_test
	
		# initialise area with self.no_area_id
		area_data = [self.no_area_id for _ in self.raw_map.data]
		super(AreaMap,self).__init__(self.raw_map.width, self.raw_map.height, area_data)
		# list of representatives of the areas, i.e. a random point of every area
		self.representatives = collections.defaultdict(set)
		# edges of areas, to the left is the inner area
		self.edges = collections.defaultdict(list)
		
		# create area map
		self._create_area_map()
	
	def _create_area_map(self):
		""" create it """
		# create shortcuts
		width,height = self.raw_map.width,self.raw_map.height
		
		# initialise id first free id
		area_id = self.no_area_id + 1
		
		#
		# fill map boundary
		#
		for x in range(width):
			# y = 0 line
			t = pf_vector.GridTile(x,0)
			self._treat_tile(area_id, t)
			
			if self.pass_test( self.raw_map[t] ):
				p     = pf_vector.GridPoint(x,  0)
				p_xpp = pf_vector.GridPoint(x+1,0)
				# inner side is to the right
				self.edges[area_id].append( pf_vector.GridEdge(p, p_xpp) )
			
			# y = max line
			t = pf_vector.GridTile(x,height-1)
			self._treat_tile(area_id, t)
			
			if self.pass_test( self.raw_map[t] ):
				p     = pf_vector.GridPoint(x,  height)
				p_xpp = pf_vector.GridPoint(x+1,height)
				# inner side is to the right
				self.edges[area_id].append( pf_vector.GridEdge(p_xpp, p) )

		for y in range(height):
			# x = 0 line
			t = pf_vector.GridTile(0,y)
			self._treat_tile(area_id, t)
			
			if self.pass_test( self.raw_map[t] ):
				p     = pf_vector.GridPoint(0, y, )
				p_ypp = pf_vector.GridPoint(0, y+1)
				# inner side is to the left
				self.edges[area_id].append( pf_vector.GridEdge(p_ypp, p) )
			
			# x = max line
			t = pf_vector.GridTile(width-1,y)
			self._treat_tile(area_id, t)
			
			if self.pass_test( self.raw_map[t] ):
				p     = pf_vector.GridPoint(width, y, )
				p_ypp = pf_vector.GridPoint(width, y+1)
				# inner side is to the left
				self.edges[area_id].append( pf_vector.GridEdge(p, p_ypp) )

		# increment area_id
		area_id += 1
		
		# iterate over all data
		for t in self.raw_map.tiles_iterator():
			if self._treat_tile(area_id, t):
				# if we found something, increment area_id
				area_id += 1
		
	def _treat_tile(self, area_id, t):
		# if the tile is unpassable and we did not know that before, treat it,
		# otherwise skip it
		if self.pass_test( self.raw_map[t] ) or self[t] != self.no_area_id:
			return False

		# add the current point as the representative of the area
		self.representatives[area_id].add(t)

		# initialise the list of propagation points with the given one
		propagation_tiles = [ t ]
		# mark it
		self[t] = area_id
		# treated points: 1
		treated_tiles = 1
		
		while propagation_tiles:
			# get last tile
			t = propagation_tiles.pop()
			
			# all nearby tiles (including the diagonal)
			for tpp in t.adjacent_tiles():
				# ignore points outside of the box
				if not self.contains(tpp):
					continue
				
				# skip the point if was or will be treated with
				if self[tpp] != self.no_area_id:
					continue
				
				# if the point is passable, skip it, but before that check
				# if this defines an edge
				if self.pass_test( self.raw_map[tpp] ):
					# it defines an edge if this is not a diagonal move,
					# i.e. the distance is one
					if (tpp - t).length_squared() == 1:
						# want the edge between t and tpp,
						# t should be right of the edge (clock-wise)
						edge = t.edge_between(tpp)
						# add edge
						self.edges[area_id].append( edge )
					continue

				# if it is unpassable, mark it
				self[tpp] = area_id
				# treated (or supposed to be treated)
				treated_tiles += 1
				# add it
				propagation_tiles.append( tpp )
		
		# print it
		print("flood filled area number %d: it has %d points" % (area_id,treated_tiles))

		# we found something
		return True