import pygame
from snakeclass import *

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((900, 600))
pygame.display.set_caption('Greedy Snake')
show_start(screen)
food_score, time_score = main_loop(screen)
show_end(screen, food_score, time_score)
show_top10(screen, food_score+time_score)
