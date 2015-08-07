import pygame
import numpy
import time

class Equation(object):
	def getCurrentValue(self, param1, param2):
		raise NotImplementedError("Please override this abstract class to implement your own equation class")
		
	def updateAfterDeltaT(self, deltaT):
		raise NotImplementedError("Please override this abstract class to implement your own equation class")
		
class CheckerboardEquation(Equation):
	def __init__(self):
		self.time = 0
	
	def getCurrentValue(self, param1, param2):
		if (param1 + param2) % 2 == 0:
			result = 255 - self.time
			if result < 0:
				return 0
			else:
				return result
		else:
			result = self.time
			if result > 255:
				return 255
			else:
				return result
	
	def updateAfterDeltaT(self, deltaT):
		self.time = self.time + 4 * deltaT
				
class SquareEquation(Equation):
	def getCurrentValue(self, x, y):
		value = int((x + y))
		if value > 255:
			return 255
		else:
			return value
			
	def updateAfterDeltaT(self, deltaT):
		pass
				
class HeatEquation(Equation):
	def __init__(self, nx, ny, diffusionConstant):
		self.nx = nx
		self.ny = ny
		self.a = diffusionConstant
		self.dx = 1/float(nx)
		self.dy = 1/float(ny)
		self.dx2 = self.dx * self.dx
		self.dy2 = self.dy * self.dy
		self.dt = self.dx2 * self.dy2 / (2 * self.a * (self.dx2 + self.dy2))	#time interval
		self.matrix = numpy.zeros([nx, ny])
		self.matrixPrime = numpy.zeros([nx, ny])
		for r in range(25, 50):
			self.matrix[25][r] = 200
			self.matrix[50][r] = 200
		for s in range(26, 50):
			self.matrix[s][25] = 200
			self.matrix[s][49] = 200
		
	def updateMatrix(self):
		self.updateCalled = True
		self.matrixPrime[1:-1, 1:-1] = self.matrix[1:-1, 1:-1] + self.a * self.dt * ((self.matrix[2:,1:-1] - 2 * self.matrix[1:-1, 1:-1] + self.matrix[:-2, 1:-1]) / self.dx2 + (self.matrix[1:-1, 2:] - 2 * self.matrix[1:-1, 1:-1] + self.matrix[1:-1, :-2]) / self.dy2)
		self.matrix = numpy.copy(self.matrixPrime)
		
	def getCurrentValue(self, x, y):
		try:
			return int(self.matrix[x][y])
		except IndexError:
			return 0
			
	def updateAfterDeltaT(self, deltaT):
		self.updateMatrix()
		
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
#				value = int(40 * self.equation.doEquation(x, y, 4 * int(time.time() - self.initialTime), 0))
				value = self.equation.getCurrentValue(x, y)
				if value > 255:
					value = 255
				if value < 0:
					value = 0
				rectangle = pygame.Rect(x * self.rectangleWidth, y * self.rectangleHeight, self.rectangleWidth, self.rectangleHeight)
				color = pygame.Color(value, value, value, 255)
				pygame.draw.rect(self.surface, color, rectangle)
				y = y + 1
			x = x + 1
		pygame.display.flip()	#display what's in temporary buffer
		self.equation.updateAfterDeltaT(1)
		
equation = HeatEquation(80, 60, 0.5)
renderer = EquationRenderer(equation, 1600, 1200, 80, 60, None)
i = 0
while i < 30:
	renderer.renderEquation()
#	time.sleep(5)
	i = i + 1
