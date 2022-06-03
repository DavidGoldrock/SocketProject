import pickle
import random
import socket
import threading
import time
import numpy as np
from Definitions import *
# green terminal:
from os import system

system('color a')
# create socket
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
# global variables
games = []
playerCount = 0

def isColliding(r1x, r1y, r1w, r1h, r2x, r2y, r2w, r2h):
    return r1x + r1w >= r2x and \
        r1x <= r2x + r2w and \
        r1y + r1h >= r2y and \
        r1y <= r2y + r2h
def createRandomDirection():
	ballDirection = Vector.fromDegrees(random.uniform(75, 40), 1)
	if random.choice([True, False]):
		ballDirection.x *= -1
	if random.choice([True, False]):
		ballDirection.y *= -1
	return ballDirection


def gameThreadFunction(gameVars: Game, nothing):
	timeNow = time.time()
	ballDirection = createRandomDirection()
	while gameVars.gameOn:
		deltaTime = time.time() - timeNow
		gameVars.ball = gameVars.ball + (ballDirection * deltaTime * 5)

		if gameVars.ball.y + BALL_WIDTH > 1:
			ballDirection.y *= -1
			gameVars.ball.y = 1 - BALL_WIDTH

		if gameVars.ball.y - BALL_WIDTH < 0:
			ballDirection.y *= -1
			gameVars.ball.y = BALL_WIDTH

		if isColliding(DISTANCE_FROM_WALL , gameVars.player1y , PLAYER_WIDTH, PLAYER_HEIGHT ,gameVars.ball.x , gameVars.ball.y , BALL_WIDTH , BALL_WIDTH):
			ballDirection.x = 1
			# get the percentage of the way the ball is from the top of the player to the bottom
			# adjust it so it goes from 0.5 to -0.5
			# make it go in the same direction from where it went and more extreme
			ballDirection.y = abs(((gameVars.ball.y - gameVars.player1y) / PLAYER_HEIGHT) - 0.5) \
			                  * math.copysign(3.5, ballDirection.y)
			ballDirection.normalize()
		if isColliding(1 - DISTANCE_FROM_WALL - PLAYER_WIDTH , gameVars.player2y , PLAYER_WIDTH, PLAYER_HEIGHT ,gameVars.ball.x , gameVars.ball.y , BALL_WIDTH , BALL_WIDTH):
			ballDirection.x = -1
			# get the percentage of the way the ball is from the top of the player to the bottom
			# adjust it so it goes from 0.5 to -0.5
			# make it go in the same direction from where it went and more extreme
			ballDirection.y = abs(((gameVars.ball.y - gameVars.player2y) / PLAYER_HEIGHT) - 0.5) \
			                  * math.copysign(3.5, ballDirection.y)
			ballDirection.normalize()
		if gameVars.ball.x - BALL_WIDTH < 0:
			gameVars.player2Score += 1
			gameVars.ball = Vector(0.5, 0.5)
			ballDirection = createRandomDirection()
		if gameVars.ball.x + BALL_WIDTH > 1:
			gameVars.player1Score += 1
			gameVars.ball = Vector(0.5, 0.5)
			ballDirection = createRandomDirection()

		timeNow = time.time()


def sendMessage(code: int, conn: socket.socket, value=None):
	msg = Response(code, value)
	message = pickle.dumps(msg.toTuple())  # turn to bytes
	# send length of message in header bytes
	msgLength = str(len(message)).encode(FORMAT)
	msgLength += b' ' * (HEADER - len(msgLength))
	conn.send(msgLength)
	# send message
	conn.send(message)


def handleClient(conn, addr):
	global playerCount
	global games
	print(f"[CONNECT]{conn.getsockname()}")
	connected = True
	gameThread = None
	Cardinality = None
	while connected:
		msgLength = conn.recv(HEADER).decode(FORMAT)
		if msgLength:
			msgLength = int(msgLength)
			msg = Request.fromTuple(pickle.loads(conn.recv(msgLength)))  # receive number of bytes told by user
			# act in different ways depending on the request type
			match msg.RequestType:
				case RequestType.DISCONNECT:
					connected = False
					playerCount -= 1
					gameThread._args[0].gameOn = False
					print(f"[DISCONNECT]{conn.getsockname()}")
					print(f"[STATUS] Number of active users:{playerCount}")
					sendMessage(200, conn)
				case RequestType.CREATE_GAME:
					if msg.value is not None:
						gameThread = threading.Thread(target=gameThreadFunction, args=(msg.value, 0), daemon=True)
						gameThread.start()
						games.append({"thread": gameThread, "name": msg.value.name, "password": msg.value.password})
						print(f"[Game Added] {msg.value}")
						Cardinality = 0
						print(f"[Player Dict Updated]")
						sendMessage(200, conn)
					else:
						print(msg)
						sendMessage(402, conn)
				case RequestType.GET_GAME_VARS:
					sendMessage(200, conn, value=gameThread._args[0])
				case RequestType.SET_Y:
					if msg.value:
						if Cardinality == 0:
							gameThread._args[0].player1y = msg.value
						else:
							gameThread._args[0].player2y = msg.value
						sendMessage(200, conn)
					else:
						sendMessage(402, conn)
				case RequestType.JOIN_GAME:
					for g in games:
						if g.name == msg.value.name:
							if g.password == msg:
								gameThread = g.thread
								Cardinality = 1
								sendMessage(200, conn)
							else:
								sendMessage(401, conn)
							break
					sendMessage(403, conn)
				case other_message:
					sendMessage(400, conn)
					print(f"[UNEXPECTED REQUEST] type:{other_message} value: {msg.value}")


def start():
	global playerCount
	while True:
		server.listen()
		conn, addr = server.accept()
		thread = threading.Thread(target=handleClient, args=(conn, addr), daemon=True)
		thread.start()
		playerCount += 1
		print(f"[STATUS] Number of active users:{playerCount}")


print(f"[STARTING] SERVER: {SERVER} PORT: {PORT}")
start()