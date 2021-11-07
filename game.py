import pygame, sys, math, os, ast
from pygame.locals import *
from imageLoader import *
from inventory import *


#-----------------TODO
##TODO:
## add slots 2 and 3 for save files
#
# make gold be used for something
#


#-----------------------Setup
pygame.init()
clock = pygame.time.Clock()
pygame.display.set_caption('pkmnClone')
WINDOW_SIZE = (1200,800)
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
display = pygame.Surface((600,400))

#-----------------------music setup
#-----------------------graphical setup

player_image.set_colorkey((248,248,248))
merchant_image.set_colorkey((248,248,248))
TILE_SIZE = wall_image.get_width()

#-------------load sprites animations

global animation_frames
animation_frames = {}

def load_animation(path, frame_durations):
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'
        animation_image = pygame.image.load(img_loc).convert()
        animation_image.set_colorkey((248,248,248))
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data

def change_action(action_var, frame, new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var, frame

animation_database = {}

animation_database['run'] = load_animation('player_animations/run',[15,9,15,9])
animation_database['runBack'] = load_animation('player_animations/runBack', [15,9,15,9])
animation_database['runLeft'] = load_animation('player_animations/runLeft', [15,9])
animation_database['runRight'] = load_animation('player_animations/runRight', [15,9])
animation_database['idle'] = load_animation('player_animations/idle',[40])



#-----------------------loadMap
def load_map(path):
    f = open(path + '.txt', 'r')
    data = f.read()
    f.close()
    data = data.split('\n')
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map

gameMap = load_map('map')
#-----------------------player class
#TODO: make maxHp and current hp separate

class player:
    def __init__(self, username, rect, movement, currentHP, maxHP, attackPower, items, gold):
        self.username = username
        self.rect = rect
        self.movement = movement
        self.currentHP = currentHP
        self.maxHP = maxHP
        self.attackPower = attackPower
        self.items = items
        self.gold = gold
#-----------------------enemy class
#TODO: make maxHp and currentHp separate variables
class enemy:
    def __init__(self, hp, attackPower, goldLoot):
        self.hp = hp
        self.attackPower = attackPower
        self.goldLoot = goldLoot
#-----------------------move function
def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

def move(rect, movement, tiles):
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement [0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types


#-----------------------Inventory

#----------gameover
def gameOver():
    inScreen = True

    while inScreen:
        display.fill((0,0,0))
        display.blit(gameOver_image, (320,130))



        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()


        surf = pygame.transform.scale(display, WINDOW_SIZE)
        screen.blit(surf, (0,0))
        pygame.display.update()

#----------------item selection screen during an encounter

def itemSelect(playerID):
    inScreen = True
    cursX = 49
    cursY = 49
    while inScreen:
        display.fill((0,0,0))
        display.blit(itemSelect_image, (50,50))
        display.blit(cursor_image, (cursX,cursY))
        display.blit(use_image, (200, 70))

        if 'hpPotion' in playerID.items:
            display.blit(hpPotionIcon_image, (49,49))
            slot1 = 'potion'

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_b:
                    inScreen = False
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
                if event.key == K_u and cursX == 49 and cursY == 49 and slot1 == 'potion':
                    playerID.currentHP = playerID.maxHP
                    playerID.items.remove('hpPotion')
                    slot1 = 'empty'
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        surf = pygame.transform.scale(display, WINDOW_SIZE)
        screen.blit(surf, (0,0))
        pygame.display.update()


#-----------------------BattleSequence
# TODO: make an enemy object parameter so that this
# function can be used for multiple enemies on the overworld
def battleSequence(playerID, haventFought, enemy):
    inBattle = True
    playerTurn = True
    takenDmg = False
    inReaction = False
    delayTimer = 0


    baseAttack = playerID.attackPower
    if 'dagger' in playerID.items:
        playerID.attackPower += 10


    red = (255,0,0)
    blue =  (0,0, 128)
    font = pygame.font.Font('freesansbold.ttf', 16)
    textDmgGiven = font.render('-' + str(playerID.attackPower), True, red, blue)
    textRectDmgGiven = textDmgGiven.get_rect()
    textRectDmgGiven.center = (420,70)
    textDmgTaken = font.render('-' + str(enemy.attackPower), True, red, blue)
    textRectDmgTaken = textDmgTaken.get_rect()
    textRectDmgTaken.center = (50, 350)
    while inBattle:
        display.fill((0,0,0))
        display.blit(player_image, (50, 300))


        pygame.draw.rect(display, (228, 25, 25), (50, 290, playerID.maxHP, 4))
        pygame.draw.rect(display, (25, 228, 59), (50, 290, playerID.currentHP, 4))



        display.blit(enemy_image, (400, 100))
        pygame.draw.rect(display, (228, 25, 25), (400, 90, 100, 4))
        pygame.draw.rect(display, (25, 228, 59), (400, 90, enemy.hp, 4))

        if playerTurn:

            display.blit(battleMenu_image, (50, 130))

            if takenDmg:
                display.blit(textDmgTaken, textRectDmgTaken)
                if playerID.currentHP <= 0:
                    gameOver()



#---------comment shortcut: alt + 3
#---------uncomment shortcut: alt + 4




        if enemy.hp <= 0:
            inBattle = False
            haventFought = False

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_c:
                    inBattle = False
                    haventFought = False
                if event.key == K_b:
                    itemSelect(playerID)
                if event.key == K_a and playerTurn:


                    enemy.hp -= playerID.attackPower
                    delayTimer = 0
                    playerTurn = False




        if not playerTurn:
            if 'dagger' in playerID.items:
                display.blit(dagger_image, (82, 300))
            display.blit(textDmgGiven, textRectDmgGiven)
            delayTimer += dt
            if delayTimer >= 1:
                playerID.currentHP -= enemy.attackPower
                playerTurn = True
                takenDmg = True
                delayTimer = 0


        surf = pygame.transform.scale(display, WINDOW_SIZE)
        screen.blit(surf, (0,0))
        pygame.display.update()
        dt = clock.tick(60)/1000


    playerID.gold += enemy.goldLoot
    playerID.attackPower = baseAttack
    return haventFought

#------------Title Screen (put in separate py file later)

def titleScreen():
    inTitleScreen = True
    while inTitleScreen:

        display.fill((0,0,0))
        display.blit(titleMenu_image, (50,50))
        display.blit(files_image, (206, 196))

        if os.stat('saveFiles/file1.txt').st_size != 0:
            file = open('saveFiles/file1.txt', 'r')
            gatherData = file.read()
            listData = ast.literal_eval(gatherData)
            playerObject = player(listData[0], pygame.Rect(listData[1][0], listData[1][1], listData[1][2], listData[1][3]), listData[2], listData[3], listData[4], listData[5], listData[6], listData[7])
            display.blit(fileOccupied_image, (214, 204))
            font = pygame.font.Font('alagard.ttf', 16)
            usernameText = font.render(' 1:   ' + str(listData[0]), True, (255,255,255),(0,0,128))
            usernameTextRect = usernameText.get_rect()
            usernameTextRect.center = (278,220)
            display.blit(usernameText, usernameTextRect)
            file.close



        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_1 and os.stat('saveFiles/file1.txt').st_size == 0:
                    print('this file is empty yay :)')
                    username = typeUsername()
                    playerRect = pygame.Rect(32,32, player_image.get_width(), player_image.get_height())
                    playerObject = player(username, playerRect, [0,0], 30, 100, 20, [], 0)
                    file = open('saveFiles/file1.txt', 'w')
                    str_data = [playerObject.username, [playerObject.rect.left,playerObject.rect.top, playerObject.rect.width, playerObject.rect.height], playerObject.movement, playerObject.currentHP, playerObject.maxHP, playerObject.attackPower, playerObject.items, playerObject.gold]
                    file.write(str(str_data))
                    file.close()
                    return playerObject
                elif event.key == K_1:
                    return playerObject




        surf = pygame.transform.scale(display, WINDOW_SIZE)
        screen.blit(surf, (0,0))
        pygame.display.update()

#------------------------save Function
def saveGame(playerObject):
    file = open('saveFiles/file1.txt', 'w')
    file.truncate(0)
    str_data = [playerObject.username, [playerObject.rect.left,playerObject.rect.top, playerObject.rect.width, playerObject.rect.height], playerObject.movement, playerObject.currentHP, playerObject.maxHP, playerObject.attackPower, playerObject.items, playerObject.gold]
    file.write(str(str_data))
    file.close

#------allow user to type username. display text as user types

def typeUsername():
    inUsernameScreen = True
    text = ''
    while inUsernameScreen:
        display.fill((0,0,0))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    return text
                elif event.key == K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode


#-------------------pause menu function (TODO: put in separate py file)

def pause(playerObject):
    inPauseMenu = True
    while inPauseMenu:
        display.fill((0,0,0))
        display.blit(pauseMenu_image, (50,50))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_p:
                    inPauseMenu = False
                if event.key == K_s:
                    saveGame(playerObject)
                    inPauseMenu = False
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()




        surf = pygame.transform.scale(display, WINDOW_SIZE)
        screen.blit(surf, (0,0))
        pygame.display.update()

#-----------------------Overworld Zone Function Setup (not battle)

true_scroll = [0,0]


inOverworld = True
def overworld(playerID):
    movingUp = False
    movingDown = False
    movingLeft = False
    movingRight = False
    haventFought_1 = True
    haventFought_2 = True
    haventFought_3 = True
    haventFought_4 = True
    haventPickedUpDagger = True
    haventPickedUpFirstHpPotion = True
    delayTimer = 0

    player_action = 'idle'
    player_frame = 0
    player_flip = False

    stack = ['idle']
    currentAction = stack.pop()

    while inOverworld:
        display.fill((34,139,34))


        true_scroll[0] += (playerID.rect.x-true_scroll[0]-280)/20
        true_scroll[1] += (playerID.rect.y-true_scroll[1]-150)/20
        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        tile_rects = []
        y = 0
        for row in gameMap:
            x = 0
            for tile in row:
                if tile == '1':
                    display.blit(wall_image, (x * TILE_SIZE-scroll[0], y * TILE_SIZE-scroll[1]))
                if tile == '2' and haventFought_1:
                    display.blit(door_image, (x * TILE_SIZE-scroll[0], y * TILE_SIZE-scroll[1]))
                if tile == '0':
                    display.blit(floorTile_image, (x * TILE_SIZE-scroll[0], y * TILE_SIZE-scroll[1]))
                elif tile == '2' and not haventFought_1:
                    gameMap[y][x] = '0'

                if tile != '0':
                    tile_rects.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                x += 1
            y += 1


        display.blit(sign_image, (300-scroll[0],100-scroll[1]))
        signRect_1 = pygame.Rect(300,100, TILE_SIZE, TILE_SIZE)

        display.blit(sign_image, (640-scroll[0],200-scroll[1]))
        signRect_2 = pygame.Rect(640,200, TILE_SIZE, TILE_SIZE)


        #-----------------item pickups

        daggerRect = pygame.Rect(1000, 120, TILE_SIZE, TILE_SIZE)
        if haventPickedUpDagger:
            display.blit(dagger_image, (1000-scroll[0], 120-scroll[1]))

        if playerID.rect.colliderect(daggerRect) and 'dagger' not in playerID.items:
            haventPickedUpDagger = False
            #add dagger to inv
            playerID.items.append('dagger')

        firstHpPotionRect = pygame.Rect(200, 120, TILE_SIZE, TILE_SIZE)
        if haventPickedUpFirstHpPotion:
            display.blit(hpPotion_image, (200-scroll[0], 120-scroll[1]))

        if playerID.rect.colliderect(firstHpPotionRect) and 'hpPotion' not in playerID.items:
            haventPickedUpFirstHpPotion = False
            playerID.items.append('hpPotion')








        if haventFought_1:
            display.blit(enemy_image, (600-scroll[0], 50-scroll[1]))

        enemyUnit1 = enemy(100, 10, 20)
        enemyRect_1 = pygame.Rect(600,50, TILE_SIZE, TILE_SIZE)

        if playerID.rect.colliderect(signRect_1):
            display.blit(sign_text_intro, (332-scroll[0], 100-scroll[1]))

        if playerID.rect.colliderect(signRect_2) and haventFought_1:
            display.blit(sign_text_door, (640-scroll[0], 232-scroll[1]))

        if playerID.rect.colliderect(signRect_2) and not haventFought_1:
            display.blit(sign_text_door_win, (640-scroll[0], 232-scroll[1]))

        if playerID.rect.colliderect(enemyRect_1) and haventFought_1:
            movingUp = False
            movingDown = False
            movingLeft = False
            movingRight = False
            haventFought_1 = battleSequence(playerID, haventFought_1, enemyUnit1)


        #-----------------First Battle With dagger

        if haventFought_2:
            display.blit(enemy_image, (1400-scroll[0], 50-scroll[1]))


        enemyUnit2 = enemy(100, 10, 20)
        enemyRect_2 = pygame.Rect(1400, 50, TILE_SIZE, TILE_SIZE)


        if playerID.rect.colliderect(enemyRect_2) and haventFought_2:
            movingUp = False
            movingDown = False
            movingLeft = False
            movingRight = False
            haventFought_2 = battleSequence(playerID, haventFought_2, enemyUnit2)

        #------------enter portal
        if not haventFought_2:
            display.blit(portal_img, (1200-scroll[0], 200-scroll[1]))

        portalRect = pygame.Rect(1200, 200, 32, 64)
        if playerID.rect.colliderect(portalRect) and not haventFought_2:
            #------change player coordinates to new area
            display.blit(cutscene_image, (50, 70))
            delayTimer += dt
            if delayTimer >= 5:
                playerID.rect.x = 50
                playerID.rect.y = 600
        else:
            delayTimer = 0



        #-------TODO: add respawning enemies that give gold when killed, add a health pickup at the end of the room

        if haventFought_3:
            display.blit(enemy_image, (460-scroll[0], 580-scroll[1]))
        enemyUnit3 = enemy(110, 10, 23)
        enemyRect_3 = pygame.Rect(460, 580, TILE_SIZE, TILE_SIZE)
        if playerID.rect.colliderect(enemyRect_3) and haventFought_3:
            movingUp = False
            movingDown = False
            movingLeft = False
            movingRight = False
            haventFought_3 = battleSequence(playerID, haventFought_3, enemyUnit3)

        if haventFought_4:
            display.blit(enemy_image, (920-scroll[0], 765-scroll[1]))
        enemyUnit4 = enemy(110, 10, 25)
        enemyRect_4 = pygame.Rect(920, 765, TILE_SIZE, TILE_SIZE)
        if playerID.rect.colliderect(enemyRect_4) and haventFought_4:
            movingUp = False
            movingDown = False
            movingLeft = False
            movingRight = False
            haventFought_4 = battleSequence(playerID, haventFought_4, enemyUnit4)

        display.blit(merchant_image, (1144-scroll[0], 610-scroll[1]))
        merchantRect = pygame.Rect(1144, 610, TILE_SIZE, TILE_SIZE)
        if playerID.rect.colliderect(merchantRect):
            print('welcome to my shop!')




        #----------------movement-----------------------





        playerID.movement = [0,0]
        if currentAction == 'idle':
            playerID.movement[0] = 0
            playerID.movement[1] = 0
        if currentAction == 'movingLeft':
            playerID.movement[0] -= 2.2

        if currentAction == 'movingRight':
            playerID.movement[0] += 2.6

        elif currentAction == 'movingUp':
            playerID.movement[1] -= 1.7

        elif currentAction == 'movingDown':
            playerID.movement[1] += 2.2

        if playerID.movement[0] == 0 and playerID.movement[1] == 0:
            player_action, player_frame = change_action(player_action, player_frame, 'idle')

        if playerID.movement[1] > 0 :
            player_action, player_frame = change_action(player_action, player_frame, 'run')




        if playerID.movement[1] < 0:
            player_action, player_frame = change_action(player_action, player_frame, 'runBack')
        if playerID.movement[0] < 0:
            player_action, player_frame = change_action(player_action, player_frame, 'runLeft')
        if playerID.movement[0] > 0:
            player_action, player_frame = change_action(player_action, player_frame, 'runRight')




        playerID.rect, collisions = move(playerID.rect, playerID.movement, tile_rects)

        player_frame += 1
        if player_frame >= len(animation_database[player_action]):
            player_frame = 0
        player_img_id = animation_database[player_action][player_frame]
        player_image = animation_frames[player_img_id]

        display.blit(pygame.transform.flip(player_image, player_flip, False), (playerID.rect.x-scroll[0], playerID.rect.y-scroll[1]))




        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                print('keypress')
                validKeyPressed = False
                if event.key == K_a:
                    stack.append('movingLeft')
                    validKeyPressed = True
                if event.key == K_d:
                    stack.append('movingRight')
                    validKeyPressed = True
                if event.key == K_w:
                    stack.append('movingUp')
                    validKeyPressed = True
                if event.key == K_s:
                    stack.append('movingDown')
                    validKeyPressed = True
                if event.key == K_x:
                    stack.append('idle')
                    validKeyPressed = True
                if event.key == K_i:
                    inventory(playerID, display, WINDOW_SIZE, screen, clock)
                    stack.append('inInventory')
                    validKeyPressed = True
                if event.key == K_p:
                    pause(playerID)
                    stack.append('inPauseMenu')
                    validKeyPressed = True
                if validKeyPressed:
                    currentAction = stack.pop()
            elif event.type == pygame.KEYUP:
                keysPressed = pygame.key.get_pressed()
                if not keysPressed[K_a] and not keysPressed[K_s] and not keysPressed[K_w] and not keysPressed[K_d]:
                    print('happening')
                    stack.append('idle')
                    currentAction = stack.pop()







        surf = pygame.transform.scale(display, WINDOW_SIZE)
        screen.blit(surf, (0,0))
        pygame.display.update()
        dt = clock.tick(60) / 1000

#-----------------------MainBody of code

player = titleScreen()
overworld(player)
