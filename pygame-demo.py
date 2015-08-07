import pygame
import numpy
import time

class Equation(object):
	def doEquation(self, param1, param2, param3, param4):
		raise NotImplementedError("Please override this abstract class to implement your own equation class")
		
class CheckerboardEquation(Equation):
	def __init__(self):
		pass
	
	def doEquation(self, param1, param2, param3, param4):
		if (param1 + param2) % 2 == 0:
			result = 255 - param3
			if result < 0:
				return 0
			else:
				return result
		else:
			result = param3
			if result > 255:
				return 255
			else:
				return result
				
class SquareEquation(Equation):
	def doEquation(self, x, y, t, notUsed):
		value = int((x + y))
		if value > 255:
			return 255
		else:
			return value
				
class HeatEquation(Equation):
	def __init__(self, nx, ny, diffusionConstant):
		self.nx = nx
		self.ny = ny
		self.a = diffusionConstant
		self.dx = 1/float(nx)
		self.dy = 1/float(ny)
		self.dx2 = self.dx * self.dx
		self.dy2 = self.dy * self.dy
		self.iterations = nx * ny
		self.currentIteration = 0
		self.dt = self.dx2 * self.dy2 / (2 * self.a * (self.dx2 + self.dy2))	#time interval
		self.matrix = numpy.random.randint(0, 50, (self.nx, self.ny))	#generate some random data as an initial condition
		for p in range(nx):
			for q in range(ny):
				print q
				self.matrix[p][q] = 0
		for r in range(25, 50):
			self.matrix[25][r] = 200
			self.matrix[50][r] = 200
		for s in range(26, 49):
			self.matrix[r][25] = 200
			self.matrix[r][50] = 200
		
	def updateMatrix(self):
		self.updateCalled = True
		self.matrix = self.matrix[1:-1, 1:-1] + self.a * self.dt * ((self.matrix[2:,1:-1] - 2 * self.matrix[1:-1, 1:-1] + self.matrix[:-2, 1:-1]) / self.dx2 + (self.matrix[1:-1, 2:] - 2 * self.matrix[1:-1, 1:-1] + self.matrix[1:-1, :-2]) / self.dy2)
		
	def doEquation(self, x, y, t, notUsed):
		temp = self.matrix
		self.currentIteration = self.currentIteration + 1
		if self.currentIteration % self.iterations == self.iterations - 1:
			self.updateMatrix()
		try:
			return temp[x][y]
		except IndexError:
			return 0
		
class EquationRenderer(object):
	def __init__(self, anEquation, screenWidth, screenHeight, columns, rows, surface):
		if surface == None:
			surface = pygame.display.set_mode((screenWidth, screenHeight), pygame.FULLSCREEN)
		self.equation = anEquation
		self.screenWidth = screenWidth
		self.screenHeight = screenHeight
		self.columns = columns
		self.rows = rows
		self.surface = surface
		self.__calculateRectangleDimensions()
		self.initialTime = int(time.time())
		
	def __calculateRectangleDimensions(self):
		self.rectangleWidth = self.screenWidth // self.columns
		self.rectangleHeight = self.screenHeight // self.rows
		
	def renderEquation(self):
		x = 0
		while x < self.columns:
			y = 0
			while y < self.rows:
				value = int(40 * self.equation.doEquation(x, y, 4 * int(time.time() - self.initialTime), 0))
				if value > 255:
					value = 255
				rectangle = pygame.Rect(x * self.rectangleWidth, y * self.rectangleHeight, self.rectangleWidth, self.rectangleHeight)
				color = pygame.Color(value, value, value, 255)
				pygame.draw.rect(self.surface, color, rectangle)
				y = y + 1
			x = x + 1
		pygame.display.flip()	#display what's in temporary buffer
		
equation = HeatEquation(80, 60, 0.5)
renderer = EquationRenderer(equation, 1600, 1200, 80, 60, None)
i = 0
while i < 10:
	renderer.renderEquation()
#	time.sleep(0.5)
	i = i + 1
