import collections

import pf_vector
import pf_map_base


class InfluenceMap(pf_map_base.MapBase):
    """
		balloon the boundary area while preserving the homotopy type of the loops
	"""

    def __init__(self, area_map):
        # save the area map
        self.area_map = area_map

        # initialise influence data with the area map data
        super(InfluenceMap, self).__init__(self.area_map.width,
                                           self.area_map.height,
                                           self.area_map.data[:])
        # dictionary: area_id -> loops of influence boundaries
        self.boundaries = {}

        # create area map
        self._create_influence_map()

    def _create_influence_map(self):
        # go through the edges and find all loops
        for area_id, edges in self.area_map.edges.items():
            self.boundaries[area_id] = self.decompose_edges_into_loops(edges)

        print("ballooning boundaries... ")

        step = 0
        # ballooning boundaries
        while True:
            step += 1
            print("expansion step number %d..." % step)

            # was a boundary expanded? if not, we are done
            expanded = False

            # keep track of finished loops
            finished_loops = []

            for area_id, loops in self.boundaries.items():
                for loop_id in range(len(loops)):
                    # skip if the loop is finished
                    if (area_id, loop_id) in finished_loops:
                        continue

                    # the old loop which we want to expand
                    loop = loops[loop_id]

                    # the new, expanded loop
                    loop_expanded, new_loop = self.__expand_loop(area_id, loop)

                    # replace the old loop
                    loops[loop_id] = new_loop

                    # keep track of the expanded state
                    expanded |= loop_expanded

                    # keep track of finished loops
                    if loop_expanded:
                        finished_loops.append((area_id, loop_id))

            # we are done if nothing was expanded
            if not expanded:
                break

    def __expand_loop(self, area_id, loop):
        """
			expand the given loop and mark all new areas with
			the given area_id
		"""
        # compute an pseudo in-place update array
        update_loop = PseudoInPlaceUpdateArray(loop)

        # keep track if the loop was expanded
        loop_expanded = False

        # go through edges of loop and see if we can expand it
        # (use index based iterator as the list is going to change)
        while not update_loop.is_finished():
            # get current edge and compute outer tile, i.e. the tile to the left
            edge = update_loop.get(0)
            tile_outer = edge.left_tile()

            # keep the original if the tile does not define a valid tile,
            # i.e. the tile does not belong to the grid
            if not self.contains(tile_outer):
                update_loop.confirm()
                continue

            # keep the original if the outer tile was already assigned to an area
            if self[tile_outer] != self.area_map.no_area_id:
                update_loop.confirm()
                continue

            # set expanded to true as we are going to expand the current edge
            loop_expanded = True

            # mark the new area
            self[tile_outer] = area_id

            # get left facing vector
            v_left = edge.direction().left()

            # create new points by translating the old ones to the left
            new_a, new_b = edge.a + v_left, edge.b + v_left
            new_a = pf_vector.GridPoint(new_a.x, new_a.y)
            new_b = pf_vector.GridPoint(new_b.x, new_b.y)

            # the configuration looks like that:
            # new_a----new_b
            #     |    |
            #     |    |
            # ----a----b-----
            # i-1   i    i+1

            #
            # compute the plan
            #

            # if the (i-1)-th edge is the inverse of a->new_a,
            # then the (i-1)-th gets annihilated
            edge_imm = update_loop.get(-1)
            # it always holds that edge_imm.b == edge.a
            assert (edge_imm.b == edge.a)
            imm_annihilated = (edge_imm.a == new_a)

            # if the (i-1)-th edge get annihilated and
            # (i-2)-th edge is the inverse of the edge new_a->new_b,
            # then the (i-2)-th gets annihilated
            edge_immmm = update_loop.get(-2)
            if imm_annihilated:
                assert (edge_immmm.b == new_a)
            immmm_annihilated = imm_annihilated and (edge_immmm.a == new_b)

            # if the (i+1)-th edge is the inverse of new_b->b,
            # then the (i+1)-th gets annihilated
            edge_ipp = update_loop.get(+1)
            # it always holds that edge.b == edge[ipp].a
            assert (edge.b == edge_ipp.a)
            ipp_annihilated = (new_b == edge_ipp.b)

            # if the (i+1)-th edge get annihilated and
            # (i+2)-th edge is the inverse of the edge new_a->new_b,
            # then the (i+2)-th gets annihilated
            edge_ipppp = update_loop.get(+2)
            if ipp_annihilated:
                assert (edge_ipppp.a == new_b)
            ipppp_annihilated = ipp_annihilated and (edge_ipppp.b == new_a)

            #
            # add and remove edges accordingly
            #
            if imm_annihilated:
                # delete the edge
                update_loop.delete(-1)
                # if we also have to delete the other edge
                if immmm_annihilated:
                    update_loop.delete(-1)
            else:
                # we have to add the edge a->new_a
                new_edge = pf_vector.GridEdge(edge.a, new_a)
                update_loop.insert(new_edge)

            # delete the current edge
            update_loop.delete(0)

            if immmm_annihilated or ipppp_annihilated:
                # we do not have to add the edge new_a->new_b
                pass
            else:
                # we have to add it
                new_edge = pf_vector.GridEdge(new_a, new_b)
                update_loop.insert(new_edge)

            if ipp_annihilated:
                # delete the edge (-1 as we just deleted the current edge)
                update_loop.delete(+1 - 1)
                # if we also have to delete the other edge
                if ipppp_annihilated and not immmm_annihilated:
                    update_loop.delete(+1 - 1)
            else:
                # we have to add the new_b->edge b
                new_edge = pf_vector.GridEdge(new_b, edge.b)
                update_loop.insert(new_edge)

        new_loop = update_loop.get_array()
        # if the loop is empty, add the smallest possible loop
        # (this is only a hack, still the situation probably only arises
        #  under synthetic conditions)
        if not new_loop:
            # create the smallest loop a->b and b->a
            edge = loop[0]
            inverse_edge = pf_vector.GridEdge(edge.b, edge.a)
            new_loop = [edge, inverse_edge]
            return False, new_loop

        return loop_expanded, new_loop

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
                edge = min(es, key=valuation)

                # add edge to loop and remove it from the big list
                loop.append(edge)
                edges.remove(edge)

            # add loop
            loops.append(loop)

        print("done, found loops of length: %s" % ", ".join(str(len(loop)) for loop in loops))

        # return loops
        return loops

    def nearest_area_grid_point_in_sector(self, base, path_a, path_b):
        """
			Find the nearest (grid) point to the (grid) point base which lies
			between the GridPaths path_a and path_b. The sector is spanned
			clock-wise from path_a to path_b.
			
			Careful: the left/right means here left or right from the path as seen from
					the point base, i.e. the left end of the sector is path_a hence we
					include everything right of path_a
			
			TODO: code seems to be unstable
		"""
        assert (isinstance(base, pf_vector.GridPoint))
        assert (isinstance(path_a, pf_vector.GridPath))
        assert (isinstance(path_b, pf_vector.GridPath))

        # compute the tile to the right of path_a[0]->path_a[1]
        tile_right = pf_vector.GridEdge(path_a.points[0], path_a.points[1]).right_tile()
        # determine the area id of the right tile
        if self.contains(tile_right):
            area_id = self[tile_right]
        else:
            area_id = self.area_map.no_area_id + 1  # wall id

        # determine points which are off limit, i.e. left of path_a and right of path_b
        # again, the perspective we take is from the point base

        off_limit_points_a = set()
        for p1, p0 in zip(path_a.points[1:], path_a.points[:-1]):
            # compute the tile to the left of p0->p1
            tile_left = pf_vector.GridEdge(p0, p1).left_tile()
            # the points left to path_a are off limit
            off_limit_points_a |= set(tile_left.adjacent_points())
        # the points on the line are fine
        for p in path_a.points:
            off_limit_points_a.discard(p)

        off_limit_points_b = set()
        for p1, p0 in zip(path_b.points[1:], path_b.points[:-1]):
            # compute the tile to the right of p0->p1
            tile_right = pf_vector.GridEdge(p0, p1).right_tile()
            # the points right to path_b are off limit
            off_limit_points_b |= set(tile_right.adjacent_points())
        # the points on the line are fine
        for p in path_b.points:
            off_limit_points_b.discard(p)

        # then collect the off limit points. we have to compute them
        # separately to avoid masking problems
        off_limit_points = off_limit_points_a | off_limit_points_b

        # initialise open points, i.e. points which have still to propagate
        open_points = [base]
        # initialise set of all seen points
        seen_points = set(open_points)

        while open_points:
            # get a new point (breadth search)
            point = open_points.pop(0)
            # check area_id
            point_area_id = self.area_map.get_point_area_id(point)

            # if the point has the right area_id, then we use it
            if point_area_id == area_id:
                # this is only an approximation to the closest point,
                # but this should be enough
                return point

            # if the point has an area_id, but the wrong one
            if point_area_id != self.area_map.no_area_id and point_area_id != area_id:
                # then skip it except it is one of the early nodes
                # (there is no harm as this is (almost) entirely an optimisation)
                if len(seen_points) > 6:
                    continue

            # propagate (along x-/y-axis, not the diagonal)
            for new_point in point.directly_adjacent_points():
                # if the point is forbidden, leave it
                if new_point in off_limit_points:
                    continue

                # propagate the point further (if it is indeed new)
                if new_point not in seen_points:
                    open_points.append(new_point)
                    seen_points.add(new_point)

        raise RuntimeError("Cannot find gate for %s." % base)


