import os

import Client
import pygame
from pygame.locals import *
from pygame.draw import *
import pygame_gui
import Definitions
from Definitions import *
from Protocol import RequestType


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
hub = True
# TODO menu, button for creating games, list of current games to join, textbox to enter password, pause menu (with
#  compatibility with server)


# Cardinality = Client.send(RequestType.JOIN_GAME, {"name": "chen", "password": None}).value


def textBlock(text: str, x: float, y: float, size: int, color: tuple):
	x, y = x * getScreenSize()[0], y * getScreenSize()[1]
	font = pygame.font.Font(configPath + "/ARCADECLASSIC.TTF", size)
	screenText = font.render(text, True, color)
	window.blit(screenText, (x, y))


manager = pygame_gui.UIManager(getScreenSize())
CreateGameButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, getScreenSize()[1] - 50), (130, 50)),
                                            text='Create Game',
                                            manager=manager)
JoinGameButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((180, getScreenSize()[1] - 50), (130, 50)),
                                            text='Join Game',
                                            manager=manager)
while hub:
	timeDelta = clock.tick(FPS) / 1000
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			hub = False
			running = False
		if event.type == pygame_gui.UI_BUTTON_PRESSED:
			if event.ui_element == CreateGameButton:
				Cardinality = Client.sendAndRecv(RequestType.CREATE_GAME, {"name": "chen", "password": "none"}).value
				print(Cardinality)
				Client.sendAndRecv(RequestType.RETRIEVE_GAMES).print(True)
				CreateGameButton.kill()
				JoinGameButton.kill()
				hub = False
		manager.process_events(event)
	manager.update(timeDelta)
	manager.draw_ui(window)
	pygame.display.flip()
	window.fill((0, 0, 0))
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
	keys = pygame.key.get_pressed()
	clock.tick(FPS)
	# [Rendering]
	Client.send(RequestType.SET_Y, min(getRelativePosition()[1], 1 - Definitions.PLAYER_HEIGHT))
	print(min(getRelativePosition()[1], 1 - Definitions.PLAYER_HEIGHT))
	gameVars = Client.sendAndRecv(RequestType.GET_GAME_VARS).value
	screenSize = getScreenSize()
	if Cardinality == 1:
		opponentY = gameVars.player1y * getScreenSize()[1]
		rect(window, (255, 255, 255), (
			DISTANCE_FROM_WALL * screenSize[0], opponentY, PLAYER_WIDTH * screenSize[0],
			PLAYER_HEIGHT * screenSize[1]))
		rect(window, (255, 255, 255), (
			(1 - DISTANCE_FROM_WALL - PLAYER_WIDTH) * screenSize[0],
			min(getRelativePosition()[1], 1 - Definitions.PLAYER_HEIGHT) * getScreenSize()[1],
			PLAYER_WIDTH * screenSize[0],
			PLAYER_HEIGHT * screenSize[1]))
	else:
		opponentY = gameVars.player2y * getScreenSize()[1]
		rect(window, (255, 255, 255), (
			DISTANCE_FROM_WALL * screenSize[0],
			min(getRelativePosition()[1], 1 - Definitions.PLAYER_HEIGHT) * getScreenSize()[1],
			PLAYER_WIDTH * screenSize[0],
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
Client.send(RequestType.DISCONNECT)
pygame.quit()
