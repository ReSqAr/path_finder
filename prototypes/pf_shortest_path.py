import pf_vector
import pf_graph
import pf_graph_shortest_path


class ShortestPathSearch:
    def __init__(self, graph, area_map, n):
        self.graph = graph
        self.area_map = area_map
        self.n = n

        # create finder
        self._create()

    def _create(self):
        """ create shortest path finder """

        # TODO: optimisations:
        # - do not follow to connectivity nodes (i.e. nodes which have exactly
        #   one edge to a non-connectivity node. (this definition is unstable,
        #   (as order dependent) but in this context OK

        self._n_hop_dict = NHopDictionary(self.graph, self.area_map, self.n)

        def get_edges(node):
            return node.directional_edges()

        def exact_eval(path):
            path = sum([edge.opt_path().points for edge in path.edges()], [])
            path = pf_vector.PathF(path)
            opt = self.area_map.optimise_path(path)
            return opt.length()

        def range_eval(path):
            # c = len(path.edges())

            c_min = 0
            c_max = float("inf")

            current = path
            edges = []

            # compute a min/max length estimate
            for i in range(1, self.n + 1):
                # find the min/max lengths from node edge[-i].start() to edge[-1].end()
                # (we have: current.last_edge() == edge[-i]
                edges.append(current.last_edge())
                assert (len(edges) == i)
                # find the estimated min/max length for the path
                sub_min, sub_max = self._n_hop_dict.length_estimation(edges)

                parent = current.parent()

                # find the estimated length of the parent path
                if parent is None:
                    c_min_parent = 0
                    c_max_parent = 0
                else:
                    c_min_parent = parent.c_min
                    c_max_parent = parent.c_max

                # update c_m??_cur if we current subdivision gives
                # a better estimate
                c_min = max(c_min, sub_min + c_min_parent)
                c_max = min(c_max, sub_max + c_max_parent)

                # advance if possible
                if parent:
                    current = parent
                else:
                    break

            # set c_min/c_max
            path.c_min = c_min
            path.c_max = c_max
            return (c_min, c_max)

        self.finder = pf_graph_shortest_path.ShortestPathFinder(
            self.graph.nodes,
            get_edges,
            exact_eval,
            range_eval)

    def find_path_between_nodes(self, start, end):
        """ find the best path between the two points """
        assert (isinstance(start, pf_graph.GraphNode))
        assert (isinstance(end, pf_graph.GraphNode))

        # find the shortest path
        path = self.finder.find_path(start, end)

        # convert it to PathF and maximise (not very optimised version)
        opt_path = sum([edge.opt_path().points for edge in path.edges()], [])
        opt_path = pf_vector.PathF(opt_path)
        opt_path = self.area_map.optimise_path(opt_path)

        # and return it
        return opt_path

    def find_path(self, start, end):
        """ find the best path between the two points """
        assert (isinstance(start, pf_vector.PointF))
        assert (isinstance(end, pf_vector.PointF))

        raise NotImplementedError


class NHopDictionary:
    """
		find all optimal distances/ optimal gate distances
		of nodes which are max n hops apart
	"""

    def __init__(self, graph, area_map, n):
        self.graph = graph
        self.area_map = area_map
        self.n = n
        # saves the min/max length of the path
        self._map_length = {}
        # saves the opt_path for the path
        self._map_opt_path = {}

        # build it
        self._build()

    def create_key(self, edges):
        """
			create and canonicalise key,
			the key is the tuple of the edge ids
			and the lower end starts direction
		"""
        for edge in edges:
            assert (isinstance(edge, pf_graph.DirectionalGraphEdge))
        key = tuple(edge._graph_edge.edge_id(self.graph) for edge in edges)
        return key if key[0] <= key[-1] else tuple(reversed(key))

    def optimal_path(self, edges):
        """ find the optimal path """
        key = self.create_key(edges)
        opt_path = self._map_opt_path[key]

        start = edges[0].start().position.toPointF()

        # make sure that we return the path in the correct direction
        if start == opt_path.points[0]:
            return opt_path
        elif start == opt_path.points[-1]:
            return opt_path.reversed()
        else:
            raise RuntimeError("Floating point or programming issue: %s != %s,%s" \
                               % (start, opt_path.points[0], opt_path.points[-1])
                               )

    def length_estimation(self, edges):
        """ get a length estimation """
        key = self.create_key(edges)
        return self._map_length[key]

    def _build_helper(self, edges):
        """ helper method: expand nodes """

        # if the nodes list is already too long, ignore it
        if len(edges) > self.n:
            return

        # get the old optimal path
        if len(edges) != 1:
            old_opt_path = self.optimal_path(edges[:-1])
        else:
            old_opt_path = pf_vector.PathF([])

        # create the key under which we can find the data
        key = self.create_key(edges)

        # if this key was already visited, do not skip it, just don't compute anything
        if key not in self._map_opt_path:
            # create an extended path along the new node
            not_opt_path = old_opt_path.points + edges[-1].opt_path().points
            not_opt_path = pf_vector.PathF(not_opt_path)
            # find optimal path
            if len(edges) > 1:
                opt_path = self.area_map.optimise_path(not_opt_path)
            else:
                opt_path = not_opt_path
            # find optimal gate path
            opt_gate_path = self._opt_gate_path(
                edges[0].start().position,
                edges[0].start_gates(),
                edges[-1].end().position,
                edges[-1].end_gates(),
                opt_path)
            # save the optimal path and min/max
            self._map_opt_path[key] = opt_path
            self._map_length[key] = (opt_gate_path.length(), opt_path.length())

        # iterate over all edges
        for edge in edges[-1].end().directional_edges():
            # do not allow loops
            if edge.end() == edges[0].start() or edge.end() in [e.end() for e in edges]:
                continue

            # now we have an edge with which we can extend our list
            new_edges = edges + [edge]

            # add it
            self._build_helper(new_edges)

    def _build(self):
        for node in self.graph.nodes:
            for edge in node.directional_edges():
                self._build_helper([edge])
        print("added %d keys" % len(self._map_opt_path))

    def _opt_gate_path(self, node_a_pos, node_a_gates, node_b_pos, node_b_gates, path):
        """
			compute the gate distance between node_a and node_b
			with the initial path path
		"""

        # if node a or b does not have a gate, add a virtual gate
        if not node_a_gates:
            node_a_gates.append(node_a_pos)
        if not node_b_gates:
            node_b_gates.append(node_b_pos)

        # iterate over all possible gates
        gate_paths = []
        for gate_a in node_a_gates:
            for gate_b in node_b_gates:
                # hence we consider the gate a->gate_a and b->gate_b
                opt = self.area_map.optimise_path_loose_ends(
                    path,
                    node_a_pos.toPointF(),
                    gate_a.toPointF(),
                    node_b_pos.toPointF(),
                    gate_b.toPointF()
                )
                gate_paths.append(opt)

        # take the smallest one
        return min(gate_paths, key=lambda p: p.length())
