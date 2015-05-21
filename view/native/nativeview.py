from view import viewinterface as v
import pygame
from pygame.locals import *

class nativeview(v.viewinterface):

	def init (self):
		# Initialise screen
		pygame.init()
		self.screen = pygame.display.set_mode((150, 50))
		pygame.display.set_caption('Basic Pygame program')

		# Fill background
		self.background = pygame.Surface(self.screen.get_size())
		self.background = self.background.convert()
		self.background.fill((250, 250, 250))

		# Display some text
		font = pygame.font.Font(None, 36)
		text = font.render("Hello There", 1, (10, 10, 10))
		textpos = text.get_rect()
		textpos.centerx = self.background.get_rect().centerx
		self.background.blit(text, textpos)

	def handle_events (self):
		for event in pygame.event.get():
			if event.type == QUIT:
				return False
		return True

	def display (self):
		# Blit everything to the screen
		self.screen.blit(self.background, (0, 0))
		pygame.display.flip()

	def quit (self):
		pygame.quit()