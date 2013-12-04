import math

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
	
	def find_gridpoints_in_triangle_iterator(self, a, b, c):
		""" find all grid points in the triangle defined by the three points """

		assert(isinstance(a,pf_vector.PointF))
		assert(isinstance(b,pf_vector.PointF))
		assert(isinstance(c,pf_vector.PointF))
		
		# tolerance for the conversion to integer values
		eps = 1e-6
		
		# sort the points by ascending y-coordinate
		p_y_min,p_mid,p_y_max = sorted([a,b,c],key=lambda p:p.y)
		
		# special case: empty triangle
		if p_y_min.y == p_y_max.y:
			return []
		
		# iterate over all y between
		#   (smallest integer >= p_y_min.y)
		# to
		#   (largest integer <= p_y_max.y)
		
		# (we use eps here to counter rounding artifacts)
		i_y_min = math.ceil(p_y_min.y - eps)
		i_y_max = math.floor(p_y_max.y + eps)

		# initialise y
		y = i_y_min
		
		while y <= p_mid.y:
			# compute the x value of the intersection const y
			# and the line p_y_min->p_y_max
			# i.e. solve the equation
			#  t (p_y_max - p_y_min) + p_y_min = s e_x + (0,y)
			# multiply the equation with e_y, then
			#  t (<p_y_max,e_y> - <p_y_min,e_y>) + <p_y_min,e_y> = y
			t = (y - p_y_min.y) / (p_y_max.y - p_y_min.y)
			# then we can calculate x
			x1 = t * (p_y_max.x - p_y_min.x) + p_y_min.x
			
			# compute the other x, it is the intersection with p_y_min->p_mid
			if p_mid.y - p_y_min.y != 0.:
				# careful: the denominator here can be zero
				t = (y - p_y_min.y) / (p_mid.y - p_y_min.y)
				x2 = t * (p_mid.x - p_y_min.x) + p_y_min.x
			else:
				# otherwise, p_y_min->p_mid is parallel to the x-axis
				x2 = p_mid.x
			
			# rearrange if needed
			if x2 < x1:
				x1,x2 = x2,x1
			
			# now find the largest integer interval in [x1,x2]
			# (we use eps here to counter rounding artifacts)
			i1 = math.ceil(x1 - eps)
			i2 = math.floor(x2 + eps)
			
			# communicate the vector
			for i in range(i1,i2+1):
				yield pf_vector.GridPoint(i,y)
			
			# increase y
			y += 1

		while y <= i_y_max:
			# compute the x value of the intersection const y
			# and the line p_y_min->p_y_max
			t = (y - p_y_min.y) / (p_y_max.y - p_y_min.y)
			x1 = t * (p_y_max.x - p_y_min.x) + p_y_min.x
			
			# compute the other x, it is now the intersection with p_mid->p_y_max
			if p_y_max.y - p_mid.y != 0.:
				# careful: the denominator here can be zero
				t = (y - p_mid.y) / (p_y_max.y - p_mid.y)
				x2 = t * (p_y_max.x - p_mid.x) + p_mid.x
			else:
				# otherwise, p_y_min->p_mid is parallel to the x-axis
				x2 = p_mid.x
			
			# rearrange if needed
			if x2 < x1:
				x1,x2 = x2,x1
			
			# now find the largest integer interval in [x1,x2]
			# (we use eps here to counter rounding artifacts)
			i1 = math.ceil(x1 - eps)
			i2 = math.floor(x2 + eps)
			
			# communicate the vector
			for i in range(i1,i2+1):
				yield pf_vector.GridPoint(i,y)
			
			# increase y
			y += 1
		
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
