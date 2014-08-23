#!/usr/bin/env python2 --
import math, random, time

import pygame

pygame.init()

WIDTH = 320
HEIGHT = 200
SCALE = 3

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
		pygame.draw.rect(surf, self.color, (x, y, 16, 16))

	def is_solid(self, other):
		return self.solid

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
		# Allocate grid
		self.g = [[None for x in xrange(len(data[0]))]
			for y in xrange(len(data))]

		# Put stuff into grid
		for l, y in zip(data, xrange(len(data))):
			for c, x in zip(l, xrange(len(l))):
				self.g[y][x] = self.translate_level_char(c, x, y)

	def tick(self):
		# TODO.
		pass

	def draw(self, surf, camx, camy):
		"""
		Draws the level at (-camx, -camy) on surface "surf".
		"""
		for y in xrange(len(self.g)):
			for x in xrange(len(self.g[0])):
				cell = self.g[y][x]
				if cell != None:
					cell.draw(surf, x*16-camx, y*16-camy)

		pygame.draw.rect(surf, rgb(0, 255, 0),
			((self.player_x*16-camx)+4,
			(self.player_y*16-camy)+4,
			8, 8))

	def translate_level_char(self, c, x, y):
		"""
		Translates a character in the level source array
		to... I need something better to write here
		"""
		if c == ".":
			return None
		elif c == ",":
			return FloorCell()
		elif c == "#":
			return WallCell()
		elif c == "P":
			self.player_x = x
			self.player_y = y
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
..#,,#####,,#...
..#,,#...#,,#...
..####...####...
................
................
................
""".split("\n")[1:-1]
)

# Main loop
quitflag = False
oldkeys = pygame.key.get_pressed()
newkeys = pygame.key.get_pressed()
while not quitflag:
	# Draw screen
	screen.fill(rgb(0,0,170))
	lvl.draw(screen, 0, 0)
	flip_screen()

	# Prevent CPU fires
	# TODO: Proper frame timing
	time.sleep(0.01)

	# Poll events
	pygame.event.pump()
	newkeys = pygame.key.get_pressed()
	if oldkeys[pygame.K_ESCAPE] and not newkeys[pygame.K_ESCAPE]:
		quitflag = True

	# Update logic
	lvl.tick()

	# Transfer newkeys to oldkeys
	oldkeys = newkeys


# Clean up
pygame.quit()

