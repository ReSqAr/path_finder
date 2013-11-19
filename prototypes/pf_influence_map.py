import collections

import pf_vector
import pf_map


class InfluenceMap(pf_map.Map):
	"""
		balloon the boundary area while preserving the homotopy type of the loops
	"""
	def __init__(self, area_map,):
		# save the area map
		self.area_map = area_map

		# initialise influence data with the area map data
		super(InfluenceMap,self).__init__(self.area_map.width,
		                                  self.area_map.height,
		                                  self.area_map.data[:])
		# dictionary: area_id -> loops of influence boundaries
		self.boundaries = {}
		
		# create area map
		self._create_influence_map()
	
	def _create_influence_map(self):
		# go through the edges and find all loops
		for area_id,edges in self.area_map.edges.items():
			self.boundaries[area_id] = self.decompose_edges_into_loops(edges)

		print("balloon boundaries... ")

		step = 0
		# ballon boundaries
		while True:
			step += 1
			print("expansion step number %d..." % step)

			# was a boundary expanded? if not, we are done
			expanded = False
			
			for area_id,loops in self.boundaries.items():
				for loop_id,loop in enumerate(loops):
					
					# go through edges of loop and see if we can expand it
					# (use index based iterator as the list is going to change)
					i = 0 # edge in dex
					while i < len(loop):
						# get edge and compute outer tile, i.e. the tile to the left
						edge = loop[i]
						tile_outer = edge.left_tile()
						
						# skip the edge if the tile does not define a valid tile
						if not self.contains(tile_outer):
							i += 1
							continue
						
						# skip the edge if the tile was already assigned to an area
						if self[tile_outer] != self.area_map.no_area_id:
							i += 1
							continue
						
						# set expanded to true as we are going to expand the current edge
						expanded = True
						
						# get left facing vector
						v_left = edge.direction().left()

						# create new points by translating to the left
						new_a,new_b = edge.a+v_left,edge.b+v_left
						new_a = pf_vector.GridPoint(new_a.x,new_a.y)
						new_b = pf_vector.GridPoint(new_b.x,new_b.y)
						
						new_edges = []
						# connect old a to new a
						new_edges.append( pf_vector.GridEdge(edge.a,new_a) )
						# connect new a to new b
						new_edges.append( pf_vector.GridEdge(new_a,new_b) )
						# connect new b to old b
						new_edges.append( pf_vector.GridEdge(new_b,edge.b) )
						
						# replace it and mark the new area
						loop[i:i+1] = new_edges
						self[tile_outer] = area_id
						# care about i: we inserted something before i
						i += 1
						next_i = i+2
						
						# delete unnecessay edges
						edges = [loop[(i+x) % len(loop)] for x in range(-2*2,2*2+1)]
						while len(loop) > 2 and edges:
							for e1,e2 in zip(edges[:-1],edges[1:]):
								# it always holds that e1.b == e2.a
								if e1.b != e2.a:
									print(area_id, loop_id)
									print(len(loop))
									print(loop)
									
								# if also holds that e1.a == e2.b, then the
								# edge is superflous and can be removed
								if e1.a == e2.b:
									# remove the edges from the edges list
									edges.remove(e1)
									edges.remove(e2)
									# remove e1 from the loop list and care about i
									index_e1 = loop.index(e1)
									del loop[index_e1]
									if index_e1 < next_i:
										next_i -= 1
									# remove e2 from the loop list and care about i
									index_e2 = loop.index(e2)
									del loop[index_e2]
									if index_e2 < next_i:
										next_i -= 1
									# restart the process
									break
							else:
								# we have done nothing, so we are finished
								break
								
						# advance i
						i = next_i
		
			# we are done if nothing was expanded
			if not expanded:
				break
		

	@staticmethod
	def decompose_edges_into_loops(edges):
		""" decompose edges into loops """
		print("finding loops in %d edges... " % len(edges))
		
		# copy edges and create loop array
		edges = list(edges)
		loops = []
		
		# create helper dictionary and fill it
		edge_from_point = collections.defaultdict(list)
		for edge in edges:
			edge_from_point[edge.a].append(edge)
		
		while edges:
			# get the next best element
			edge = edges.pop()
			
			# if we find an edge ending at the start_point, we completed the loop
			start_point = edge.a
			# start the loop
			loop = [edge]
			
			# we are looking for the next edge
			while edge.b != start_point:
				# find all edges which start at edge.b (but not end at edge.a)
				es = edge_from_point[edge.b]
				# compute the right facing vector
				v_right = edge.direction().right()
				
				# the prefered order is: left, straight, right, so we want to
				# find the vector with the smallest scalar product with v_right
				valuation = lambda e: v_right * e.direction()
				edge = min(es,key=valuation)

				# add edge to loop and remove it from the big list
				loop.append( edge )
				edges.remove( edge )

			# add loop
			loops.append(loop)
		
		print("done, found loops of length: %s" % ", ".join(str(len(loop)) for loop in loops))
		
		# return loops
		return loops
