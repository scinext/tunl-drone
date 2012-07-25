'''
Created on Jun 29, 2012

@author: Peter Hendriks
'''
import quad_connector
import random, time, sys, math, json
import pygame
from pygame import locals

#vars:
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
black = (0, 0, 0)
white = (255, 255, 255)

grad2rad = math.pi / 180.0
rad2grad = 180.0 / math.pi

# Config 
field_of_view = 90.0 # degrees of field of vision of the camera

#Start PyGame:
pygame.init()
#Create a PyGame screen, and set its size to 640x480L
screen = pygame.display.set_mode((1024,768))
#Set the window caption:
pygame.display.set_caption('Remote Webcam Viewer')
#Load a font:
font = pygame.font.SysFont("Arial",14)
#Create a PyGame clock which will be used to limit the fps:
clock = pygame.time.Clock()

joystick = pygame.joystick.Joystick(0)
joystick.init()

roll_x = 50
roll_y = 50
pitch_x = 50
pitch_y = 100
compass_x = 50
compass_y = 150

quad_client = quad_connector.quad_client('192.168.0.36', 4000)
quad_client.start()

roll = 0.0
pitch = 0.0
yaw = 0.0

joyroll = 0.0
joypitch = 0.0

while 1:
    #-------------- INPUT -------------
    for e in pygame.event.get(): # iterate over event stack
        if e.type == pygame.locals.JOYAXISMOTION: # 7
            joyroll , joypitch = joystick.get_axis(0), joystick.get_axis(1)    
            
    screen.fill(black)
    x, y = screen.get_size()
    middle = (x / 2, y / 2)
    pygame.draw.line(screen, green, ((x / 2) + 10, (y / 2)), ((x / 2) - 10, (y / 2)))
    pygame.draw.line(screen, green, ((x / 2), (y / 2) + 10), ((x / 2), (y / 2) - 10))
    
    # draw middle cross
    
    
    jsonstring = quad_client.read_data()
    #rolldeg = str(joyroll * 90.0)
    #pitchdeg = str(joypitch * 90.0)
    #jsonstring = '[' + rolldeg + ', ' + pitchdeg + ', 0.0]'
    if (len(jsonstring) > 0):
        jsonstring = jsonstring[:jsonstring.rindex("]") + 1]
        last_read = jsonstring[jsonstring.rindex("["):]
        jsonarray = json.loads(last_read)
        
        roll = jsonarray[0] * grad2rad
        pitch = jsonarray[1] * grad2rad
        yaw = jsonarray[2] * grad2rad
        
        screen.blit(font.render(str(yaw), 1, green), (10, 10))
        
        #print str(roll) + " - " + str(pitch) + " - " + str(yaw)
        
        # ---------------------- analog meters -------------------
        start_pos = (roll_x + 20 * math.cos(roll) , roll_y + 20 * math.sin(roll))
        end_pos = (roll_x + -20 * math.cos(roll), roll_y + -20 * math.sin(roll))
        pygame.draw.line(screen, red, start_pos, end_pos)
        
        start_pos = (pitch_x + 20 * math.cos(pitch) , pitch_y + 20 * math.sin(pitch))
        end_pos = (pitch_x + -20 * math.cos(pitch), pitch_y + -20 * math.sin(pitch))
        pygame.draw.line(screen, blue, start_pos, end_pos)
        
        start_pos = (compass_x, compass_y)
        end_pos = (compass_x + -20 * math.cos(yaw), compass_y + -20 * math.sin(yaw))
        pygame.draw.line(screen, white, start_pos, end_pos)
        # ---------------------- analog meters -------------------
        
        
        degree = pitch * rad2grad
        first_line_degree = math.ceil(degree / 10.0) * 10.0 # get closest line above the middle of the screen
        line_distance = -(x / (field_of_view / 10.0))
        
        
        first_line_above_center = (degree - first_line_degree) * (line_distance / 10)
        line_center = {}
        
        
        line_center[0] = ((math.sin(roll) * (first_line_above_center - (2* line_distance))), (math.cos(roll) * (first_line_above_center - (2 *line_distance))))
        line_center[1] = ((math.sin(roll) * (first_line_above_center - line_distance)), (math.cos(roll) * (first_line_above_center - line_distance)))
        line_center[2] = ((math.sin(roll) * first_line_above_center), (math.cos(roll) * first_line_above_center))
        line_center[3] = ((math.sin(roll) * (first_line_above_center + line_distance)), (math.cos(roll) * (first_line_above_center + line_distance)))
        line_center[4] = ((math.sin(roll) * (first_line_above_center + (2* line_distance))), (math.cos(roll) * (first_line_above_center + (2 *line_distance))))
        
        change_x = math.cos(roll) * (x / 10) # line is one 5th of screen width 
        change_y = math.sin(roll) * (x / 10)
        
        for i in range(0, 5):
            
            start_pos = ((middle[0] + line_center[i][0] - change_x), (middle[1] + line_center[i][1] + change_y))
            end_pos = ((middle[0] + line_center[i][0] + change_x), (middle[1] + line_center[i][1] - change_y))
            pygame.draw.line(screen, green, start_pos, end_pos)
            degreestr = (first_line_degree + 20) - (i * 10.0)
            screen.blit(font.render(str(degreestr), 1, green), ((start_pos[0] - 20), (start_pos[1] - 5)))
        
        #cil_roll.axis=(0.2*cos(roll),0.2*sin(roll),0)
        #cil_roll2.axis=(-0.2*cos(roll),-0.2*sin(roll),0)
        #cil_pitch.axis=(0.2*cos(pitch),0.2*sin(pitch),0)
        #cil_pitch2.axis=(-0.2*cos(pitch),-0.2*sin(pitch),0)
        #arrow_course.axis=(0.2*sin(yaw),0.2*cos(yaw),0)
        
    clock.tick(50)
    pygame.display.flip()
   