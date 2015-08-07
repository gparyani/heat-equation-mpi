from mpi4py import MPI

import pygame
import numpy
import time
import socket

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
		
class NullEquation(Equation):
	def getCurrentValue(self, param1, param2):
		return 100
		
	def updateAfterDeltaT(self, deltaT):
		pass
				
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
	def __init__(self, nx, ny, diffusionConstant, initialMatrix = None):
		self.nx = nx
		self.ny = ny
		self.a = diffusionConstant
		self.dx = 1/float(nx)
		self.dy = 1/float(ny)
		self.dx2 = self.dx * self.dx
		self.dy2 = self.dy * self.dy
		self.dt = self.dx2 * self.dy2 / (2 * self.a * (self.dx2 + self.dy2))	#time interval
		if initialMatrix == None:
			self.matrix = numpy.zeros([nx, ny])
			self.matrixPrime = numpy.zeros([nx, ny])
			for r in range(25, 50):
				self.matrix[25][r] = 200
				self.matrix[50][r] = 200
			for s in range(26, 50):
				self.matrix[s][25] = 200
				self.matrix[s][49] = 200
		else:
			self.matrix = numpy.copy(initialMatrix)
		
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
	def __init__(self, anEquation, screenWidth, screenHeight, columns, rows, surface = None):
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
	
	def displayAndUpdate(self):
		pygame.display.flip()	#display what's in temporary buffer
		self.equation.updateAfterDeltaT(1)
		
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
if rank == 0:	#Master node
	connected = 0
	readyToFlip = 0
	print "Master: Waiting for others to join"
	while connected < 15:
		connectedValue = comm.recv(source=MPI.ANY_SOURCE)
	 	if connectedValue == "Join network":
	 		print "Received one connection"
	 	 	connected = connected + 1
	print "Ready"
	initialCondition = numpy.zeros([500, 300])
	for r in range(50, 250):
		initialCondition[50][r] = 200
		initialCondition[450][r] = 200
	for s in range(51, 450):
		initialCondition[s][59] = 200
		initialCondition[s][249] = 200
	for t in range(150, 350):
		initialCondition[t][150] = 200
	comm.bcast(obj=["HeatEquation", 500, 300, initialCondition])
	
	while True:
		while readytoFlip < 15:
			if comm.recv(source=MPI.ANY_SOURCE) == "Ready to flip":
				readyToFlip = readyToFlip + 1
		comm.bcast(obj="Flip!")
		readyToFlip = 0
			
	
else:	#Client code
	comm.send(obj="Join network", dest=0)
	data = comm.recv(source=0)
	print data
	
	#obtain x- and y-coordinates from network name
	hostname = socket.gethostname()
	xandy = hostname[5:]
	x = int(xandy[:1])
	y = int(xandy[-1:])
	
	equationName = data[0]
	totalX = data[1]
	totalY = data[2]
	initial = data[3]
	xPerScreen = totalX // 5
	yPerScreen = totalY // 3
	matrix = numpy.zeros([xPerScreen, yPerScreen])
	for i in range(xPerScreen):
		for j in range(yPerScreen):
			matrix[i][j] = initial[x * xPerScreen + i][y * yPerScreen + j]
	
	equation = None
	if equationName == "HeatEquation":
		equation = HeatEquation(xPerScreen, yPerScreen, 0.5, matrix)
	elif equationName == "CheckerboardEquation":
		equation = CheckerboardEquation()
	elif equationName == "SquareEquation":
		equation = SquareEquation()
	else:	#check for invalid values and fall back to prevent null pointer error
		equation = NullEquation()
		
	renderer = EquationRenderer(equation, 1920, 1200, xPerScreen, yPerScreen)
	while True:
		renderer.renderEquation()
		flippedState = comm.sendrecv(sendobj = "Ready to flip", dest = 0, source = 0)
		if flippedState == "Flip!":
			renderer.displayAndUpdate()
