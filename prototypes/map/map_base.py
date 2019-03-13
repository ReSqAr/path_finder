import math

from geometry import halfplane, vector


class MapBase:
    def __init__(self, width, height, data):
        self.width = width
        self.height = height
        self.data = data

    def contains(self, obj):
        """ does the current map contain the point/tile? """
        if isinstance(obj, vector.PointTemplate):
            return 0 <= obj.x <= self.width and 0 <= obj.y <= self.height
        elif isinstance(obj, vector.GridTile):
            return 0 <= obj.x < self.width and 0 <= obj.y < self.height
        else:
            raise TypeError()

    def tiles_iterator(self):
        """ returns an iterator over all tiles """
        for x in range(self.width):
            for y in range(self.height):
                yield vector.GridTile(x, y)

    def __getitem__(self, i):
        assert (isinstance(i, vector.GridTile))
        index = i.x + i.y * self.width
        return self.data[index]

    def __setitem__(self, i, v):
        assert (isinstance(i, vector.GridTile))
        index = i.x + i.y * self.width
        self.data[index] = v

    @staticmethod
    def find_gridpoints_in_triangle_iterator(a, b, c):
        """ find all grid points in the triangle defined by the three points """

        assert (isinstance(a, vector.PointF))
        assert (isinstance(b, vector.PointF))
        assert (isinstance(c, vector.PointF))

        # tolerance for the conversion to integer values
        eps = 1e-6
        eps_floor = lambda x: math.floor(x + eps)
        eps_ceil = lambda x: math.ceil(x - eps)

        # sort the points by ascending y-coordinate
        p_y_min, p_mid, p_y_max = sorted([a, b, c], key=lambda p: p.y)

        # special case: empty triangle
        if p_y_min.y == p_y_max.y:
            return []

        # iterate over all y between
        #   (smallest integer >= p_y_min.y)
        # to
        #   (largest integer <= p_y_max.y)

        # (we use eps here to counter rounding artifacts)
        i_y_min = eps_ceil(p_y_min.y)
        i_y_max = eps_floor(p_y_max.y)

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
                x1, x2 = x2, x1

            # now find the largest integer interval in [x1,x2]
            # (we use eps here to counter rounding artifacts)
            i1 = eps_ceil(x1)
            i2 = eps_floor(x2)

            # communicate the vector
            for i in range(i1, i2 + 1):
                yield vector.GridPoint(i, y)

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
                x1, x2 = x2, x1

            # now find the largest integer interval in [x1,x2]
            # (we use eps here to counter rounding artifacts)
            i1 = eps_ceil(x1)
            i2 = eps_floor(x2)

            # communicate the vector
            for i in range(i1, i2 + 1):
                yield vector.GridPoint(i, y)

            # increase y
            y += 1

    def find_tiles_in_triangle_iterator(self, a, b, c):
        """ find all tiles in the triangle defined by the three points """

        assert (isinstance(a, vector.PointF))
        assert (isinstance(b, vector.PointF))
        assert (isinstance(c, vector.PointF))

        # tolerance for the conversion to integer values
        eps = 1e-6
        eps_floor = lambda x: math.floor(x + eps)
        eps_ceil = lambda x: math.ceil(x - eps)

        # sort the points by ascending y-coordinate
        p_y_min, p_mid, p_y_max = sorted([a, b, c], key=lambda p: p.y)

        # special case: empty triangle
        if p_y_min.y == p_y_max.y:
            return []

        # helper
        def intersection_with_line(y, a, b):
            """
                intersection of y const with the line a->b
                if a->b is parallel to the x-axis, the point b is used
            """
            if b.y - a.y != 0.:
                # careful: the denominator can be zero
                t = (y - a.y) / (b.y - a.y)
                return t * (b.x - a.x) + a.x
            else:
                # otherwise, a->b is parallel to the x-axis
                return b.x

        # iterate over all y between
        #   (largest integer <= p_y_min.y)
        # to
        #   (smallest integer <= p_y_max.y)

        # (we use eps here to counter rounding artifacts)
        i_y_min = eps_floor(p_y_min.y)
        i_y_max = eps_ceil(p_y_max.y)
        i_y_mid = eps_ceil(p_mid.y)

        # special cases:
        # 1. i_y_min == i_y_mid: handled below
        # 2. i_y_max == i_y_mid: handled implicitly
        # 3. i_y_min == i_y_max: cannot happen, excluded above

        # initialise lower_x_min/max
        lower_x_min = eps_floor(p_y_min.x)
        lower_x_max = eps_ceil(p_y_min.x)

        # special case 1.: p_y_min.y == p_mid.y and both are integers
        # then we have to add p_mid.x to the range
        if i_y_min == i_y_mid:
            lower_x_min = min(lower_x_min, eps_floor(p_mid.x))
            lower_x_max = max(lower_x_max, eps_ceil(p_mid.x))

        for y in range(i_y_min, i_y_max):
            # intersection of y+1 const with p_y_min->p_y_max
            if y + 1 <= p_y_max.y:
                x1 = intersection_with_line(y + 1, p_y_min, p_y_max)
            else:
                # but only if it makes sense
                x1 = p_y_max.x

            # find x2
            if y + 1 == i_y_mid:
                # this is the change from p_y_min->p_mid to p_mid->p_y_max
                x2 = p_mid.x
            elif y + 1 <= p_mid.y:
                # we are looking at p_y_min->p_mid
                x2 = intersection_with_line(y + 1, p_y_min, p_mid)
            elif y + 1 <= p_y_max.y:
                # we are looking at p_mid->p_y_max
                # careful: if the line is parallel to the x-axis,
                #          we want p_mid, hence it comes last
                x2 = intersection_with_line(y + 1, p_y_max, p_mid)
            else:
                x2 = p_y_max.x

            # rearrange if needed
            if x2 < x1:
                x1, x2 = x2, x1

            # now find the smallest integer interval containing [x1,x2]
            upper_x_min, upper_x_max = eps_floor(x1), eps_ceil(x2)

            # communicate all the tiles between
            #  min(lower_x_min,upper_x_min)
            # and
            #   max(lower_x_max,upper_x_max)
            i_min = min(lower_x_min, upper_x_min)
            i_max = max(lower_x_max, upper_x_max)

            # communicate the tile
            for i in range(i_min, i_max):
                tile = vector.GridTile(i, y)
                if self.contains(tile):
                    yield tile

            # swap upper to lower
            lower_x_min, lower_x_max = upper_x_min, upper_x_max

    def find_tiles_in_triangle_iterator_slow(self, base, start, end):
        """ find all tiles in the triangle defined by the three points """

        assert (isinstance(base, vector.PointF))
        assert (isinstance(start, vector.PointF))
        assert (isinstance(end, vector.PointF))

        #
        # find orientation
        #
        # compute vectors originating from base
        v_start = start - base
        v_end = end - base
        v_far_edge = end - start

        # compute vector originating from base which goes to the left of v_start
        v_start_left = v_start.left()
        v_end_left = v_end.left()
        v_far_edge_left = v_far_edge.left()

        # find inner direction
        leftness = v_start_left * v_end

        if leftness > 0:
            # inner direction is to the left of v_start, i.e. to the right of v_end
            v_start_normal = v_start_left
            v_end_normal = -v_end_left
            v_far_edge_normal = v_far_edge_left
        elif leftness < 0:
            # inner direction is to the right of v_start
            v_start_normal = -v_start_left
            v_end_normal = v_end_left
            v_far_edge_normal = -v_far_edge_left
        else:  # leftness == 0
            # they are parallel: everything is fine because we assume that
            # the original lines are fine
            return []

        # the triangle is the intersection of the three half planes
        triangle = [
            halfplane.HalfPlane(base, v_start_normal),
            halfplane.HalfPlane(base, v_end_normal),
            halfplane.HalfPlane(start, v_far_edge_normal),
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
        p = vector.GridPoint(int(base.x), int(base.y))

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
                    open_tiles.append(next_tile)
                    all_tiles.append(next_tile)

        # return all found tiles
        return all_tiles
