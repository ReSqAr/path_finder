# -*- coding: utf-8 -*-
import sys
if sys.version_info < (3,2,0):
        raise RuntimeError("Python version >= 3.2 is needed.")

import unittest

import pf_vector
import pf_map_base
import pf_raw_map
import pf_area_map

# available methods:
# - assertFalse, assertTrue
# - assertEqual
# - assertRaises
# - assertIn
# - assertCountEqual
# - assertIsNotNone


class TestBaseMap(unittest.TestCase):
	"""
		test pf_map_base
	"""
	def test_create(self):
		""" test if everything works as expected """
		base_map = pf_map_base.MapBase(10,10,[])
	
	def test_find_gridpoints_in_triangle_iterator(self):
		""" test find_gridpoints_in_triangle_iterator """
		
		# shortcut
		GridPoint = pf_vector.GridPoint
		
		# create map
		base_map = pf_map_base.MapBase(10,10,[])
		
		# triangle (draw it!)
		a = pf_vector.PointF(1,1)
		b = pf_vector.PointF(3,1)
		c = pf_vector.PointF(2,3)
		
		result = list(base_map.find_gridpoints_in_triangle_iterator(a,b,c))
		expected = [GridPoint(1,1), GridPoint(2,1), GridPoint(3,1), GridPoint(2,2), GridPoint(2,3)]
		self.assertEqual(result,expected)

		# triangle (draw it!)
		a = pf_vector.PointF(1,1)
		b = pf_vector.PointF(3,1)
		c = pf_vector.PointF(1,3)
		
		result = list(base_map.find_gridpoints_in_triangle_iterator(a,b,c))
		expected = [GridPoint(1,1), GridPoint(2,1), GridPoint(3,1), GridPoint(1,2), GridPoint(2,2), GridPoint(1,3)]
		self.assertEqual(result,expected)

		# triangle (draw it!)
		a = pf_vector.PointF(6,4)
		b = pf_vector.PointF(3,1)
		c = pf_vector.PointF(1,3)
		
		result = list(base_map.find_gridpoints_in_triangle_iterator(a,b,c))
		expected = [GridPoint(3,1), GridPoint(2,2), GridPoint(3,2), GridPoint(4,2), GridPoint(1,3), GridPoint(2,3), GridPoint(3,3), GridPoint(4,3), GridPoint(5,3), GridPoint(6,4)]
		self.assertEqual(result,expected)

		# triangle (draw it!)
		a = pf_vector.PointF(5,5)
		b = pf_vector.PointF(3,1)
		c = pf_vector.PointF(1,3)
		
		result = list(base_map.find_gridpoints_in_triangle_iterator(a,b,c))
		expected = [GridPoint(3,1), GridPoint(2,2), GridPoint(3,2), GridPoint(1,3), GridPoint(2,3), GridPoint(3,3), GridPoint(4,3), GridPoint(3,4), GridPoint(4,4), GridPoint(5,5)]
		self.assertEqual(result,expected)

		# triangle (draw it!)
		a = pf_vector.PointF(1,1)
		b = pf_vector.PointF(2,1)
		c = pf_vector.PointF(3,1)
		
		result = list(base_map.find_gridpoints_in_triangle_iterator(a,b,c))
		expected = []
		self.assertEqual(result,expected)
		
	
	def test_find_tiles_in_triangle_iterator(self):
		""" test find_tiles_in_triangle_iterator """
		
		# shortcut
		GridTile = pf_vector.GridTile
		
		# create map
		base_map = pf_map_base.MapBase(10,10,[])
		
		# shortcut
		f = base_map.find_tiles_in_triangle_iterator
		#f = lambda a,b,c: sorted(base_map.find_tiles_in_triangle_iterator_slow(a,b,c), key=lambda t: (t.y,t.x))
		
		# triangle (draw it!)
		a = pf_vector.PointF(1,1)
		b = pf_vector.PointF(3,1)
		c = pf_vector.PointF(2,3)
		
		result = list(f(a,b,c))
		expected = [GridTile(1,1), GridTile(2,1), GridTile(1,2), GridTile(2,2)]
		self.assertEqual(result,expected)

		# triangle (draw it!)
		a = pf_vector.PointF(1,1)
		b = pf_vector.PointF(2,2)
		c = pf_vector.PointF(1,3)
		
		result = list(f(a,b,c))
		expected = [GridTile(1,1), GridTile(1,2)]
		self.assertEqual(result,expected)

		# triangle (draw it!)
		a = pf_vector.PointF(1,1)
		b = pf_vector.PointF(2,1.8)
		c = pf_vector.PointF(1,3)
		
		result = list(f(a,b,c))
		expected = [GridTile(1,1), GridTile(1,2)]
		self.assertEqual(result,expected)

		# triangle (draw it!)
		a = pf_vector.PointF(1,1)
		b = pf_vector.PointF(2,2.2)
		c = pf_vector.PointF(1,3)
		
		result = list(f(a,b,c))
		expected = [GridTile(1,1), GridTile(1,2)]
		self.assertEqual(result,expected)

		# triangle (draw it!)
		a = pf_vector.PointF(1.8,1.2)
		b = pf_vector.PointF(2.1,1.2)
		c = pf_vector.PointF(2.1,2.1)
		
		result = list(f(a,b,c))
		expected = [GridTile(1,1),GridTile(2,1),GridTile(2,2)]
		self.assertEqual(result,expected)

		# triangle (draw it!)
		# special case 2. i_y_max == i_y_mid
		a = pf_vector.PointF(1.2,1.8)
		b = pf_vector.PointF(1.2,2.1)
		c = pf_vector.PointF(2.1,2.2)
		
		result = list(f(a,b,c))
		expected = [GridTile(1,1),GridTile(1,2),GridTile(2,2)]
		self.assertEqual(result,expected)

		# triangle (draw it!)
		# special case 2. i_y_max == i_y_mid
		a = pf_vector.PointF(1.2,1.8)
		b = pf_vector.PointF(2.1,2.1)
		c = pf_vector.PointF(1.2,2.2)
		
		result = list(f(a,b,c))
		expected = [GridTile(1,1),GridTile(1,2),GridTile(2,2)]
		self.assertEqual(result,expected)

		# triangle (draw it!)
		# special case 1. i_y_min == i_y_mid
		a = pf_vector.PointF(1,1)
		b = pf_vector.PointF(2.1,1)
		c = pf_vector.PointF(1,2)
		
		result = list(f(a,b,c))
		expected = [GridTile(1,1),GridTile(2,1)]
		self.assertEqual(result,expected)


