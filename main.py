#!/usr/bin/env python2 --
import math, random, time

import pygame

pygame.init()

WIDTH = 320
HEIGHT = 200
SCALE = 3

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

# Set up display
pygame.display.set_caption("LD30")
screen_real = pygame.display.set_mode((WIDTH*SCALE, HEIGHT*SCALE), 0, 0)
screen = pygame.Surface((WIDTH, HEIGHT), 0, screen_real.get_bitsize())

# TEST CODE.
tstart = time.time()
for i in xrange(1000):
	screen.fill(rgb(0, 0, 255))
	for j in xrange(100):
		pygame.draw.circle(screen,
			rgb(*tuple(random.randint(0, 255) for _ in xrange(3))),
			(random.randint(0, WIDTH), random.randint(0, HEIGHT)),
			random.randint(10, 30), 1)

	flip_screen()

tend = time.time()
tdelta = tend - tstart
print "%f FPS" % (float(1000)/float(tdelta))

# Clean up
pygame.quit()

