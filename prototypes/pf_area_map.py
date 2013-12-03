import collections

import pf_vector
import pf_map_base
import pf_halfplane

class AreaMap(pf_map_base.MapBase):
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
			self.__treat_tile(area_id, t)
			
			if self.pass_test( self.raw_map[t] ):
				p     = pf_vector.GridPoint(x,  0)
				p_xpp = pf_vector.GridPoint(x+1,0)
				# inner side is to the right
				self.edges[area_id].append( pf_vector.GridEdge(p, p_xpp) )
			
			# y = max line
			t = pf_vector.GridTile(x,height-1)
			self.__treat_tile(area_id, t)
			
			if self.pass_test( self.raw_map[t] ):
				p     = pf_vector.GridPoint(x,  height)
				p_xpp = pf_vector.GridPoint(x+1,height)
				# inner side is to the right
				self.edges[area_id].append( pf_vector.GridEdge(p_xpp, p) )

		for y in range(height):
			# x = 0 line
			t = pf_vector.GridTile(0,y)
			self.__treat_tile(area_id, t)
			
			if self.pass_test( self.raw_map[t] ):
				p     = pf_vector.GridPoint(0, y, )
				p_ypp = pf_vector.GridPoint(0, y+1)
				# inner side is to the left
				self.edges[area_id].append( pf_vector.GridEdge(p_ypp, p) )
			
			# x = max line
			t = pf_vector.GridTile(width-1,y)
			self.__treat_tile(area_id, t)
			
			if self.pass_test( self.raw_map[t] ):
				p     = pf_vector.GridPoint(width, y, )
				p_ypp = pf_vector.GridPoint(width, y+1)
				# inner side is to the left
				self.edges[area_id].append( pf_vector.GridEdge(p, p_ypp) )

		# increment area_id
		area_id += 1
		
		# iterate over all data
		for t in self.raw_map.tiles_iterator():
			if self.__treat_tile(area_id, t):
				# if we found something, increment area_id
				area_id += 1
		
	def __treat_tile(self, area_id, t):
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

	def get_point_area_id(self, point):
		""" get the area_id which belongs to a point """

		# this is the area_id of an adjacent tile
		for tile in point.adjacent_tiles():
			# if it is a usual tile, treat it like that
			if self.contains(tile):
				if self[tile] != self.no_area_id:
					return self[tile]
			else:
				# if a wall was found, use the wall id
				return self.no_area_id + 1
		else:
			# nothing was found
			return self.no_area_id

	def find_obstruction_when_transforming_line(self, base, start, end):
		"""
			is there any obstruction to transforming base->start to base->end?
			
			or, to put it differently, find the biggest t such that the triangle
				base->start->start+t*(end-start)
			intersects no unpassable tiles. Assuming that no obstruction
			lies on the lines base->start and start->end.
			
			tests:
				raw_map = pf_map.Map(10,10,100*[0])
				area_map = pf_area_map.AreaMap(raw_map, lambda _: True)
				
				area_map[pf_vector.GridTile(4,4)] = 0 # 4,4 is now unpassable
				
				base = pf_vector.PointF(2,2)
				start = pf_vector.PointF(8,2)
				end = pf_vector.PointF(8,2)
				
				area_map.find_obstruction_when_transforming_line(base, start, end)
				Out: (1.0, None)
				
				area_map.find_obstruction_when_transforming_line(base, start, end)
				Out: (0.4, GridTile(5, 4))
				
				area_map[pf_vector.GridTile(6,3)] = 0 # 6,3 is now unpassable
				area_map.find_obstruction_when_transforming_line(base, start, end)
				Out: (0.16666666666666666, GridPoint(7, 3))
				
				area_map[pf_vector.GridTile(4,2)] = 0 # 4,2 is now unpassable
				area_map.find_obstruction_when_transforming_line(base, start, end)
				Out: (0.0, GridPoint(5, 2))

				area_map[pf_vector.GridTile(2,2)] = 0 # 2,2 is now unpassable
				area_map.find_obstruction_when_transforming_line(base, start, end)
				Out: (0.0, GridPoint(5, 2))
		"""

		assert(isinstance(base,pf_vector.PointF))
		assert(isinstance(start,pf_vector.PointF))
		assert(isinstance(end,pf_vector.PointF))


		# find inner direction
		v_start = start - base
		v_end   =   end - base
		v_start_left = v_start.left()

		# if leftness > 0, the inner direction is to the left of v_start,
		# otherwise to the right
		leftness = v_start_left * v_end
		leftness_sign = +1 if leftness >= 0 else -1
		
		
		
		# the obstructing point
		obstructing_point = None
		# the vector base->obstructing_point
		v_obstructing_point = None
		# the vector v_obstructing_point.right()
		v_obstructing_point_right = None

		# iterate over all tiles
		for tile in self.find_tiles_in_triangle_iterator(base, start, end):
			# skip the tile if it is not obstructing
			if self[tile] == self.no_area_id:
				continue
		
			# iterate over all points which are adjacent to the tile
			for point in tile.adjacent_points():
				# compute v_point
				v_point = point.toPointF() - base
				
				if not obstructing_point:
					# if do not yet have an obstructing point, this one is one
					obstructing_point = point
					v_obstructing_point = v_point
					v_obstructing_point_right = v_obstructing_point.right()
					continue

				# assume leftness_sign = +1.
				# we are looking for the point which has the smallest angle
				# with base->start. as obstructing_point is to the left of
				# base->start (as leftness_sign = +1), if we find a point
				# which is to the right of v_obstructing_point, then this is
				# a new candidate. if they are on the same line, the one
				# which is further away from base wins.
				
				# assuming leftness_sign = +1.
				# if v_point is between v_obstructing_point and v_start,
				# then it is right of v_obstructing_point, i.e. the scalar
				# product below is positive
				scalar_product = v_obstructing_point_right * v_point

				if leftness_sign*scalar_product > 0\
				   or\
				   (scalar_product == 0\
					and\
					v_point.length_squared() > v_obstructing_point.length_squared()):
					# we have a new candidate
					obstructing_point = point
					v_obstructing_point = v_point
					v_obstructing_point_right = v_obstructing_point.right()

		# if there is no obstruction point
		if not obstructing_point:
			return 1., None
		else:
			# otherwise, compute t value
			
			# t value now is the intersection of the start->end line with the
			# halfplane which is defined by base->point
			v_obstruction_normal = (obstructing_point.toPointF() - base).left()
			halfplane = pf_halfplane.HalfPlane(base, v_obstruction_normal)
			t = halfplane.find_t(start, end)

			return t, obstructing_point

	def optimise_path(self, path, max_iterations=20):
		"""
			find the shortest way between path.start() and path.end()
			taking path as the starting point
		"""
		print("optimising path of length %s (nodes: %d)..." % (path.length(),path.node_count()))

		# original path
		original_path = path

		for iteration in range(max_iterations):
			path_changed = False
			
			# start new path with the starting point of the path, truncate old_path
			path,old_path = pf_vector.PathF(path.points[0:1]),pf_vector.PathF(path.points[1:])
			
			while not old_path.empty():
				# take the last point of the new path
				base = path.end()
				
				while old_path.node_count() >= 2:
					p0 = old_path.pop_first()
					p1 = old_path.start()
					t,obs = self.find_obstruction_when_transforming_line(base,p0,p1)
					obs = obs.toPointF() if obs is not None else None
					
					if obs is None:
						# p0 is superflous, ignore it
						path_changed = True
						continue
					elif obs == p0:
						# p0 is necessary
						path.append( p0 )
						break
					elif obs is not None:
						# replace
						#   base|->...->p0->p1
						# by
						#   base->obs|->pt->p1
						# with pt = p0+t*(p1-p0)
						path.append( obs )
						pt = p0 + (p1-p0).scaled(t)
						pt = pf_vector.PointF(pt.x,pt.y)
						if obs != pt:
							old_path.prepend(pt)
						path_changed = True
						break
				else:
					# there is only one element left, the end point which we may not change
					path.append(old_path.pop_first())

			print("new path: length: %s, nodes: %d" % (path.length(),path.node_count()))
			
			# do it until the path does not change anymore
			if not path_changed:
				break
		else:
			raise RuntimeError("Needed way too many iterations.")
		
		print("done")
		
		return path
