import pf_vector
import pf_halfplane

class MapBase:
	def __init__(self, width, height, data):
		self.width = width
		self.height = height
		self.data = data

	def contains(self, obj):
		""" does the current map contain the point/tile? """
		if isinstance(obj, pf_vector.PointTemplate):
			return 0 <= obj.x <= self.width and 0 <= obj.y <= self.height
		elif isinstance(obj, pf_vector.GridTile):
			return 0 <= obj.x < self.width and 0 <= obj.y < self.height
		else:
			raise TypeError()

	def tiles_iterator(self):
		""" returns an iterator over all tiles """
		for x in range(self.width):
			for y in range(self.height):
				yield pf_vector.GridTile(x,y)

	def __getitem__(self, i):
		assert( isinstance(i, pf_vector.GridTile) )
		index = i.x + i.y*self.width
		return self.data[index]

	def __setitem__(self, i, v):
		assert( isinstance(i, pf_vector.GridTile) )
		index = i.x + i.y*self.width
		self.data[index] = v
	
	def find_tiles_in_triangle_iterator(self, base, start, end):
		""" find all tiles in the triangle defined by the three points """

		assert(isinstance(base,pf_vector.PointF))
		assert(isinstance(start,pf_vector.PointF))
		assert(isinstance(end,pf_vector.PointF))

		#
		# find orientation
		#
		# compute vectors originating from base
		v_start = start - base
		v_end   = end   - base
		v_far_edge = end - start
		
		# compute vector originating from base which goes to the left of v_start
		v_start_left = v_start.left()
		v_end_left   = v_end.left()
		v_far_edge_left = v_far_edge.left()
		
		# find inner direction
		leftness = v_start_left * v_end
		
		if leftness > 0:
			# inner direction is to the left of v_start, i.e. to the right of v_end
			v_start_normal    = v_start_left
			v_end_normal      = -v_end_left
			v_far_edge_normal = v_far_edge_left
		elif leftness < 0:
			# inner direction is to the right of v_start
			v_start_normal    = -v_start_left
			v_end_normal      = v_end_left
			v_far_edge_normal = -v_far_edge_left
		else: # leftness == 0
			# they are parallel: everything is fine because we assume that
			# the original lines are fine
			return []
		
		# the triangle is the intersection of the three half planes
		triangle = [
						pf_halfplane.HalfPlane(base,v_start_normal),
						pf_halfplane.HalfPlane(base,v_end_normal),
						pf_halfplane.HalfPlane(start,v_far_edge_normal),
					]
						
		def tile_intersects_triangle(tile):
			# tile polygon
			polygon = tile.polygon()
			# intersections
			for halfplane in triangle:
				polygon = halfplane.intersection(polygon)
				# we want a proper intersection, not just a line
				if polygon.node_count() <= 2:
					return False
			# if end up here, then the polygon has a non-trivial
			# intersection with the triangle
			return True
		
		# find all tiles intersecting the triangle
		open_tiles = []
		all_tiles = []
		
		# find first tile which intersects the interior of the area
		p = pf_vector.GridPoint( int(base.x),int(base.y) )
		
		for tile in p.adjacent_tiles():
			if tile_intersects_triangle(tile):
				# we found our first tile
				open_tiles.append(tile)
				all_tiles.append(tile)
				break
		else:
			raise ValueError()
		
		# find all tiles in the triangle
		while open_tiles:
			# propagate open tiles
			tile = open_tiles.pop(0)
			# propagate to all nearby points (including the diagonal)
			for next_tile in tile.adjacent_tiles():
				# ignore points outside of the box
				if not self.contains(next_tile):
					continue
				
				# if it was already treated, skip it
				if next_tile in all_tiles:
					continue
				
				# does it intersect the triangle?
				if tile_intersects_triangle(next_tile):
					# if yes, add it to open list
					open_tiles.append( next_tile )
					all_tiles.append( next_tile )
		
		# return all found tiles
		return all_tiles
