class Vector:
    """
		This class represents a general vector, independent of its purpose.
		
		C++: template class with variable type T
		Problem: x + y is of type Vector
		Solution: use x += y to change an existing vector
	"""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __neg__(self):
        """ return -self """
        return Vector(-self.x, -self.y)

    def __add__(self, other):
        """ return self + other """
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        """ return self - other """
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        """ returns the scalar product """
        assert (isinstance(other, Vector))
        return self.x * other.x + self.y * other.y

    def __rmul__(self, other):
        """ returns self scaled by a scalar"""
        assert (isinstance(other, float))
        return self.scaled(other)

    def length_squared(self):
        """
			compute the length of self squared
			
			C++: this method returns a number of type T
		"""
        return self * self

    def length(self):
        """ compute the length of self """
        return self.length_squared() ** 0.5

    def cos_angle(self, other):
        """ compute the angle between self and other """
        return self * other / (self.length() * other.length())

    def scaled(self, s):
        """ return a scaled version of the current vector """
        return Vector(s * self.x, s * self.y)

    def left(self):
        """
		    find the vector of the same length which goes to the left
		    
		    assume the standard coordinate system (x to the right, y up)
		    
		    left of (1,0) [x-axis] is (0,1) [y-axis]
		    left of (0,1) [y-axis] is (-1,0) [-x-axis]
		"""
        return Vector(-self.y, self.x)

    def right(self):
        """
		    find the vector of the same length which goes to the right
		    
		    assume the standard coordinate system (x to the right, y up)
		    
		    right of (1,0) [x-axis] is (0,-1) [-y-axis]
		    right of (0,1) [y-axis] is (1,0) [x-axis]
		"""
        return Vector(self.y, -self.x)

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self):
        """ Generate a string representation of the current object. """
        return "%s(%s,%s)" % (self.__class__.__name__, self.x, self.y)

    def __repr__(self):
        """ Generate a string representation of the current object. """
        return "%s(%r,%r)" % (self.__class__.__name__, self.x, self.y)


class PointTemplate(Vector):
    """
		Represents a point.
		
		C++: derives from Vector<T>, still has an open type
	"""
    pass


class GridPoint(PointTemplate):
    """
		Represents a point on the grid.
		
		C++: derives from PointTemplate<int>
	"""

    def adjacent_tiles(self):
        """
			compute the tiles which are adjacent to this point
		"""
        # these are the points with x/y coordinate which is -0 or -1
        return [
            GridTile(self.x - dx, self.y - dy)
            for dx, dy in ((0, 0), (0, 1), (1, 1), (1, 0))
        ]

    def adjacent_points(self):
        """ all nearby points (including the diagonal) """
        return [
            GridPoint(self.x + dx, self.y + dy)
            for dx, dy in ((1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1))
        ]

    def directly_adjacent_points(self):
        """ all nearby points (excluding the diagonal) """
        return [
            GridPoint(self.x + dx, self.y + dy)
            for dx, dy in ((1, 0), (0, -1), (-1, 0), (0, 1))
        ]

    def toPointF(self):
        return PointF(float(self.x), float(self.y))


class PointF(PointTemplate):
    """
		Represents a point.
		
		C++: derives from PointTemplate<float>
	"""
    pass


class GridTile(Vector):
    """
		Represents a tile on the grid.
		
		C++: derives from Vector<int>
	"""

    def adjacent_points(self):
        """ compute the points which are adjacent to the tile """
        # these are the points with x/y coordinate which is +0 or +1
        return [
            GridPoint(self.x + dx, self.y + dy)
            for dx, dy in ((0, 0), (0, 1), (1, 1), (1, 0))
        ]

    def adjacent_tiles(self):
        """ all nearby tiles (including the diagonal) """
        return [
            GridTile(self.x + dx, self.y + dy)
            for dx, dy in ((1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1))
        ]

    def polygon(self):
        """ get the polygon of the tile """
        return Polygon(self.adjacent_points())

    def edge_between(self, t):
        """
			Create the edge between self and t.
			We assume that self and t are direct neighbours.
			The direction should be given such that edge.right_tile() == self.
			
			Examples:
			GridTile(0,0).edge_between(GridTile(1,0))
			-> GridEdge(GridPoint(1,1),GridPoint(1,0))
			GridTile(0,0).edge_between(GridTile(0,1))
			-> GridEdge(GridPoint(0,1),GridPoint(1,1))
			GridTile(0,0).edge_between(GridTile(-1,0))
			-> GridEdge(GridPoint(0,0),GridPoint(0,1))
			GridTile(0,0).edge_between(GridTile(0,-1))
			-> GridEdge(GridPoint(1,0),GridPoint(0,0))
		"""
        # get the direction vector
        v = t - self

        # question: how does the closed formula look like?
        x, y = self.x, self.y
        if v.x == 1:
            p1, p2 = GridPoint(x + 1, y + 1), GridPoint(x + 1, y + 0)
        elif v.y == 1:
            p1, p2 = GridPoint(x + 0, y + 1), GridPoint(x + 1, y + 1)
        elif v.x == -1:
            p1, p2 = GridPoint(x + 0, y + 0), GridPoint(x + 0, y + 1)
        elif v.y == -1:
            p1, p2 = GridPoint(x + 1, y + 0), GridPoint(x + 0, y + 0)
        else:
            raise ValueError()

        # create edge
        edge = GridEdge(p1, p2)
        assert (edge.right_tile() == self)
        return edge


