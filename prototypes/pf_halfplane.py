import sys

import pf_vector


class HalfPlane:
    """
		This object represents a half plane.
	"""

    def __init__(self, x0, normal):
        """
			x0 is the base point (type: PointF) and the normal
			(type: VectorF = Vector<float>) defines the inner area
			of the half plane, i.e. (x - x0) * normal \geq 0
		"""
        self.x0 = x0
        self.normal = normal
        self.x0_times_normal = self.x0 * self.normal

    def contains(self, x):
        """ does the half plane contain the point x? """
        scalar_product = x * self.normal - self.x0_times_normal
        return scalar_product >= 0

    def find_t(self, a, b):
        """
			solve
				t*(b-a) + a \in boundary of halfplane,
			i.e.
				(t*(b-a) + a - x0) * normal = 0
		"""
        x0, n = self.x0, self.normal

        # compute all important vectors/scalars
        v, c = b - a, a - x0
        v_times_normal = v * n
        c_times_normal = c * n

        if v_times_normal == 0.:
            # parallel, either 0 if all points are in there or
            # sys.float_info.min, if none are in the halfplane
            return 0. if c_times_normal == 0 else sys.float_info.min
        else:
            return -c_times_normal / v_times_normal

    def intersection(self, polygon):
        """
			intersects a convex polygon with a halfplane
		"""

        # save the result for the halfplane_test for every point
        halfplane_status = [self.contains(p) for p in polygon.points]

        # create intersection polygon
        intersection_polygon = pf_vector.Polygon()

        for i in range(polygon.node_count()):
            if halfplane_status[i]:
                # add to the polygon if it is contained in the halfplane
                intersection_polygon.append(polygon.points[i])

            # if the edge to the next point intersects the halfplane boundary,
            # i.e. add the intersection point to the polygon
            ipp = (i + 1) % polygon.node_count()
            if halfplane_status[i] != halfplane_status[ipp]:
                # find the next best point on this edge which is in the intersection
                p_ipp, p_i = polygon.points[ipp], polygon.points[i]
                t = self.find_t(p_i, p_ipp)
                if 0 < t < 1:
                    # found something
                    x = (p_ipp - p_i).scaled(t) + p_i
                    intersection_polygon.append(x)

        return intersection_polygon