class TestRawMap(unittest.TestCase):
	"""
		test pf_raw_map
	"""
	raw_map_path = "example.pgm"
	
	def test_create(self):
		""" test if everything works as expected """
		raw_map = pf_raw_map.RawMap.read(self.raw_map_path)
	
class TestAreaMap(unittest.TestCase):
	"""
		test pf_area_map
	"""
	def test_create(self):
		""" test if everything works as expected """
		raw_map = pf_raw_map.RawMap(10,10,100*[0])
		area_map = pf_area_map.AreaMap(raw_map, lambda _: True)
	
	def test_find_obstruction_when_transforming_line(self):
		""" test find_obstruction_when_transforming_line """
		raw_map = pf_raw_map.RawMap(10,10,100*[0])
		area_map = pf_area_map.AreaMap(raw_map, lambda _: True)

		base = pf_vector.PointF(2,2)
		start = pf_vector.PointF(8,2)
		end = pf_vector.PointF(2,8)

		#print(area_map.find_tiles_in_triangle(base, start, end)) 

		self.assertEqual(area_map.find_obstruction_when_transforming_line(base, start, end),
		                  (1.0, None))

		area_map[pf_vector.GridTile(4,4)] = 0 # 4,4 is now unpassable
		self.assertEqual(area_map.find_obstruction_when_transforming_line(base, start, end),
		                  (0.4, pf_vector.GridPoint(5, 4)))

		area_map[pf_vector.GridTile(6,3)] = 0 # 6,3 is now unpassable
		self.assertEqual(area_map.find_obstruction_when_transforming_line(base, start, end),
		                  (1./6., pf_vector.GridTile(7, 3)))

		area_map[pf_vector.GridTile(4,2)] = 0 # 4,2 is now unpassable
		self.assertEqual(area_map.find_obstruction_when_transforming_line(base, start, end),
		                  (0., pf_vector.GridPoint(5, 2)))

		area_map[pf_vector.GridTile(2,2)] = 0 # 2,2 is now unpassable
		self.assertEqual(area_map.find_obstruction_when_transforming_line(base, start, end),
		                  (0., pf_vector.GridPoint(5, 2)))

		# test angle > 90
		base = pf_vector.PointF(6,4)
		start = pf_vector.PointF(9,5)
		end = pf_vector.PointF(3,5)
		self.assertEqual(area_map.find_obstruction_when_transforming_line(base, start, end),
		                  (2./3., pf_vector.GridPoint(5, 5)))

		base = pf_vector.PointF(3,3)
		start = pf_vector.PointF(0,5)
		end = pf_vector.PointF(9,7)
		self.assertEqual(area_map.find_obstruction_when_transforming_line(base, start, end),
		                  (0.5, pf_vector.GridPoint(4, 5)))

		area_map[pf_vector.GridTile(6,5)] = 0 # 6,5 is now unpassable
		self.assertEqual(area_map.find_obstruction_when_transforming_line(base, start, end),
		                  (0.5, pf_vector.GridPoint(4, 5)))

		area_map[pf_vector.GridTile(4,4)] = -1 # 4,4 is now passable again
		self.assertEqual(area_map.find_obstruction_when_transforming_line(base, start, end),
		                  (5./7., pf_vector.GridPoint(6, 6)))

	def test_optimise_point_to_line(self):
		""" test optimise_point_to_line """
		raw_map = pf_raw_map.RawMap(10,10,100*[0])
		area_map = pf_area_map.AreaMap(raw_map, lambda _: True)

		p = pf_vector.PointF(3,4)
		a = pf_vector.PointF(2,0)
		b = pf_vector.PointF(4,0)
		p0 = a

		# direct path p->(3,0) is valid and optimal
		self.assertEqual(area_map.optimise_point_to_line(p,p0,a,b),
		                  pf_vector.PathF([p,pf_vector.PointF(3,0)]))

		# direct path p->a is valid and optimal
		p = pf_vector.PointF(1,4)
		self.assertEqual(area_map.optimise_point_to_line(p,p0,a,b),
		                  pf_vector.PathF([p,a]))

		# direct path p->b is valid and optimal
		p = pf_vector.PointF(5,4)
		self.assertEqual(area_map.optimise_point_to_line(p,p0,a,b),
		                  pf_vector.PathF([p,b]))
		
		print("h")
		# direct path p->b is not valid anymore, but
		# p->(3,2)->(3,0) is valid and optimal.
		# also note that p->a is valid.
		area_map[pf_vector.GridTile(3,1)] = 0 # 3,1 is now unpassable
		p = pf_vector.PointF(4,4)
		self.assertEqual(area_map.optimise_point_to_line(p,p0,a,b),
		        pf_vector.PathF([p,pf_vector.PointF(3,2),pf_vector.PointF(3,0)]))
	
	def optimise_path_loose_ends(self):
		""" test optimise_path_loose_ends """
		raw_map = pf_raw_map.RawMap(10,10,100*[0])
		area_map = pf_area_map.AreaMap(raw_map, lambda _: True)

		start_a = pf_vector.PointF(2,0)
		start_b = pf_vector.PointF(4,0)
		end_a = pf_vector.PointF(4,4)
		end_b = pf_vector.PointF(6,4)

		# direct start_b->end_a is valid and optimal
		path = pf_vector.PathF([start_a,end_b])
		self.assertEqual(area_map.optimise_path_loose_ends(path,start_a,start_b,end_a,end_b),
		                  pf_vector.PathF([start_b,end_a]))

		area_map[pf_vector.GridTile(3,1)] = 0 # 3,1 is now unpassable
		# direct start_b->end_a is not valid anymore. however
		# (3,0)->(3,2)->end_a is. note that start_a->end_a is valid
		path = pf_vector.PathF([start_a,end_a])
		self.assertEqual(area_map.optimise_path_loose_ends(path,start_a,start_b,end_a,end_b),
		                  pf_vector.PathF([pf_vector.PointF(3,0),pf_vector.PointF(3,2),end_a]))

		area_map[pf_vector.GridTile(3,1)] = -1 # 3,1 is now passable again

		# small number
		eps = 0.001

		# slow convergance (fixed by preprocess step)
		start_a = pf_vector.PointF(2,0)
		start_b = pf_vector.PointF(4,eps)
		end_a = pf_vector.PointF(2,4)
		end_b = pf_vector.PointF(4,4-eps)

		# direct start_b->end_b is valid and optimal
		path = pf_vector.PathF([start_a,end_a])
		self.assertEqual(area_map.optimise_path_loose_ends(path,start_a,start_b,end_a,end_b),
		                  pf_vector.PathF([start_b,end_b]))

		area_map[pf_vector.GridTile(2,1)] = 0 # 2,1 is now unpassable
		# prevented convergance catastrophe (fixed by preprocess step)
		start_a = pf_vector.PointF(0,0)
		start_b = pf_vector.PointF(10,1.5)
		end_a = pf_vector.PointF(0,3)
		end_b = pf_vector.PointF(10,1.5)

		# optimal is ???->(3,1)->(3,2)->???
		path = pf_vector.PathF([start_a,end_a])
		self.assertEqual(area_map.optimise_path_loose_ends(path,start_a,start_b,end_a,end_b),
		                  pf_vector.PathF([
											pf_vector.PointF(860/409.,129/409.),
											pf_vector.PointF(2,1),
											pf_vector.PointF(2,2),
											pf_vector.PointF(860/409.,1098/409.)
										]))

		# convergance catastrophe (fixed by preprocess step)
		start_a = pf_vector.PointF(2,0)
		start_b = pf_vector.PointF(4,eps)
		end_a = pf_vector.PointF(2,2*eps)
		end_b = pf_vector.PointF(4,eps)

		# degerenates to start_b=end_b
		path = pf_vector.PathF([start_a,end_a])
		self.assertEqual(area_map.optimise_path_loose_ends(path,start_a,start_b,end_a,end_b),
		                 pf_vector.PathF([start_b,end_b]))



class TestInfluenceMap(unittest.TestCase):
	"""
		test pf_area_map
	"""
	def test_create(self):
		""" test if everything works as expected """
		raw_map = pf_raw_map.RawMap(10,10,100*[0])
		area_map = pf_area_map.AreaMap(raw_map, lambda _: True)
		influence_map = pf_area_map.InfluenceMap(area_map)
	
if __name__ == '__main__':
	unittest.main()
