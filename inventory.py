import pygame
from pygame.locals import *
from imageLoader import *

def inventory(playerID, display, WINDOW_SIZE, screen, clock):

    white = (255,255,255)
    blue =  (0,0, 128)
    font = pygame.font.Font('freesansbold.ttf', 16)
    textGold = font.render("gold: " + str(playerID.gold), True, white, blue)
    textGoldRect = textGold.get_rect()
    textGoldRect.center = (50,300)
    textHealth = font.render("health: " + str(playerID.currentHP)+'/'+str(playerID.maxHP), True, white, blue)
    textHealthRect = textHealth.get_rect()
    textHealthRect.center = (82, 332)
    cursX = 49
    cursY = 49
    inInventory = True
    while inInventory:
        display.fill((0,0,0))
        display.blit(textGold, textGoldRect)
        display.blit(textHealth, textHealthRect)
        display.blit(invGrid_image, (50,50))
        display.blit(cursor_image, (cursX,cursY))

        if 'dagger' in playerID.items:
            display.blit(dagger_image, (273,50))

        if 'hpPotion' in playerID.items:
            display.blit(hpPotionIcon_image, (49,49))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_i:
                    inInventory = False
                if event.key == K_RIGHT and cursX < 145:
                    cursX += 32
                if event.key == K_LEFT and cursX > 49:
                    cursX -= 32
                if event.key == K_UP and cursY > 49:
                    cursY -= 32
                if event.key == K_DOWN and cursY < 209:
                    cursY += 32

        surf = pygame.transform.scale(display, WINDOW_SIZE)
        screen.blit(surf, (0,0))
        pygame.display.update()
        dt = clock.tick(60)/1000
