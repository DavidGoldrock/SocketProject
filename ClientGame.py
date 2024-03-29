import os

import Client
import pygame
from pygame.locals import *
from pygame.draw import *
import pygame_gui
import Definitions
from Definitions import *
from Protocol import RequestType, ApplicationError


def getScreenSize():
    return pygame.display.get_surface().get_size()


def getRelativePosition():
    return pygame.mouse.get_pos()[0] / getScreenSize()[0], pygame.mouse.get_pos()[1] / \
           getScreenSize()[1]


def textBlock(text: str, x: float, y: float, size: int, color: tuple | str, center: bool = True,
              absoluteSize: bool = True, font=None):
    if font is None:
        try:
            font = pygame.font.Font(configPath + "/ARCADECLASSIC.TTF", size)
        except Exception:
            print("file missing")
            font = pygame.font.SysFont("Arial", size)
        text = text.replace(' ', '     ')
    screenText = font.render(text, False, color)

    if absoluteSize:
        x, y = x * getScreenSize()[0], y * getScreenSize()[1]

    if center:
        x -= screenText.get_size()[0] // 2
        y -= screenText.get_size()[1] // 2
    window.blit(screenText, (x, y))


def longTextBlock(texts: list[str], x: float, y: float, size: int, color: tuple | str, center: bool = True,
                  absoluteSize: bool = True, sizeInPixels=True,font=None):
    realSize = size
    if not sizeInPixels:
        realSize = size * 16 // 12
    # split based on max length of text
    for i, text in enumerate(texts):
        print(texts)
        textBlock(text,
                  x,
                  y + 4 * i / realSize,
                  realSize,
                  color,
                  center,
                  absoluteSize,
                  font)


def exitGame():
    try:
        Client.send(RequestType.DISCONNECT)
    except OSError:
        pass
    pygame.quit()
    exit()


pygame.init()
configPath = os.path.dirname(os.path.realpath(__file__))
defaultWidth = 640
defaultHeight = 640
window = pygame.display.set_mode([defaultWidth, defaultHeight], RESIZABLE)
clock = pygame.time.Clock()
running = True
hub = True

