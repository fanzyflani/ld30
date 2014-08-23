#!/usr/bin/env python2 --
import math, random, time

import pygame

pygame.init()

WIDTH = 320
HEIGHT = 200
SCALE = 3

FPS = 60.0
SPF = 1.0/FPS

# Set up display
pygame.display.set_caption("LD30")
screen_real = pygame.display.set_mode((WIDTH*SCALE, HEIGHT*SCALE), 0, 0)
screen = pygame.Surface((WIDTH, HEIGHT), 0, screen_real.get_bitsize())

def rgb(r, g, b):
	"""
	Turns an RGB tuple into a colour value.
	"""

	return screen.map_rgb((r, g, b))

def flip_screen():
	"""
	Push the back buffer to the front buffer.
	That is, actually draw what you were drawing to the screen.
	"""

	pygame.transform.scale(screen,
		(screen_real.get_width(), screen_real.get_height()),
		screen_real)
	pygame.display.flip()

class BaseCell:
	color = rgb(255, 0, 255)
	solid = True

	def draw(self, surf, x, y):
		"""
		Draws the cell to the surface "surf".
		"""
		pygame.draw.rect(surf, self.color, (x, y, 16, 16))

	def is_solid(self, world=None):
		"""
		Determines if this cell is solid or not.
		"""
		return self.solid

class BaseEnt:
	color = rgb(255, 0, 255)
	rect = (4, 4, 8, 8)
	world = 0

	def __init__(self, lvl, cx, cy):
		"""
		Places an entity on level "lvl" at cell cx, cy.
		"""
		self.lvl = lvl
		self.cx, self.cy = cx, cy
		self.ox, self.oy =  0,  0

	def draw(self, surf, x, y):
		"""
		Draws the entity at pixel position x, y.
		"""
		rx, ry, rw, rh = self.rect
		rx += x + self.cx*16 + self.ox
		ry += y + self.cy*16 + self.oy
		pygame.draw.rect(surf, self.color, (rx, ry, rw, rh))

	def tick(self):
		"""
		Logic update for entity.
		"""

		# To be overrided by subclasses.
		pass

class PlayerEnt(BaseEnt):
	color = rgb(0, 255, 0)

	# TODO: Move this function to a better spot eventually
	def cell_is_walkable(self, cx, cy, world=None):
		"""
		Determine if we can walk onto a given cell.
		"""

		# Get the relevant "world" we're checking this for
		if world == None:
			world = self.world

		# Get cell
		cell = self.lvl.get_cell(cx, cy)

		# Check if None
		if cell == None:
			return False # NEVER WALKABLE!

		# Check if solid
		return not cell.is_solid(world=world)

	def tick(self):
		# Move to relevant cell if need be
		if self.ox != 0:
			self.ox += (1 if self.ox < 0 else -1)
		if self.oy != 0:
			self.oy += (1 if self.oy < 0 else -1)

		if self.ox == 0 and self.oy == 0:
			# Work out movement
			vx, vy = 0, 0
			if newkeys[pygame.K_LEFT]:
				vx -= 1
			if newkeys[pygame.K_RIGHT]:
				vx += 1
			if newkeys[pygame.K_UP]:
				vy -= 1
			if newkeys[pygame.K_DOWN]:
				vy += 1

			# Work out if anything is in that cell
			if self.cell_is_walkable(self.cx + vx, self.cy + vy):
				self.cx += vx
				self.cy += vy
				self.ox -= 16*vx
				self.oy -= 16*vy
			elif self.cell_is_walkable(self.cx + vx, self.cy):
				self.cx += vx
				self.ox -= 16*vx
			elif self.cell_is_walkable(self.cx, self.cy + vy):
				self.cy += vy
				self.oy -= 16*vy

class FloorCell(BaseCell):
	color = rgb(170, 100, 85)
	solid = False

class WallCell(BaseCell):
	color = rgb(55, 55, 55)
	solid = True

class Level:
	"""
	A Level contains all the logic and stuff for a, well, level.
	"""
	def __init__(self, data):
		# Allocate entity list
		self.ents = []

		# Allocate grid
		self.g = [[None for x in xrange(len(data[0]))]
			for y in xrange(len(data))]

		# Put stuff into grid
		for l, y in zip(data, xrange(len(data))):
			for c, x in zip(l, xrange(len(l))):
				self.g[y][x] = self.translate_level_char(c, x, y)

	def get_cell(self, x, y):
		"""
		Gets a cell from the level for inspection or mutilation.
		"""
		if y < 0 or y >= len(self.g): return None
		if x < 0 or x >= len(self.g[y]): return None
		return self.g[y][x]

	def tick(self):
		"""
		Logic update for level.
		"""
		# Update entities
		for ent in self.ents:
			ent.tick()
		pass

	def draw(self, surf, camx, camy):
		"""
		Draws the level at (-camx, -camy) on surface "surf".
		"""

		# Draw cells
		for y in xrange(len(self.g)):
			for x in xrange(len(self.g[0])):
				cell = self.g[y][x]
				if cell != None:
					cell.draw(surf, x*16-camx, y*16-camy)

		# Draw entities
		for ent in self.ents:
			ent.draw(surf, -camx, -camy)

	def translate_level_char(self, c, x, y):
		"""
		Maps a character from the source level to an actual class.
		"""

		if c == ".":
			return None

		elif c == ",":
			return FloorCell()

		elif c == "#":
			return WallCell()

		elif c == "P":
			self.ents.append(PlayerEnt(self, x, y))
			return FloorCell()

		else:
			raise Exception("invalid level char: %s" % repr(c))

# Create test level
lvl = Level(
"""
................
................
.....#####......
..####,,,####...
..#P,#,,,#,,#...
..#,,,,,,,,,#...
..#,,,###,,,#...
..#,,#,,,#,,#...
..####,,,####...
......###.......
................
................
""".split("\n")[1:-1]
)

# Main loop
quitflag = False
oldkeys = pygame.key.get_pressed()
newkeys = pygame.key.get_pressed()
tick_next = time.time()
while not quitflag:
	# Handle timing
	tick_current = time.time()

	if tick_current < tick_next:
		# Draw screen
		screen.fill(rgb(0,0,170))
		lvl.draw(screen, 0, 0)
		flip_screen()

		# Prevent CPU fires
		time.sleep(0.01)

	else:
		# Poll events
		pygame.event.pump()
		newkeys = pygame.key.get_pressed()
		if oldkeys[pygame.K_ESCAPE] and not newkeys[pygame.K_ESCAPE]:
			quitflag = True

		# Update logic
		lvl.tick()

		# Transfer newkeys to oldkeys
		oldkeys = newkeys

		# Update tick counter
		tick_next += SPF


# Clean up
pygame.quit()

