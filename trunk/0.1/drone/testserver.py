'''
Created on Jun 29, 2012

@author: Peter Hendriks
'''
import quad_connector
import minimu9
import imu
import random, time, sys, json
import pygame

fps = 50

quad_server = quad_connector.quad_server(4000)
quad_server.start()


imumodule = minimu9.minimu9(0, 0x69, 0x18, 0x1e)

imu = imu.imu(imumodule)
imu.start()

pygame.init()
clock = pygame.time.Clock()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    data = json.dumps(imu.output_array())
    quad_server.send(data)
    clock.tick(fps)