# server is down
while not Client.isConnected:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exitGame()
    keys = pygame.key.get_pressed()
    clock.tick(FPS)
    window.fill((0, 0, 0))
    longTextBlock(
        [f"Server {str(Client.ADDR)} is down", "please close the application and", "open it again at a later time"],
        0.5,
        0.3,
        getScreenSize()[1] // 30,
        "white",
        font=pygame.font.SysFont("Arial", getScreenSize()[1] // 30))
    pygame.display.flip()
try:
    games = Client.sendAndRecv(RequestType.RETRIEVE_GAMES).value

    # TODO menu, button for creating games, list of current games to join, textbox to enter password, pause menu (with
    #  compatibility with server)


    # Cardinality = Client.send(RequestType.JOIN_GAME, {"name": "chen", "password": None}).value


    manager = pygame_gui.UIManager(getScreenSize())
    CreateGameButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, getScreenSize()[1] - 50), (130, 50)),
                                                    text='Create Game',
                                                    manager=manager)
    RefreshButton = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((130, getScreenSize()[1] - 50), (130, 50)),
                                                 text='Refresh',
                                                 manager=manager)
    NameTextBox = pygame_gui.elements.UITextEntryBox(
        relative_rect=pygame.Rect((getScreenSize()[1] / 2 - 65, getScreenSize()[1] / 2 - 85), (130, 50)),
        manager=manager)
    PasswordTextBox = pygame_gui.elements.UITextEntryBox(
        relative_rect=pygame.Rect((getScreenSize()[1] / 2 - 65, getScreenSize()[1] / 2 - 25), (130, 50)),
        manager=manager)
    OKButton = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((getScreenSize()[1] / 2 + 65, getScreenSize()[1] / 2 + 25), (65, 50)),
        text='OK',
        manager=manager)
    CancelButton = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((getScreenSize()[1] / 2 + 130, getScreenSize()[1] / 2 + 25), (65, 50)),
        text='Cancel',
        manager=manager)
    gameButtons = [pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((0, getScreenSize()[1] / 5 + 50 * i), (getScreenSize()[0], 50)),
        text=game,
        manager=manager) for i, game in enumerate(games)]
    CancelButton.hide()
    OKButton.hide()
    NameTextBox.hide()
    PasswordTextBox.hide()
    request = None
    joinGameName = None

    # show game
    print(f"{Client.isConnected=}")
    while hub:
        timeDelta = clock.tick(FPS) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exitGame()
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == CreateGameButton:
                    CancelButton.show()
                    OKButton.show()
                    NameTextBox.show()
                    NameTextBox.set_text('')
                    PasswordTextBox.show()
                    PasswordTextBox.set_text('')
                    CreateGameButton.disable()
                    RefreshButton.disable()
                    for button in gameButtons:
                        button.disable()
                    request = RequestType.CREATE_GAME
                if event.ui_element == CancelButton:
                    CancelButton.hide()
                    OKButton.hide()
                    NameTextBox.hide()
                    PasswordTextBox.hide()
                    CreateGameButton.enable()
                    RefreshButton.enable()
                    for button in gameButtons:
                        button.enable()
                if event.ui_element == OKButton:
                    if request == RequestType.CREATE_GAME:
                        Cardinality = Client.sendAndRecv(request, {"name": NameTextBox.get_text(),
                                                                   "password": PasswordTextBox.get_text()}).value
                    elif request == RequestType.JOIN_GAME:
                        print(PasswordTextBox.get_text())
                        Cardinality = Client.sendAndRecv(request, {"name": joinGameName,
                                                                   "password": PasswordTextBox.get_text()}).value
                    Client.sendAndRecv(RequestType.RETRIEVE_GAMES).print(True)
                    CreateGameButton.kill()
                    RefreshButton.kill()
                    CancelButton.kill()
                    OKButton.kill()
                    NameTextBox.kill()
                    PasswordTextBox.kill()
                    for button in gameButtons:
                        button.kill()
                    hub = False
                if event.ui_element in gameButtons:
                    CancelButton.show()
                    OKButton.show()
                    PasswordTextBox.show()
                    PasswordTextBox.set_text('')
                    CreateGameButton.disable()
                    RefreshButton.disable()
                    for button in gameButtons:
                        button.disable()
                    request = RequestType.JOIN_GAME
                    joinGameName = event.ui_element.text
                if event.ui_element == RefreshButton:
                    games = Client.sendAndRecv(RequestType.RETRIEVE_GAMES).value
                    for button in gameButtons:
                        button.kill()
                    gameButtons = [pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((0, getScreenSize()[1] / 5 + 50 * i), (getScreenSize()[0], 50)),
                        text=game,
                        manager=manager) for i, game in enumerate(games)]
            manager.process_events(event)
        manager.update(timeDelta)
        manager.draw_ui(window)
        pygame.display.flip()
        window.fill((0, 0, 0))
    print(Cardinality)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exitGame()
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
        textBlock(str(gameVars.player1Score), DISTANCE_FROM_WALL, 0, 48, (255, 255, 255), absoluteSize=True, center=False)
        textBlock(str(gameVars.player2Score), 1 - DISTANCE_FROM_WALL, 0, 48, (255, 255, 255), absoluteSize=True, center=False)
        pygame.display.flip()
        window.fill((0, 0, 0))
except ApplicationError as e:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exitGame()
        keys = pygame.key.get_pressed()
        clock.tick(FPS)
        textBlock("ERROR SCREEN", 0.5, 0.1, 40, "white",font=pygame.font.SysFont("Arial", 40))
        textBlock(str(e), 0.5, 0.5, 25, "white",font=pygame.font.SysFont("Arial", 25))
        pygame.display.flip()
        window.fill((255, 0, 0))
exitGame()
