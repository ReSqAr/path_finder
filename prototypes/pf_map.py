import pf_vector

class Map:
	def __init__(self, width, height, data):
		self.width = width
		self.height = height
		self.data = data

	def contains(self, obj):
		""" does the current map contain the point/tile? """
		if isinstance(obj, pf_vector.PointTemplate):
			return 0 <= obj.x <= self.width and 0 <= obj.y <= self.height
		elif isinstance(obj, pf_vector.GridTile):
			return 0 <= obj.x < self.width and 0 <= obj.y < self.height
		else:
			raise TypeError()

	def tiles_iterator(self):
		""" returns an iterator over all tiles """
		for x in range(self.width):
			for y in range(self.height):
				yield pf_vector.GridTile(x,y)

	def __getitem__(self, i):
		assert( isinstance(i, pf_vector.GridTile) )
		index = i.x + i.y*self.width
		return self.data[index]

	def __setitem__(self, i, v):
		assert( isinstance(i, pf_vector.GridTile) )
		index = i.x + i.y*self.width
		self.data[index] = v
	
	@staticmethod
	def read(path):
		""" read the map """
		# open source in binary read mode and open destination in binary write mode
		with open(path,"rb") as f:
			# read the first 3+x lines
			read_lines = 0
			while read_lines != 3:
				line = f.readline()
				
				# ignore comments
				if line.startswith(b'#'):
					continue
				
				# first line is the version
				if read_lines == 0:
					version = line.strip()
					assert(version == b"P5")
				# second line is width and height
				if read_lines == 1:
					width,height = line.strip().split(b" ")
					width,height = int(width),int(height)
				# third line is the max pixel value
				if read_lines == 2:
					max_value = line.strip()
				
				# increment read line counter
				read_lines += 1
			
			# after that, all is data
			data = f.read()
		
		assert( len(data) == width*height )
		
		# return interesting data
		return Map(width, height, data)
