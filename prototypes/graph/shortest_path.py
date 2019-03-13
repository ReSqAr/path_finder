import collections


class ShortestPathFinder:
    """
	title:
		full path dependant shortest path finder
		employing a path length estimator for partial paths
	
	given data:
		- graph with nodes and edges
		- valuation e which gives the length of a path
		  (=collection of edges) (e=exact,expensive)
		  with the following property: e(P) <= e(P + loop)
		- estimation c which gives the range in which the
		  length of a path lies and it fullfils a natural triangle
		  inequality: (let P,Q be paths, P+Q its concatenation)
		  c(P+Q) is a subset of c(P) + c(Q)
	
	objective:
		find the shortest path in the graph between a given
		start and end node
	
	challenge:
		the length of a path depends on the whole path, in particular:
		e does not have to obey the triangle inequality, it may
		even decrease for longer paths (however, if loops occur,
		the path with the loop cut away has to be shorter)
		furthermore, if only e was given, we had to try every possibility
	
	strategy:
		state:
		- maintain a list OpenPaths of all interesting paths which
		  we may want to extend
		- maintain a dictionary UpperBound which holds for every
		  node the upper bound to get there, i.e.
		    max_{known path P) max c(P)
		  (this is just an optimisation)
		- path P_opt with the minimal known distance e(P_best) to the
		  end node (if one is known)
		algorithm:
		1. extract the path P with the smallest min c(P) from OpenPaths
		2. if P_opt exists, it is the optimal path if c(P) > e(P_opt), so stop
		3. skip P if UpperBound[P.end] < min c(P), otherwise set
		   UpperBound[P.end] to max c(P) if it is smaller
		4. if P.end is end, compute e(P) and update P_opt if necessary,
		   skip to the next path
		5. otherwise extend it, but without loops; add the extended paths
		   to OpenPaths
		
	degeneration properties:
		- if c is constant [0,inf), then the algorithm degenerates to trying
		all possible paths. depending on the implementation it can be a
		breadth or depth search
		- if c comes from a weighted graph, i.e.
			c(P) = sum c(i-th edge in P)
		and the interval c(i-th edge in P) has length 0, then the algorithm
		degenerates to Dijkstra's algorithm
	
	expected object signatures:
		- nodes:
			- __eq__ and __hash__
		- edges:
			start() -> start node
			end() -> end node
		- get_edges(node) -> all edges from the given node
		- exact_eval(path) -> exact length
		- range_eval(path) -> tuple of min/max length
	"""

    def __init__(self, nodes, get_edges, exact_eval, range_eval):
        self._nodes = nodes
        self._get_edges = get_edges
        self._exact_eval = exact_eval
        self._range_eval = range_eval

    def find_path(self, start, end):

        # paths which have to be considered
        OpenPaths = []
        # map of node -> worst known distance to the node
        UpperBound = {}
        # optimal path
        P_opt = None
        P_opt_length = None

        # initialise OpenPaths:
        # iterate over the edges of the start node
        for edge in self._get_edges(start):
            # add everything except loops
            if edge.end() != start:
                OpenPaths.append(Path(None, edge))

        # initialise UpperBound:
        # we can get to start directly
        UpperBound[start] = 0.

        # keep statistics
        c_evals = collections.defaultdict(int)
        e_evals = collections.defaultdict(int)
        N_rejected = collections.defaultdict(int)

        while OpenPaths:
            # 1. extract the element with the smallest min c(P)
            P = min(OpenPaths, key=lambda P: self._range_eval(P)[0])
            OpenPaths.remove(P)

            # print("current", str(P))

            # 2. if P_opt exists, test the length
            # compute c(P)
            min_cP, max_cP = self._range_eval(P)
            c_evals[P.length] += 1
            # print("c(P):", min_cP,max_cP)

            # if all following paths are longer
            if P_opt is not None and min_cP > P_opt_length:
                # P_opt is the optimal path
                break

            # 3. a) skip P if UpperBound[P.end_node] < min c(P)
            if P.end_node() in UpperBound and UpperBound[P.end_node()] < min_cP:
                N_rejected[P.length] += 1
                continue

            # 3. b) update UpperBound[P.end_node] if > max c(P)
            if P.end_node() not in UpperBound or UpperBound[P.end_node()] > max_cP:
                UpperBound[P.end_node()] = max_cP
            # TODO: question: are there any guarantees like
            #       could a reordering prevent certain paths from propagation?

            # 4. if P.end_node is end, compute e(P) and update P_opt if necessary
            if P.end_node() == end:
                eP = self._exact_eval(P)
                e_evals[P.length] += 1
                if P_opt is None or eP < P_opt_length:
                    P_opt = P
                    P_opt_length = eP
                # skip to the next one
                continue

            # 5. otherwise extend it, but without loops; add the extended paths
            possible_edges = self._get_edges(P.end_node())

            # iterate over the edges
            for edge in possible_edges:
                new_node = edge.end()
                # skip if edge.end() is P.start()==start
                if new_node == start:
                    continue
                # if edge.end() appears somewhere in P, skip the edge
                for P_edge in P.edges():
                    if new_node == P_edge.end():
                        break
                else:
                    # otherwise add the extended path to OpenPaths
                    new_P = P.get_extended_by(edge)
                    OpenPaths.append(new_P)

        def f(dd):
            s = sum(dd.values())
            d = ",".join("%s:%s" % (k, v) for k, v in sorted(dd.items(), key=lambda kv: kv[0]))
            return "%s (%s)" % (s, d)

        print("c_evals:", f(c_evals),
              "e_evals:", f(e_evals),
              "N_rejected:", f(N_rejected))

        # if we end up here, we could not exit the algorithm early
        return P_opt


class Path:
    """
		represents a collection of edges
	"""

    def __init__(self, parent, edge):
        self._parent = parent  # can be None
        self._edge = edge
        self.length = parent.length + 1 if parent else 1

    def end_node(self):
        """ return the end node """
        return self._edge.end()

    def last_edge(self):
        """ find the last edge """
        return self._edge

    def get_extended_by(self, edge):
        """ get a path which es extended by the given edge """
        return Path(self, edge)

    def edges(self):
        """ get all edges """
        edges = []
        if self._parent:
            edges += self._parent.edges()
        edges.append(self._edge)
        return edges

    def nodes(self):
        """ get all nodes """
        edges = self.edges()
        return [edges[0].start()] + [edge.end() for edge in edges]

    def parent(self):
        """ get the parent path """
        return self._parent

    def __str__(self):
        return "Path: %s" % '->'.join("%s" % x for x in self.edges())
