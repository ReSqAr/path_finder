# -*- coding: utf-8 -*-
import sys
if sys.version_info < (3,2,0):
        raise RuntimeError("Python version >= 3.2 is needed.")

import math

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import uic


#import path_finding_algo

import pf_raw_map
import pf_preprocess

class MainWindow(QtGui.QMainWindow):
	def __init__(self, app, map_path):
		super(QtGui.QMainWindow,self).__init__()
		
		self.raw_map_path = map_path
		self.raw_map = pf_raw_map.RawMap.read(self.raw_map_path)
		
		self.preprocessed =\
			pf_preprocess.PreprocessedPathFindingData(self.raw_map, lambda x: x == 255) # default 255

		# init gui
		self.initUI()
		
		# draw the map
		colors = [QtCore.Qt.red, QtCore.Qt.green, QtCore.Qt.blue,
					QtCore.Qt.yellow, QtCore.Qt.gray, QtCore.Qt.cyan,
					QtCore.Qt.magenta, QtCore.Qt.blue, QtCore.Qt.black,
					QtCore.Qt.darkRed, QtCore.Qt.darkGreen, QtCore.Qt.darkBlue,
					QtCore.Qt.darkYellow, QtCore.Qt.darkGray, QtCore.Qt.darkCyan,
					QtCore.Qt.darkMagenta, QtCore.Qt.darkBlue]
					
		self.draw_bounding_box()

		self.draw_area_map(colors)
		#self.draw_boundary_edges("orange")
		
		#self.draw_influence_boundaries()
		#self.draw_influence_map(colors)
		
		self.draw_graph(draw_gates=True,
		                   draw_path=True,
		                   draw_opt_path=True,
		                   draw_opt_gate_path=True)
		
		# maximise
		self.showMaximized()
	
	def initUI(self):
		#
		# load
		# source: http://bitesofcode.blogspot.co.uk/2011/10/comparison-of-loading-techniques.html
		uic.loadUi('ui/main.ui', self)

		# connect signals
		self.graphicsView = self.findChild(QtGui.QGraphicsView,"graphicsView")
		self.scene = QtGui.QGraphicsScene()
		self.graphicsView.setScene(self.scene)

		#self.tabs.tabCloseRequested.connect(self.tabs.removeTab)

	# convience method
	def draw_path(self, path, pen, draw_nodes=False):
		
		for p1,p0 in zip(path.points[1:],path.points[:-1]):
			self.scene.addLine(p0.x*10,
								p0.y*10,
								p1.x*10,
								p1.y*10,
								pen)

		if draw_nodes:
			for p in path.points:
				self.scene.addRect(p.x*10-2, p.y*10-2, 4, 4,
									QtGui.QPen(),
									QtGui.QBrush("blue"))
		
	
	
	def draw_bounding_box(self):
		"""
			draw the bounding box
		"""
		self.scene.addRect(0, 0, self.raw_map.width*10, self.raw_map.height*10,
							QtGui.QPen(),
							QtGui.QBrush())
	
	def draw_area_map(self, colors):
		"""
			draw the area map
		"""
		print("Drawing area map...")

		for t in self.raw_map.tiles_iterator():
			z = self.preprocessed.area_map[t]
			if z != -1:
				self.scene.addRect(t.x*10, t.y*10, 10, 10,
									QtGui.QPen(),
									QtGui.QBrush(colors[z % len(colors)]))

	def draw_boundary_edges(self, color):
		"""
			draw the found edges on the map
		"""
		pen = QtGui.QPen()
		pen.setWidth(3)
		pen.setColor(QtGui.QColor(color))

		for area_edges in self.preprocessed.area_map.edges.values():
			for edge in area_edges:
				self.scene.addLine(edge.a.x*10,edge.a.y*10,edge.b.x*10,edge.b.y*10,pen)

	def draw_influence_boundaries(self):
		"""
			draw the influence boundaries on the map
		"""
		i = 0
		
		for area_id,loops in self.preprocessed.influence_map.boundaries.items():
			for loop_id,loop in enumerate(loops):
				pen = QtGui.QPen()
				pen.setWidth(3)
				color = QtGui.QColor()
				color.setBlueF(1-(i%4)/4.)
				color.setRedF(1-(i%3)/3.)
				color.setGreenF((i%5)/5.)
				pen.setColor(color)
				i += 1
				
				for edge in loop:
					v_straight = edge.direction()
					v_right = v_straight.right()
					
					if v_straight.length_squared() != 1:
						print("WARNING!!!")
					
					self.scene.addLine(edge.a.x*10 + 2*v_right.x,
										edge.a.y*10 + 2*v_right.y,
										edge.b.x*10 + 2*v_right.x,
										edge.b.y*10 + 2*v_right.y,
										pen)

	def draw_graph(self, draw_gates=True,
	                     draw_path=True,
	                     draw_opt_path=True,
	                     draw_opt_gate_path=True):
		"""
			draw the graph
		"""
		pen = QtGui.QPen()
		pen.setWidth(4)
		pen.setColor(QtGui.QColor("orange"))
		gate_pen = QtGui.QPen()
		gate_pen.setWidth(3)
		gate_pen.setColor(QtGui.QColor("green"))
		opt_pen = QtGui.QPen()
		opt_pen.setWidth(2)
		opt_pen.setColor(QtGui.QColor("orchid"))
		opt_gate_pen = QtGui.QPen()
		opt_gate_pen.setWidth(1)
		opt_gate_pen.setColor(QtGui.QColor("red"))

		for node in self.preprocessed.graph.nodes:
			#print(node)
			#for edge in node.edges:
			#	print("->", edge.nodes() - {node})
			x,y = node.position.x,node.position.y
			self.scene.addEllipse(x*10-4,y*10-4,8,8,
			                      QtGui.QPen(),
			                      QtGui.QBrush(QtCore.Qt.red))
		
		for edge in self.preprocessed.graph.edges:
			if draw_path:
				self.draw_path( edge._path, pen )
			
			if draw_gates:
				gates = [(edge.node_a,g) for g in edge._node_a_gates] + [(edge.node_b,g) for g in edge._node_b_gates]
				for node,gate in gates:
					self.scene.addEllipse(gate.x*10-4,gate.y*10-4,8,8,
										QtGui.QPen(),
										QtGui.QBrush(QtCore.Qt.magenta))

					self.scene.addLine(node.position.x*10,
										node.position.y*10,
										gate.x*10,
										gate.y*10,
										gate_pen)
		

			if edge._opt_path and draw_opt_path:
				self.draw_path( edge._opt_path, opt_pen, draw_nodes=True )

			if edge._opt_gate_path and draw_opt_gate_path:
				self.draw_path( edge._opt_gate_path, opt_gate_pen, draw_nodes=True )

	def resizeEvent(self, *args, **kwargs):
		self.graphicsView.fitInView(self.scene.itemsBoundingRect(), QtCore.Qt.KeepAspectRatio)
		
		super(QtGui.QMainWindow,self).resizeEvent(*args, **kwargs)
	
	def wheelEvent(self, event):
		self.graphicsView.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
 
		scaleFactor = 1.2
		if event.delta() > 0:
			self.graphicsView.scale(scaleFactor, scaleFactor)
		else:
			self.graphicsView.scale(1.0 / scaleFactor, 1.0 / scaleFactor)

def main(): 
	import argparse
	
	# create parser
	parser = argparse.ArgumentParser(prog='pgm2path')
	parser.add_argument("map_path")

	# parse arguments and call function
	args = parser.parse_args()
	map_path = args.map_path

	app = QtGui.QApplication(sys.argv)
	w = MainWindow(app, map_path)
	w.show()
	sys.exit(app.exec_())

if __name__ == "__main__": 
	main()
 
