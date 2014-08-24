#!/usr/bin/env python2 --
import math, os, random, time

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
screen = pygame.Surface((WIDTH, HEIGHT), 0, screen_real.get_bitsize()).convert(screen_real)

def subtile(img, w, h, cx, cy):
	"""
	Gets a tile-indexed w by h subsurface from the tilemap "img".
	"""

	return img.subsurface((cx*w, cy*h, w, h))

# Load some images
img_tiles = pygame.image.load(os.path.join("dat", "tiles.png"))
#img_tiles.set_colorkey(0, pygame.RLEACCEL)
img_tiles = img_tiles.convert(screen)

img_tiles_floor = subtile(img_tiles, 16, 16, 0, 1)
img_tiles_portal = subtile(img_tiles, 16, 16, 0, 2)
img_tiles_wall = subtile(img_tiles, 16, 16, 0, 3)
img_tiles_doorno = subtile(img_tiles, 16, 16, 0, 4)
img_tiles_dooryes = subtile(img_tiles, 16, 16, 0, 5)

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
	imgs = None
	solid = True

	def draw(self, surf, x, y, world):
		"""
		Draws the cell to the surface "surf".
		"""
		if self.imgs == None:
			# No image - draw a rect
			pass
			#pygame.draw.rect(surf, self.color, (x, y, 16, 16))

		elif type(self.imgs) in (list, tuple,):
			# Indexable sequence - pick an image
			# TODO: do more than just the first image
			surf.blit(self.imgs[0], (x, y))

		else:
			# Assuming this is a single image
			surf.blit(self.imgs, (x, y))

	def on_enter(self, ent):
		"""
		CALLBACK: Handles entry of an entity.
		"""
		pass

	def on_exit(self, ent):
		"""
		CALLBACK: Handles exit of an entity.
		"""
		pass

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

	def draw(self, surf, x, y, world):
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
	color = rgb(0, 255, 255)

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
		if not(self.ox == 0 and self.oy == 0):
			if self.ox != 0:
				self.ox += (1 if self.ox < 0 else -1)
			if self.oy != 0:
				self.oy += (1 if self.oy < 0 else -1)

			# If we've just entered the cell, call on_enter
			if self.ox == 0 and self.oy == 0:
				self.lvl.get_cell(self.cx, self.cy).on_enter(self)

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

			# Bail if we're not moving anywhere
			if vx == 0 and vy == 0:
				return

			# Work out if anything is in that cell
			if self.cell_is_walkable(self.cx + vx, self.cy + vy):
				self.lvl.get_cell(self.cx, self.cy).on_exit(self)
				self.cx += vx
				self.cy += vy
				self.ox -= 16*vx
				self.oy -= 16*vy
			elif self.cell_is_walkable(self.cx + vx, self.cy):
				self.lvl.get_cell(self.cx, self.cy).on_exit(self)
				self.cx += vx
				self.ox -= 16*vx
			elif self.cell_is_walkable(self.cx, self.cy + vy):
				self.lvl.get_cell(self.cx, self.cy).on_exit(self)
				self.cy += vy
				self.oy -= 16*vy
	

class FloorCell(BaseCell):
	color = rgb(170, 100, 85)
	imgs = img_tiles_floor
	solid = False

class WallCell(BaseCell):
	color = rgb(55, 55, 55)
	imgs = img_tiles_wall
	solid = True
	
class NextLevelCell(BaseCell):
    color = rgb(170, 100, 85)
	imgs = img_tiles_portal #TODO : Make a green portal for this cell
	solid = False
	
	'''TODO:
	def on_entry(): 
	    inrement listPos by 1 (i.e. listPos += 1)
    '''
	
class WorldAcceptCell(BaseCell):
	def __init__(self, worlds):
		self.worlds = worlds

	def is_solid(self, world=None):
		return not (world in self.worlds)

	def draw(self, surf, x, y, world):
		surf.blit(
			(img_tiles_dooryes if world in self.worlds else img_tiles_doorno),
			(x, y))
		"""
		pygame.draw.rect(surf,
			(rgb(0, 255, 0) if world in self.worlds else rgb(255, 0, 0)),
			(x, y, 16, 16))
		"""

class WorldChangeCell(BaseCell):
	solid = False

	def __init__(self, change_map):
		self.change_map = change_map

	def on_enter(self, ent):
		if ent.world in self.change_map:
			ent.world = self.change_map[ent.world]

	def draw(self, surf, x, y, world):
		surf.blit(
			(img_tiles_portal if world in self.change_map else img_tiles_floor),
			(x, y))
		"""
		pygame.draw.rect(surf,
			(rgb(40, 0, 64) if world in self.change_map else rgb(170, 100, 85)),
			(x, y, 16, 16))
		"""

class Level:
	"""
	A Level contains all the logic and stuff for a, well, level.
	"""
	def __init__(self, data):
		# Allocate entity list
		self.ents = []
		self.player = None

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

	def draw(self, surf, camx, camy, world):
		"""
		Draws the level at (-camx, -camy) on surface "surf", using world "world".
		"""

		# Draw cells
		for y in xrange(len(self.g)):
			for x in xrange(len(self.g[0])):
				cell = self.g[y][x]
				if cell != None:
					cell.draw(surf, x*16-camx, y*16-camy, world)

		# Draw entities
		for ent in self.ents:
			ent.draw(surf, -camx, -camy, world)

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

		elif c == "0":
			return WorldAcceptCell(set((0,)))

		elif c == "1":
			return WorldChangeCell({0:2, 2:0})

		elif c == "2":
			return WorldAcceptCell(set((2,)))

		elif c == "3":
			return WorldChangeCell({2:4, 4:2})

		elif c == "4":
			return WorldAcceptCell(set((4,)))

		elif c == "5":
			return WorldChangeCell({4:0})
		
		elif c == "6":
		    return NextLevelCell()

		elif c == "P":
			assert self.player == None
			self.player = PlayerEnt(self, x, y)
			self.ents.append(self.player)
			return FloorCell()

		else:
			raise Exception("invalid level char: %s" % repr(c))

'''
-----Tom's Nooby guide to help him create maps---
0 is open at the start.
1 changes the state of 2.
2 is locked until 1 is entered.
3 changes the state of 4.
4 is locked until 3 is entered.
5 changes the state of 0.
6 is the end of the level.
P is the Player's starting position.
'''		
			
# Create test level
lvl = Level(
"""
##################
#5,32,,,2,,##,,,,#
#,###,5,#####,1,,#
#4###,,,0,,,0,,,,#
#,,,##44########2#
#,,,32P,#,1,#,,#,#
######,,0,,,2,,#,#
.#,1,2,,#####,,#,#
.#,,,#,54,,,2,,#,#
.#,######,3,####,#
.#,543210,,,0,,,1#
.#################
""".split("\n")[1:-1]
)

#One list to rule them all

levelList = [lvl]

#Calculates total levels (will be used to display an end-game message)

totalLevels = len(levelList)

#Used to determine what level the player is on

levelPos = 0

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
		levelList[levelPos].draw(screen, 0, 0, levelList[levelPos].player.world)
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
		levelList[levelPos].tick()

		# Transfer newkeys to oldkeys
		oldkeys = newkeys

		# Update tick counter
		tick_next += SPF


# Clean up
pygame.quit()