class PseudoInPlaceUpdateArray:
    """
		Helper class which helps with in place updates.
		
		Methods:
		- constructor: Takes the array which is to be updated.
		- is_finished: Are we finished?
		- get_array(): If we are finished, get the new array.
		- length: Compute the length of the total array.
		- get(rel_pos): rel_pos=0 gets the current element,
		                i.e. the first which was not yet updated.
		- delete(rel_pos): Deletes the requested element.
		- insert(new_element): Insert new_element directly before the current one.
		- confirm: confirm the current element
	"""

    def __init__(self, array):
        self._old_array = array
        self._new_array = []

        self._old_array_range_start = 0
        self._old_array_range_end = len(self._old_array)

    def is_finished(self):
        """
			Is the update finished?
		"""
        # we are finished when the there are no more new elements
        return self._old_array_range_start >= self._old_array_range_end

    def get_array(self):
        """
			Return the new array if we are finished.
		"""
        assert (self.is_finished())
        return self._new_array

    def length(self):
        """
			Compute the length of the total array.
		"""
        return len(self._new_array) + self._old_array_range_end - self._old_array_range_start

    def _rel_abs_position(self, rel_pos):
        """
			Compute the absolute position which corresponds to rel_pos.
			The array is indexed as we would have a long array
			new_array + old_array[start:end].
			
			Example:
				old_array = [d,e,f]
				new_array = [a,b,c]
				start = 1
				end = 3
				[local variable array_length=5]
				_rel_abs_position:
					-2 -> 1
					-1 -> 2
					0  -> 3
					1  -> 4
					2  -> 0
		"""
        # compute the length of the total array
        array_length = self.length()
        # compute the position in the total array
        abs_pos = len(self._new_array) + rel_pos
        # normalise the position
        return abs_pos % array_length

    def get(self, rel_pos):
        """
			Get the element, it is addressed relative to the current one,
			which is the first element which was not yet updated.

			Example:
				old_array = [d,e,f]
				new_array = [a,b,c]
				start = 1
				end = 3

				get:
					-2 -> abs_pos=1, if branch, 'b'
					-1 -> abs_pos=2, if branch, 'c'
					0  -> abs_pos=3, else branch, pos = 3-3+1=1, 'e'
					1  -> abs_pos=4, else branch, pos = 4-3+1=2, 'f'
					2  -> abs_pos=0, if branch, 'a'
		"""
        abs_pos = self._rel_abs_position(rel_pos)
        # get the element by the absolute position
        if abs_pos < len(self._new_array):
            # the element is in the new array
            return self._new_array[abs_pos]
        else:
            # the element is in the old array
            pos = (abs_pos - len(self._new_array)) + self._old_array_range_start
            return self._old_array[pos]

    def delete(self, rel_pos):
        """
			Delete the element.

			Example:
				old_array = [d,e,f,g]
				new_array = [a,b,c]
				start = 1
				end = 4

				get:
					-2 -> abs_pos=1, if branch, 'b'
					-1 -> abs_pos=2, if branch, 'c'
					0  -> abs_pos=3, else branch, pos = 3-3+1=1, if branch
					1  -> abs_pos=4, else branch, pos = 4-3+1=2, else branch
					2  -> abs_pos=5, else branch, pos = 5-3+1=3, elif branch
					3  -> abs_pos=0, if branch, 'a'
		"""
        abs_pos = self._rel_abs_position(rel_pos)
        # find the element by the absolute position
        if abs_pos < len(self._new_array):
            # the element is in the new array:
            # indeed, delete it
            del self._new_array[abs_pos]
        else:
            # the element is in the old array:
            # don't delete it, just mask the position
            pos = (abs_pos - len(self._new_array)) + self._old_array_range_start
            if pos == self._old_array_range_start:
                # advance start
                self._old_array_range_start += 1
            elif pos == self._old_array_range_end - 1:
                # advance end
                self._old_array_range_end -= 1
            else:
                print("rel_pos:", rel_pos)
                print("len(self._old_array):", len(self._old_array))
                print("len(self._new_array):", len(self._new_array))
                print("abs_pos:", abs_pos)
                print("pos:", pos)
                print("self._old_array_range_start:", self._old_array_range_start)
                print("self._old_array_range_end:", self._old_array_range_end)
                raise ValueError("delete improperly used")
            assert (self._old_array_range_start <= self._old_array_range_end)

    def insert(self, new_element):
        """
			Insert new_element directly before the current one.
		"""
        self._new_array.append(new_element)

    def confirm(self):
        """
			Confirm the current element. Equivalent to:
			x = array.get(0)
			array.delete(0)
			array.insert(x)
		"""
        assert (not self.is_finished())
        # get the element
        element = self._old_array[self._old_array_range_start]
        # delete it
        self._old_array_range_start += 1
        # add it to the new array
        self._new_array.append(element)
