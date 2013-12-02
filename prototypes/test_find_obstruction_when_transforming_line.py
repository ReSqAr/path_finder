import pf_vector
import pf_map
import pf_area_map


raw_map = pf_map.Map(10,10,100*[0])
area_map = pf_area_map.AreaMap(raw_map, lambda _: True)

base = pf_vector.PointF(2,2)
start = pf_vector.PointF(8,2)
end = pf_vector.PointF(2,8)

#print(area_map.find_tiles_in_triangle(base, start, end)) 

print(area_map.find_obstruction_when_transforming_line(base, start, end) )
print("Out: (1.0, None) ")
print()

area_map[pf_vector.GridTile(4,4)] = 0 # 4,4 is now unpassable
print(area_map.find_obstruction_when_transforming_line(base, start, end) )
print("Out: (0.4, pf_vector.GridTile(5, 4))")
print()

area_map[pf_vector.GridTile(6,3)] = 0 # 6,3 is now unpassable
print(area_map.find_obstruction_when_transforming_line(base, start, end) )
print("Out: (0.16666666666666666, pf_vector.GridPoint(7, 3))")
print()

area_map[pf_vector.GridTile(4,2)] = 0 # 4,2 is now unpassable
print(area_map.find_obstruction_when_transforming_line(base, start, end) )
print("Out: (0.0, pf_vector.GridPoint(5, 2))")
print()

area_map[pf_vector.GridTile(2,2)] = 0 # 2,2 is now unpassable
print(area_map.find_obstruction_when_transforming_line(base, start, end) )
print("Out: (0.0, pf_vector.GridPoint(5, 2))")
print()

# test angle > 90
base = pf_vector.PointF(6,4)
start = pf_vector.PointF(9,5)
end = pf_vector.PointF(3,5)

print(area_map.find_obstruction_when_transforming_line(base, start, end) )
print("Out: (0.66666666666666666, pf_vector.GridPoint(5, 5))")
print()

base = pf_vector.PointF(3,3)
start = pf_vector.PointF(0,5)
end = pf_vector.PointF(9,7)

print(area_map.find_obstruction_when_transforming_line(base, start, end) )
print("Out: (0.5, pf_vector.GridPoint(4, 5))")
print()

area_map[pf_vector.GridTile(6,5)] = 0 # 6,5 is now unpassable

print(area_map.find_obstruction_when_transforming_line(base, start, end) )
print("Out: (0.5, pf_vector.GridPoint(4, 5))")
print()

area_map[pf_vector.GridTile(4,4)] = -1 # 4,4 is now passable again

print(area_map.find_obstruction_when_transforming_line(base, start, end) )
print("Out: (0.7142857142857143, pf_vector.GridPoint(6, 6))")
print()