class GridLine:
    """
		Represents the line between a and b.
	"""

    def __init__(self, a, b):
        assert (isinstance(a, GridPoint))
        assert (isinstance(b, GridPoint))
        self.a = a
        self.b = b

    def direction(self):
        """ return the direction in which the line is showing, i.e. b - a """
        return self.b - self.a

    def __str__(self):
        """ Generate a string representation of the current object. """
        return "%s(%s,%s)" % (self.__class__.__name__, self.a, self.b)

    def __repr__(self):
        """ Generate a string representation of the current object. """
        return "%s(%r,%r)" % (self.__class__.__name__, self.a, self.b)


def grid_line_equality(l1, l2):
    """ check if two lines are equal """
    return ((l1.a, l1.b) == (l2.a, l2.b)) or ((l1.a, l1.b) == (l2.b, l2.a))


class GridEdge(GridLine):
    """
		Represents the edge between a and b.
		
		For this |b - a| has to be 1, otherwise this is not a grid edge.
	"""

    def __init__(self, a, b):
        assert ((b - a).length() == 1)
        super(GridEdge, self).__init__(a, b)

    def left_tile(self):
        """
			get the tile to the left of the grid edge a->b
			
			examples:
				edge = GridEdge( GridPoint(0,0), GridPoint(1,0) )
				edge.left_tile() -> GridTile(0,0)
				edge = GridEdge( GridPoint(0,0), GridPoint(0,1) )
				edge.left_tile() -> GridTile(-1,0)
				edge = GridEdge( GridPoint(0,0), GridPoint(-1,0) )
				edge.left_tile() -> GridTile(-1,-1)
				edge = GridEdge( GridPoint(0,0), GridPoint(0,-1) )
				edge.left_tile() -> GridTile(0,-1)
		"""
        a, b = self.a, self.b

        # compute the direction of the left tile as seen from the edge
        v_left = (b - a).left()

        # the base point is min(p0,p1), then subtract 1 of the coordinate
        # only if we go back one step in this direction
        tile_x = min(a.x, b.x) + (-1 if v_left.x == -1 else 0)
        tile_y = min(a.y, b.y) + (-1 if v_left.y == -1 else 0)

        return GridTile(tile_x, tile_y)

    def right_tile(self):
        """
			get the tile to the right of the grid edge a->b
			
			examples:
				edge = GridEdge( GridPoint(0,0), GridPoint(1,0) )
				edge.right_tile() -> GridTile(0,-1)
				edge = GridEdge( GridPoint(0,0), GridPoint(0,1) )
				edge.right_tile() -> GridTile(0,0)
				edge = GridEdge( GridPoint(0,0), GridPoint(-1,0) )
				edge.right_tile() -> GridTile(-1,0)
				edge = GridEdge( GridPoint(0,0), GridPoint(0,-1) )
				edge.right_tile() -> GridTile(-1,-1)
		"""
        a, b = self.a, self.b

        # compute the direction of the right tile as seen from the edge
        v_right = (b - a).right()

        # the base point is min(p0,p1), then subtract 1 of the coordinate
        # only if we go back one step in this direction
        tile_x = min(a.x, b.x) + (-1 if v_right.x == -1 else 0)
        tile_y = min(a.y, b.y) + (-1 if v_right.y == -1 else 0)

        return GridTile(tile_x, tile_y)


class PathTemplate:
    """
		Represents a path.
		
		C++: template class with variable type T, i.e still has open
		     (for the PointTemplate type)
	"""

    def __init__(self, points=None):
        # points is a list of points
        self.points = points if points else []

    def node_count(self):
        """ length of the points """
        return len(self.points)

    def empty(self):
        """ is the points list empty? """
        return self.node_count() == 0

    def start(self):
        """ get the start point of the points """
        return self.points[0]

    def end(self):
        """ get the end point of the points """
        return self.points[-1]

    def has_point(self, point):
        """ does the path contain the point? """
        return point in self.points

    def pop_first(self):
        """ remove the first element of the points and return it """
        return self.points.pop(0)

    def append(self, p):
        """ append p to the end """
        return self.points.append(p)

    def prepend(self, p):
        """ prepend p to the start """
        return self.points.insert(0, p)

    def get_path_extended_by(self, p):
        """ create a new list with the point added to the end """
        return self.__class__(self.points + [p])

    def reversed(self):
        """ returns a copy of the path which is reversed """
        return self.__class__(list(reversed(self.points)))

    def length(self):
        """ returns the length of the path """
        return sum(
            (self.points[i + 1] - self.points[i]).length()
            for i in range(self.node_count() - 1)
        )

    def __eq__(self, other):
        """ equality of paths means equality of points """
        return tuple(self.points) == tuple(other.points)

    def directionless_compare(self, other):
        """ compare the paths but disregard the direction """
        return self == other or self.reversed() == other

    def __hash__(self, other):
        """ just use the the tuple hash function """
        return hash(tuple(self.points))

    def __str__(self):
        """ Generate a string representation of the current object. """
        points = " -> ".join("%s|%s" % (p.x, p.y) for p in self.points)
        return "%s(%s)" % (self.__class__.__name__, points)

    def __repr__(self):
        """ Generate a string representation of the current object. """
        return "%s(%r)" % (self.__class__.__name__, self.points)


class GridPath(PathTemplate):
    """
		Represents a path on the grid.
		
		C++: derives from PathTemplate<GridPoint>
	"""

    def toPathF(self):
        return PathF([p.toPointF() for p in self.points])


class PathF(PathTemplate):
    """
		Represents a path in the plane.
		
		C++: derives from PathTemplate<Point>
	"""
    pass


class Polygon(PathF):
    """
		Represents a polygon in the plane.
	"""
    pass
