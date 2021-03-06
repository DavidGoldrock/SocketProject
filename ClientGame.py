import os

import Client
import pygame
from pygame.locals import *
from pygame.draw import *
from Definitions import *
from RequestResponse import *


def getScreenSize():
	return pygame.display.get_surface().get_size()


def getRelativePosition():
	return pygame.mouse.get_pos()[0] / getScreenSize()[0], pygame.mouse.get_pos()[1] / \
	       getScreenSize()[1]


pygame.init()
configPath = os.path.dirname(os.path.realpath(__file__))
defaultWidth = 640
defaultHeight = 640
window = pygame.display.set_mode([defaultWidth, defaultHeight], RESIZABLE)
clock = pygame.time.Clock()
running = True
# TODO menu, button for creating games, list of current games to join, textbox to enter password, pause menu (with
#  compatibility with server)
Cardinality = Client.send(RequestType.CREATE_GAME, {"name": "chen", "password": "none"}).value


# Cardinality = Client.send(RequestType.JOIN_GAME, {"name": "chen", "password": None}).value


def textBlock(text: str, x: float, y: float, size: int, color: tuple):
	x, y = x * getScreenSize()[0], y * getScreenSize()[1]
	font = pygame.font.Font(configPath + "/ARCADECLASSIC.TTF", size)
	screenText = font.render(text, True, color)
	window.blit(screenText, (x, y))


while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
	keys = pygame.key.get_pressed()
	clock.tick(FPS)
	# [Rendering]
	Client.send(RequestType.SET_Y, getRelativePosition()[1])
	gameVars = Client.send(RequestType.GET_GAME_VARS).value
	screenSize = getScreenSize()
	if Cardinality == 1:
		opponentY = gameVars.player1y * getScreenSize()[1]
		rect(window, (255, 255, 255), (
			DISTANCE_FROM_WALL * screenSize[0], opponentY, PLAYER_WIDTH * screenSize[0],
			PLAYER_HEIGHT * screenSize[1]))
		rect(window, (255, 255, 255), (
			(1 - DISTANCE_FROM_WALL - PLAYER_WIDTH) * screenSize[0], pygame.mouse.get_pos()[1],
			PLAYER_WIDTH * screenSize[0],
			PLAYER_HEIGHT * screenSize[1]))
	else:
		opponentY = gameVars.player2y * getScreenSize()[1]
		rect(window, (255, 255, 255), (
			DISTANCE_FROM_WALL * screenSize[0], pygame.mouse.get_pos()[1], PLAYER_WIDTH * screenSize[0],
			PLAYER_HEIGHT * screenSize[1]))
		rect(window, (255, 255, 255), (
			(1 - DISTANCE_FROM_WALL - PLAYER_WIDTH) * screenSize[0], opponentY, PLAYER_WIDTH * screenSize[0],
			PLAYER_HEIGHT * screenSize[1]))
	circle(window, (255, 255, 255), (gameVars.ball.x * screenSize[0], gameVars.ball.y * screenSize[1]),
	       BALL_WIDTH * screenSize[0])
	textBlock(str(gameVars.player1Score), DISTANCE_FROM_WALL, 0, 48, (255, 255, 255))
	textBlock(str(gameVars.player2Score), 1 - DISTANCE_FROM_WALL, 0, 48, (255, 255, 255))
	pygame.display.flip()
	window.fill((0, 0, 0))
Client.send(RequestType.DISCONNECT).print()
pygame.quit()
