import sys, asyncio,os
from pygame import mixer
import pygame.time, pygame
import pygame
from pygame.sprite import Sprite
import random
import math
cwd = os.getcwd()
print("Current working directory: {0}".format(cwd))
#setting
screen_width = 1600
screen_height = 900
#game setup
pygame.mixer.pre_init(30000,16,2,4500)
pygame.init()
mixer.init()
screen = pygame.display.set_mode((screen_width,screen_height))
clock = pygame.time.Clock()
#DIALOGUES,CHARACTERS,ENEMIES,ETC.,EVERYTHING ELSE----------------#
#player
class Player(Sprite):
    def __init__(self):
        super().__init__()
        #load img
        self.img = [pygame.image.load('mainChar4.png').convert_alpha(), pygame.image.load('mainChar5.png').convert_alpha(),
                    pygame.image.load('mainChar6.png').convert_alpha(), pygame.image.load('mainChar7.png').convert_alpha()]
        self.frame = 0
        self.frame2 = 2
        self.image = self.img[self.frame]
        #load on screen
        self.x_pos = screen_width//2
        self.y_pos = screen_height//2
        self.player = self.image.get_rect(topleft = (self.x_pos,self.y_pos))
        self.rect = self.player
        self.speed = 5
        self.fired = False
        self.bullet_group= pygame.sprite.Group()
        #animation
        self.update_animTime = pygame.time.get_ticks()
        self.anim_cd = 200
        self.run_anim_cd = 100
        self.gotHit_CD = 0
        self.invincible = False
        #dmg anim
        self.imgCopy = self.image.copy()
        self.imgCopy.fill("red",special_flags=pygame.BLEND_RGBA_MULT)
        self.dmgAnim = False
        self.dmgAnimCD = 0
        #"health" for Lvl 1
        self.dmg = 600
        self.bossDmg = 7850
        self.dues = 10000
        self.IRSdues = 100000
        # "health" for Lvl 2
        self.lvl2_dmg = 1
        self.health = 10
        self.TrashTakenOut = 10
        #"health" for lvl 3
        self.scaleHeartsTo = 200
        self.hearts = 0
        self.heartImg = pygame.image.load("heart0.png").convert_alpha()
        self.heartImg = pygame.transform.scale(self.heartImg,(self.scaleHeartsTo,self.scaleHeartsTo)).convert_alpha()
        self.heartRows = screen_width/self.scaleHeartsTo
        #health for lvl2 Boss
        self.lvl2_hearts = 10
        #health for lvl3 Boss
        self.life = 10

    def get_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.player.right += self.speed
        if keys[pygame.K_a]:
            self.player.left -=self.speed
        if keys[pygame.K_w]:
            self.player.bottom -=self.speed
        if keys[pygame.K_s]:
            self.player.top +=self.speed

    def shoot(self):
        if pygame.mouse.get_pressed()[0] and self.fired == False:
            self.fired= True
            bullet = Bullet(self.player)
            self.bullet_group.add(bullet)
        if pygame.mouse.get_pressed()[0] == False:
            self.fired= False

    def update(self, screen,enemy):
        self.bullet_group.update()
        self.bullet_group.draw(screen)
        #animate
        if pygame.time.get_ticks() - self.update_animTime > self.anim_cd:
            self.update_animTime = pygame.time.get_ticks()
            self.animate()
        #collisions, health,dmg anim
        gets_hit = pygame.sprite.spritecollide(self, enemy.enemy_group,True)
        if gets_hit and self.dmgAnim == False:
            self.dues -=self.dmg
            self.dmgAnim = True
        if self.dmgAnim == True:
            if self.dmgAnimCD <= 50:
                screen.blit(self.imgCopy,self.player)
                self.dmgAnimCD +=1
            elif self.dmgAnimCD > 50:
                self.dmgAnim = False
                screen.blit(self.image, self.player)
        else:
            self.dmgAnimCD = 0
            screen.blit(self.image, self.player)
        #boundaries
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.right >= screen_width:
            self.rect.right = screen_width
        if self.rect.bottom >= screen_height:
            self.rect.bottom = screen_height

        #display health
        text_size = 30
        font = pygame.font.Font("PressStart2P.ttf", text_size)
        text = "$" + str(self.dues)
        text_render = font.render(text, False, "Black")
        width, height = font.size(text)
        screen.blit(text_render,(screen_width//2-width//2,20))
    #LVL 2 ENEMY
    def updateForLvl2Enemy(self, screen,enemy,trails):
        self.image = self.img[self.frame2].convert_alpha()
        self.bullet_group.update()
        self.bullet_group.draw(screen)
        #animate
        if pygame.time.get_ticks() - self.update_animTime > self.anim_cd:
            self.update_animTime = pygame.time.get_ticks()
            self.animate2()
        #collisions, health,dmg anim
        gets_hit = pygame.sprite.spritecollide(self, enemy.enemy_group,True)
        gets_hit_OtherEnemy = pygame.sprite.spritecollide(self, enemy.enemy_group2,True)
        gets_hitByTrail = pygame.sprite.spritecollide(self, trails, True)
        if gets_hit and self.dmgAnim == False or gets_hit_OtherEnemy and self.dmgAnim == False:
            self.TrashTakenOut -=self.lvl2_dmg
            self.dmgAnim = True
        if gets_hitByTrail and self.dmgAnim == False:
            self.health -=1
            self.dmgAnim = True
        if self.dmgAnim == True:
            imgCopy = self.image.copy().convert_alpha()
            imgCopy.fill("red", special_flags=pygame.BLEND_RGBA_MULT)
            if self.dmgAnimCD <= 50:
                screen.blit(imgCopy,self.player)
                self.dmgAnimCD +=1
            elif self.dmgAnimCD > 50:
                self.dmgAnim = False
                self.dmgAnimCD = 0
                screen.blit(self.image, self.player)
        elif self.dmgAnim ==False:
            screen.blit(self.image, self.player)
        #display health & stats
        for i in range(1,self.TrashTakenOut):
            self.TrashImg = pygame.transform.scale(pygame.image.load("RedTrash5.png"), (30, 30)).convert_alpha()
            screen.blit(self.TrashImg, (30 * i, 30))
        for i in range(1,self.health + 1):
            self.heartImg = pygame.transform.scale(self.heartImg,(30,30)).convert_alpha()
            screen.blit(self.heartImg,(30 * i,65))
        #boundaries
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.right >= screen_width:
            self.rect.right = screen_width
        if self.rect.bottom >= screen_height:
            self.rect.bottom = screen_height

    def updateForLvl3Enemy(self, screen,enemy):
        self.image = self.img[self.frame2].convert_alpha()
        self.bullet_group.update()
        self.bullet_group.draw(screen)
        # boundaries
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.right >= screen_width:
            self.rect.right = screen_width
        if self.rect.bottom >= screen_height:
            self.rect.bottom = screen_height
        #animate
        if pygame.time.get_ticks() - self.update_animTime > self.anim_cd:
            self.update_animTime = pygame.time.get_ticks()
            self.animate2()
        #collisions, health,dmg anim
        gets_hit = pygame.sprite.spritecollide(self, enemy.enemy_group,True)
        gets_hitBy_Bullet = pygame.sprite.spritecollide(self, enemy.enemy_bullet_group,True)
        # gets_hitByTrail = pygame.sprite.spritecollide(self, trails, True)
        if gets_hit and self.dmgAnim == False or gets_hitBy_Bullet and self.dmgAnim == False:
            self.hearts += 1
            self.dmgAnim = True
        if self.dmgAnim == True:
            imgCopy = self.image.copy().convert_alpha()
            imgCopy.fill("red", special_flags=pygame.BLEND_RGBA_MULT)
            if self.dmgAnimCD <= 50:
                screen.blit(imgCopy,self.player)
                self.dmgAnimCD +=1
            elif self.dmgAnimCD > 50:
                self.dmgAnim = False
                self.dmgAnimCD = 0
                screen.blit(self.image, self.player)
        elif self.dmgAnim ==False:
            screen.blit(self.image, self.player)
        # #display hearts
        if self.hearts > 0:
            for h in range(self.hearts):
                screen.blit(self.heartImg,(self.heartImg.get_width() * (h%self.heartRows),(h//self.heartRows) * self.heartImg.get_height()))

    #BOSS
    def updateForBoss(self, screen,enemy):
        # boundaries
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.right >= screen_width:
            self.rect.right = screen_width
        if self.rect.bottom >= screen_height:
            self.rect.bottom = screen_height
        self.image = self.img[self.frame2].convert_alpha()
        self.bullet_group.update()
        self.bullet_group.draw(screen)
        #animate player
        if pygame.time.get_ticks() - self.update_animTime > self.run_anim_cd:
            self.update_animTime = pygame.time.get_ticks()
            self.animate2()
        #collisions, health, damage animation
        gets_hit = pygame.Rect.colliderect(self.rect, enemy.rect)
        hitByBullet = pygame.sprite.spritecollide(self,enemy.boss_bullet,True)
        if hitByBullet and self.invincible == False:
            self.invincible = True
            self.IRSdues -=self.bossDmg
            if self.invincible == True:
                imgCopy = self.image.copy().convert_alpha()
                imgCopy.fill("red", special_flags=pygame.BLEND_RGBA_MULT)
                if self.gotHit_CD >= 100:
                    self.gotHit_CD = 0
                    self.invincible = False
                else:
                    screen.blit(imgCopy, self.player)

        else:
            screen.blit(self.image, self.player)
        if gets_hit and self.invincible == False:
            self.IRSdues -= self.bossDmg
            self.invincible = True
        if self.invincible == True:
            imgCopy = self.image.copy().convert_alpha()
            imgCopy.fill("red", special_flags=pygame.BLEND_RGBA_MULT)
            if self.gotHit_CD >= 100:
                self.gotHit_CD = 0
                self.invincible = False
            else:
                screen.blit(imgCopy, self.player)
            self.gotHit_CD += 1
        #display health
        text_size = 30
        font = pygame.font.Font("PressStart2P.ttf", text_size)
        text = "$" + str(self.IRSdues)
        text_render = font.render(text, False, "Black")
        width, height = font.size(text)
        screen.blit(text_render,(screen_width//2-width//2,20))
    #BOSS 2:
    def updateForBoss2(self, screen,enemy,trails):
        self.image = self.img[self.frame2].convert_alpha()
        self.bullet_group.update()
        self.bullet_group.draw(screen)
        # boundaries
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.right >= screen_width:
            self.rect.right = screen_width
        if self.rect.bottom >= screen_height:
            self.rect.bottom = screen_height
        #animate player
        if pygame.time.get_ticks() - self.update_animTime > self.run_anim_cd:
            self.update_animTime = pygame.time.get_ticks()
            self.animate2()
        #collisions, health, damage animation
        gets_hit = pygame.Rect.colliderect(self.rect, enemy.rect)
        if gets_hit:
            imgCopy = self.image.copy().convert_alpha()
            imgCopy.fill("red", special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(imgCopy, self.player)
        else:
            screen.blit(self.image, self.player)
        if gets_hit and self.invincible == False:
            self.lvl2_hearts -= 1
            self.invincible = True
        if self.invincible == True:
            if self.gotHit_CD >= 100:
                self.gotHit_CD = 0
                self.invincible = False
            self.gotHit_CD +=1
        if len(trails) == 0:
            for i in range(1,self.lvl2_hearts + 1):
                heartImg = pygame.transform.scale(pygame.image.load("heart0.png").convert_alpha(), (40, 40))
                screen.blit(heartImg,(heartImg.get_width()* i,20))

    def updateForLvl3Boss(self, screen,enemy):
        self.image = self.img[self.frame2].convert_alpha()
        self.bullet_group.update()
        self.bullet_group.draw(screen)
        # boundaries
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.right >= screen_width:
            self.rect.right = screen_width
        if self.rect.bottom >= screen_height:
            self.rect.bottom = screen_height
        #animate
        if pygame.time.get_ticks() - self.update_animTime > self.anim_cd:
            self.update_animTime = pygame.time.get_ticks()
            self.animate2()
        #collisions, health,dmg anim
        gets_hitBy_Bullet = pygame.sprite.spritecollide(self, enemy.boss_bullet,True)
        gets_hitBy_SecondBullet = pygame.sprite.spritecollide(self, enemy.second_bullet,True)
        gets_hitBy_projectiles = pygame.sprite.spritecollide(self,enemy.projectile_group,True)
        if gets_hitBy_Bullet and self.dmgAnim == False or gets_hitBy_SecondBullet and self.dmgAnim == False or gets_hitBy_projectiles and self.dmgAnim == False:
            self.life -= 1
            self.dmgAnim = True
        if self.dmgAnim == True:
            imgCopy = self.image.copy().convert_alpha()
            imgCopy.fill("red", special_flags=pygame.BLEND_RGBA_MULT)
            if self.dmgAnimCD <= 50:
                screen.blit(imgCopy,self.player)
                self.dmgAnimCD +=1
            elif self.dmgAnimCD > 50:
                self.dmgAnim = False
                self.dmgAnimCD = 0
                screen.blit(self.image, self.player)
        elif self.dmgAnim ==False:
            screen.blit(self.image, self.player)
        # #display hearts
        for h in range(1,self.life+1):
            self.heartImg = pygame.transform.scale(self.heartImg,(30,30))
            screen.blit(self.heartImg,(self.heartImg.get_width() * h,10))

    #Main Character frames for certain scenes
    def animate(self):
        if self.frame == 0:
            self.frame = 1
            self.image = self.img[self.frame].convert_alpha()
        else:
            self.frame = 0
            self.image = self.img[self.frame].convert_alpha()
    def animate2(self):
        if self.frame2 == 2:
            self.frame2 = 3
            self.image = self.img[self.frame2].convert_alpha()
        else:
            self.frame2 = 2
            self.image = self.img[self.frame2].convert_alpha()

class Bullet(Sprite):
    def __init__(self,player_pos):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.player_pos = player_pos
        self.rect = self.image.get_rect(midleft=(self.player_pos.midleft[0],self.player_pos.midleft[1]))
        self.pos = pygame.mouse.get_pos()
        self.x_dist = self.pos[0] - self.player_pos.midleft[0]
        self.y_dist = self.pos[1] - self.player_pos.midleft[1]
        self.rad = math.atan2(self.y_dist, self.x_dist)
        self.dx = math.cos(self.rad)
        self.dy = math.sin(self.rad)
        self.bullet_speed = 12

    def update(self):
        self.rect.left += self.dx * self.bullet_speed
        self.rect.top += self.dy * self.bullet_speed
        if self.rect.right < 0 or self.rect.top > screen_height or self.rect.bottom < 0 or self.rect.left > screen_width:
            self.kill()

#game over
class gameOverDialogues:
    def __init__(self):
        # animation
        self.update_text_time = pygame.time.get_ticks()
        self.anim_cd = 30
        # text
        self.curr_t = 0
        self.currentText = ""
        self.curr_letter = 1
        self.dialogues = ["Whatchu tryna do..?","Be responsible???"]
        # next text
        self.next_text_cd = 0
        self.finish_dialog = False

    def DialogAnim(self, screen):
        # key press
        self.keys = pygame.key.get_pressed()
        # text
        text_size = 30
        font = pygame.font.Font("PressStart2P.ttf", text_size)
        text = self.dialogues[self.curr_t]
        self.currentText = text
        text = text[:self.curr_letter]
        text_render = font.render(text, False, "Black")
        width, height = font.size(text)
        # animation
        if pygame.time.get_ticks() - self.update_text_time > self.anim_cd:
            self.update_text_time = pygame.time.get_ticks()
            self.curr_letter += 1
        # next text
        if self.keys[pygame.K_SPACE]:
            if self.curr_t == len(self.dialogues) - 1:
                if self.next_text_cd > 300:
                    self.finish_dialog = True
            elif self.next_text_cd > 300:
                self.curr_letter = 1
                self.curr_t += 1
                self.next_text_cd = 0
        self.next_text_cd += 10
        screen.blit(text_render, (screen_width // 2 - width // 2, screen_height // 2 - height // 2))



#SCENES---#
class Texts():
    def __init__(self):
        self.update_text_time = pygame.time.get_ticks()
        self.anim_cd = 10
        self.curr_letter = 1
        self.howToPlayTexts = ["How to Play","A young man wants to stay true to himself,", "but is constantly pressured by society",
                "to change and conform.","A,W,S,D keys: to move", "Mouse Left-Click: to shoot","Your only weapon? Sheer willpower.", "Good luck!"]
        #next screen
        self.next_screen_cd = 0
        self.next_screen = False

    def display_Title(self,screen):
        text_size = 60
        font = pygame.font.Font("PressStart2P.ttf", text_size)
        t = "Only DownHill From Here"
        text = font.render(t, False, "White")
        width, height = font.size(t)
        screen.blit(text, (screen_width//2 - (width//2), screen_height//6))

    def P2Play(self,screen):
        text_size = 52
        font = pygame.font.Font("PressStart2P.ttf", text_size)
        t = "Press Space to Navigate"
        text = font.render(t, False, "White")
        width, height = font.size(t)
        screen.blit(text, (screen_width // 2 - (width // 2), screen_height - height - 50))

    def howToPlay(self,screen):
        screen.fill("white")
        text_size = 30
        font = pygame.font.Font("PressStart2P.ttf", text_size)
        keys = pygame.key.get_pressed()
        for i,t in enumerate(self.howToPlayTexts):
            padding = 30
            if i == len(self.howToPlayTexts)-1:
                padding = 50
            text = self.howToPlayTexts[i]
            text = text[:self.curr_letter]
            text_render = font.render(text, False, "Black")
            screen.blit(text_render, (250,screen_height//4 - (-(text_size + padding) * i)))
        #text anim
        if pygame.time.get_ticks() - self.update_text_time > self.anim_cd:
            self.update_text_time = pygame.time.get_ticks()
            self.curr_letter += 1
        #next screen
        if keys[pygame.K_SPACE]:
            if self.next_screen_cd > 600:
                self.next_screen = True
        self.next_screen_cd += 10

class main_char():
    def __init__(self):
        self.spriteSheet_img = pygame.image.load('main char.png')
        self.update_time = pygame.time.get_ticks()
        self.frame_size = 180
        self.anim_cd = 700
        self.frame = 0
        self.x_pos = screen_width//2 -(self.frame_size//2)
        self.y_pos = screen_height//2 - (self.frame_size//2)

    def animate(self,screen):
        screen.blit(self.spriteSheet_img,(self.x_pos,self.y_pos),(self.frame,0,self.frame_size,self.frame_size))
        if pygame.time.get_ticks() - self.update_time > self.anim_cd:
            self.update_time = pygame.time.get_ticks()
            if self.frame == 0:
                self.frame = self.frame_size
            elif self.frame == self.frame_size:
                self.frame =0

class banker_boss():
    def __init__(self):
        self.spriteSheet_img = pygame.image.load('Banker Boss.png')
        self.update_time = pygame.time.get_ticks()
        self.anim_cd = 600
        self.frame = 0
        self.frame_size = 190
        self.x_pos = screen_width//2 + 300
        self.y_pos = screen_height // 2 - (self.frame_size//2)
    def animate(self,screen):
        screen.blit(self.spriteSheet_img,(self.x_pos,self.y_pos),(self.frame,0,self.frame_size,self.frame_size))
        if pygame.time.get_ticks() - self.update_time > self.anim_cd:
            self.update_time = pygame.time.get_ticks()
            if self.frame == 0:
                self.frame = self.frame_size
            elif self.frame == self.frame_size:
                self.frame =0


class Mom():
    def __init__(self):
        self.spriteSheet_img = pygame.image.load('mom_crying.png')
        self.update_time = pygame.time.get_ticks()
        self.frame_size = 180
        self.anim_cd = 200
        self.frame = 0
        self.x_pos = screen_width // 2 - (300 + self.frame_size)
        self.y_pos = screen_height // 2 - (self.frame_size // 2)

    def animate(self, screen):
        screen.blit(self.spriteSheet_img, (self.x_pos, self.y_pos), (self.frame, 0, self.frame_size, self.frame_size))
        if pygame.time.get_ticks() - self.update_time > self.anim_cd:
            self.update_time = pygame.time.get_ticks()
            if self.frame == 0:
                self.frame = self.frame_size
            elif self.frame == self.frame_size:
                self.frame = 0
#pre-level 1 scene
class lvl1_Texts:
    def __init__(self,padding):
        #animation
        self.update_text_time = pygame.time.get_ticks()
        self.anim_cd = 45
        # text
        self.curr_t = 0
        self.currentText = ""
        self.curr_letter = 1
        self.mainChar_Texts = ["Another day to be lazy..." , "Hehe...", "(Looks at bank account)" ,
                               "THOUSANDS of dollars due today,", "but still not gonna pay for it!" , "Hehehehe..." ,
                               "You have so much money due today,","and you're not gonna pay it??????","What are you, nuts?????",
                               "Nahhh....No paying today." , "All this responsibility is makin' me sleepy...","Zzzzzzzzzzzzzzzzzzzzzzzz",
                               "Hey!!!!..........","The credit card desperately urges him to pay.","Looks like it's taking matters to its own hands!",
                               "This man ain't tryna pay though. He tryna sleep!!!"]
        self.dialog_box = pygame.Surface((screen_width - padding,250))
        self.dialog_box.fill("white")
        # next text
        self.next_text_cd = 0
        self.finish_dialog = False

    def mainChar_dialogue(self, screen):
        self.keys = pygame.key.get_pressed()
        text_size = 30
        font = pygame.font.Font("PressStart2P.ttf", text_size)
        #text
        text = self.mainChar_Texts[self.curr_t]
        self.currentText = text
        text = text[:self.curr_letter]
        text_render = font.render(text, False, "Black")
        width, height = font.size(text)
        screen.blit(text_render, (screen_width // 2 - (width // 2), screen_height - 200))
        # text anim
        if pygame.time.get_ticks() - self.update_text_time > self.anim_cd:
            self.update_text_time = pygame.time.get_ticks()
            self.curr_letter += 1
        # next text
        if self.keys[pygame.K_SPACE]:
            if self.curr_t == len(self.mainChar_Texts)-1:
                self.curr_letter = 1
                if self.next_text_cd > 300:
                    self.finish_dialog = True
            elif self.next_text_cd > 300:
                self.curr_letter = 1
                self.curr_t += 1
                self.next_text_cd = 0
        self.next_text_cd += 10

class Lvl1_main_char:
    def __init__(self):
        #load img
        self.spriteSheet_img = pygame.image.load('main char.png')
        self.imgScaleTo = 500
        self.totalFrames = 4
        self.spriteSheet_img = pygame.transform.scale(self.spriteSheet_img,(self.imgScaleTo,self.imgScaleTo//2 * self.totalFrames))
        #animation
        self.update_time = pygame.time.get_ticks()
        self.frame_size = self.imgScaleTo/2
        self.curr_y = self.frame_size
        self.anim_cd = 100
        self.frame = 0
        #load on screen
        self.x_pos = screen_width // 2 - (self.frame_size // 2)
        self.y_pos = screen_height // 2 - (self.frame_size // 2)
        #dialogue
        self.padding_dialog_box = 50
        self.text = lvl1_Texts(self.padding_dialog_box)
        self.dialogue_box = self.text.dialog_box
        self.lvl1_txts = lvl1_Texts(0)
        self.card = card()

    def animate(self, screen):
        if self.lvl1_txts.curr_t >= 11:
            self.anim_cd = 150
            self.curr_y = self.frame_size * 2
        screen.blit(self.spriteSheet_img, (self.x_pos, self.y_pos),
                    (self.frame, self.curr_y, self.frame_size, self.frame_size))
        screen.blit(self.dialogue_box,(screen_width-self.dialogue_box.get_width()-self.padding_dialog_box//2,
                                       screen_height-self.dialogue_box.get_height()-self.padding_dialog_box))
        if pygame.time.get_ticks() - self.update_time > self.anim_cd:
            self.update_time = pygame.time.get_ticks()
            if self.lvl1_txts.curr_t < 6 or self.lvl1_txts.curr_t > 8 and self.lvl1_txts.curr_t < 12:
                if self.lvl1_txts.curr_letter >= len(self.lvl1_txts.currentText):
                    self.frame = 0
                elif self.frame == 0:
                    self.frame = self.frame_size
                elif self.frame == self.frame_size:
                    self.frame = 0
        self.lvl1_txts.mainChar_dialogue(screen)
        self.card.animate(screen,self.lvl1_txts)

class card():
    def __init__(self):
        self.spriteSheet_img = pygame.image.load('card.png')
        self.imgScaleTo = 500
        self.spriteSheet_img = pygame.transform.scale(self.spriteSheet_img,(self.imgScaleTo,self.imgScaleTo))
        self.update_CardTime = pygame.time.get_ticks()
        self.frame_size = self.imgScaleTo/2
        self.anim_cd = 120
        self.frame = 0
        self.x_pos = screen_width // 2 - (self.frame_size // 2) - 300
        self.y_pos = screen_height // 2 - (self.frame_size // 2)
        self.curr_y = 0

    def animate(self, screen,curr_dialog):
        if curr_dialog.curr_t >=6:
            if curr_dialog.curr_t == 12:
                self.curr_y = self.frame_size
            screen.blit(self.spriteSheet_img, (self.x_pos, self.y_pos), (self.frame, self.curr_y, self.frame_size, self.frame_size))
        if pygame.time.get_ticks() - self.update_CardTime > self.anim_cd:
            self.update_CardTime = pygame.time.get_ticks()
            if curr_dialog.curr_t >=6 and curr_dialog.curr_t <=8 or curr_dialog.curr_t ==12:
                if curr_dialog.curr_letter >= len(curr_dialog.currentText):
                    self.frame = 0
                elif self.frame == 0:
                    self.frame = self.frame_size
                elif self.frame == self.frame_size:
                    self.frame = 0
#prelvl1 boss
class Dialogues:
    def __init__(self):
        # animation
        self.update_text_time = pygame.time.get_ticks()
        self.anim_cd = 45
        # text
        self.curr_t = 0
        self.currentText = ""
        self.curr_letter = 1
        self.dialogues = ["1 Year Later...","(Wakes up.....)","HOLY -. I've been asleep for a whole year???",
                          "I slept GOOD!","Like a teddy bear in hibernation..","(Knock knock knock)","This is the IRS!!",
                          "You're past overdue for $100,000!!!","Pay up!!!","(no response......)",
                          "The IRS agent is impatient and kicks down the door."]
        # next text
        self.next_text_cd = 0
        self.finish_dialog = False

    def displayTexts(self,screen):
        #key press
        self.keys = pygame.key.get_pressed()
        #text
        text_size = 30
        font = pygame.font.Font("PressStart2P.ttf", text_size)
        text = self.dialogues[self.curr_t]
        self.currentText = text
        text = text[:self.curr_letter]
        text_render = font.render(text, False, "Black")
        width, height = font.size(text)
        textHeight = screen_height//2 - height//2
        #animation
        if pygame.time.get_ticks() - self.update_text_time > self.anim_cd:
            self.update_text_time = pygame.time.get_ticks()
            self.curr_letter += 1
        # next text
        if self.keys[pygame.K_SPACE]:
            if self.curr_t == len(self.dialogues)-1:
                self.curr_letter = 1
                if self.next_text_cd > 300:
                    self.finish_dialog = True
            elif self.next_text_cd > 300:
                self.curr_letter = 1
                self.curr_t += 1
                self.next_text_cd = 0
        self.next_text_cd += 10
        if self.curr_t ==0:
            screen.blit(text_render,(screen_width//2 - width//2,textHeight))
        elif self.curr_t > 0:
            screen.blit(text_render, (screen_width // 2 - width // 2, screen_height - height - 100))

class charAnims():
    def __init__(self):
        # main char
        self.imgScaleTo = 500
        self.frame_size = self.imgScaleTo//2
        self.selected_anim = 2
        self.curr_anims = (self.imgScaleTo//2) * 4
        self.spriteSheet_img2 = pygame.image.load('main char.png')
        self.spriteSheet_img2 = pygame.transform.scale(self.spriteSheet_img2,
                                                       (self.imgScaleTo, self.curr_anims))
        # main char anim
        self.update_time = pygame.time.get_ticks()
        self.frame_size = self.imgScaleTo / 2
        self.curr_x = 0
        self.anim_cd = 500
        self.talk_animCD = 100
        self.chosen_cd = self.anim_cd
        self.frame = 0
        self.x_pos = screen_width // 2 - (self.frame_size // 2)
        self.y_pos = screen_height // 2 - (self.frame_size // 2)

        #BOSS
        self.selected_anim2 = 0
        self.imgScaleTo2 = 700
        self.curr_anims2 = (self.imgScaleTo2 // 2) * 2
        self.spriteSheet_img = pygame.image.load('Banker Boss.png')
        self.spriteSheet_img = pygame.transform.scale(self.spriteSheet_img,(self.imgScaleTo2, self.curr_anims2))
        # boss animation
        self.frame_size2 = self.imgScaleTo2 / 2
        self.curr_x2 = 0
        self.frame = 0
        # boss load on screen
        self.x_pos2 = screen_width // 2 - (self.frame_size // 2) - 400
        self.y_pos2 = screen_height // 2 - (self.frame_size // 2)

    def animate(self,screen,curr_dial):
        #MAIN CHAR
        if curr_dial.curr_t ==1:
            screen.blit(self.spriteSheet_img2, (self.x_pos, self.y_pos),
                        (self.curr_x,self.frame_size * self.selected_anim, self.frame_size,self.frame_size))
        if curr_dial.curr_t >1 and curr_dial.curr_t < 5:
            self.chosen_cd = self.talk_animCD
            self.selected_anim = 1
            screen.blit(self.spriteSheet_img2, (self.x_pos, self.y_pos),
                        (self.curr_x, self.frame_size * self.selected_anim, self.frame_size, self.frame_size))
            if pygame.time.get_ticks() - self.update_time > self.chosen_cd:
                if curr_dial.curr_letter >= len(curr_dial.currentText):
                    self.curr_x = 0
                elif self.curr_x == 0:
                    self.curr_x = self.frame_size
                elif self.curr_x == self.frame_size:
                    self.curr_x = 0
                self.update_time = pygame.time.get_ticks()
        elif  curr_dial.curr_t >= 5 and curr_dial.curr_t <= 8:
            self.curr_x = 0
            screen.blit(self.spriteSheet_img2, (self.x_pos, self.y_pos),
                        (self.curr_x, self.frame_size * self.selected_anim, self.frame_size, self.frame_size))
            # BOSS
            screen.blit(self.spriteSheet_img, (self.x_pos2, self.y_pos2),
                        (self.curr_x2, self.frame_size2 * self.selected_anim2, self.frame_size2, self.frame_size2))
            if pygame.time.get_ticks() - self.update_time > self.chosen_cd:
                if curr_dial.curr_letter >= len(curr_dial.currentText):
                    self.curr_x2 = 0
                elif self.curr_x2 == 0:
                    self.curr_x2 = self.frame_size2
                elif self.curr_x2 == self.frame_size2:
                    self.curr_x2 = 0
                self.update_time = pygame.time.get_ticks()
        elif curr_dial.curr_t > 8:
            self.curr_x = 0
            self.curr_x2 = 0
            screen.blit(self.spriteSheet_img2, (self.x_pos, self.y_pos),
                        (self.curr_x, self.frame_size * self.selected_anim, self.frame_size, self.frame_size))
            # BOSS
            screen.blit(self.spriteSheet_img, (self.x_pos2, self.y_pos2),
                        (self.curr_x2, self.frame_size2 * self.selected_anim2, self.frame_size2, self.frame_size2))

#prelvl2 scene
class preLvl2Dialogues:
    def __init__(self):
        # animation
        self.update_text_time = pygame.time.get_ticks()
        self.anim_cd = 30
        # text
        self.curr_t = 0
        self.currentText = ""
        self.curr_letter = 1
        self.dialogues = ["Hehe..Ain't nobody paying...Hehe...","(He travels to an unknown place)",
                          "(where the IRS won't bother him ever again...)",#3 >>
                          "Month 1","Month 2","Month 3","Month 4",
                          "Month 5","Month 6","Month 7",#10 >>
                          "Pheeee -yew! Oh man, it stinks in here!","......","Oh well.",
                          "Ayyooo! Yo room stinkin' right now!","Take us out to the dumpsters, man!","He's not gonna listen....",
                          "There's only one way to handle this....","We do it ourselves!!!!","An angry trash mob forms..","..even THEY are tired of the smell."]
        # next text
        self.next_text_cd = 0
        self.finish_dialog = False
        #Characters
        self.RedTrashTalkImgs = [pygame.image.load('RedTrash1.png'),pygame.image.load('RedTrash2.png')]
        self.RedTrashIdleImgs = [pygame.image.load('RedTrash3.png'),pygame.image.load('RedTrash4.png')]
        self.RedBagImgs = [pygame.image.load('RedTrash5.png'), pygame.image.load('RedTrash6.png')]
        self.BlueTrashTalkImgs = [pygame.image.load('BlueTrash3.png'), pygame.image.load('BlueTrash4.png')]
        self.BlueTrashIdleImgs = [pygame.image.load('BlueTrash1.png'), pygame.image.load('BlueTrash2.png')]
        self.BlueBagImgs = [pygame.image.load('BlueTrash5.png'), pygame.image.load('BlueTrash6.png')]
        self.mainChar = [pygame.image.load('mainChar2.png'),pygame.image.load('mainChar3.png')]
        #Character Animation Settings
        self.scalemainCharImgTo = 330
        self.mainCharCurrFrame = 0
        self.mainCharCurrImg = self.mainChar[self.mainCharCurrFrame]
        self.mainCharCurrImg = pygame.transform.scale(self.mainCharCurrImg,(self.scalemainCharImgTo,self.scalemainCharImgTo))
        self.updateMainCharTalkTime = pygame.time.get_ticks()
        self.mainCharTalkAnim_cd = 120
        #Trash Animation Settings
            #red
        self.scaleTrashImgTo = 140
        self.RedTrashCurrFrame = 0
        self.RedTrashCurrImg = self.RedBagImgs[self.RedTrashCurrFrame]
        self.RedTrashCurrImg = pygame.transform.scale(self.RedTrashCurrImg,(self.scaleTrashImgTo,self.scaleTrashImgTo))
        self.RedupdateTrashTime = pygame.time.get_ticks()
        self.RedTrashAnim_cd = 260
            #red talking
        self.RedTalkCurrFrame = 0
        self.RedTalkingCurrImg = self.RedTrashTalkImgs[self.RedTalkCurrFrame]
        self.RedupdateTrashTalkTime = pygame.time.get_ticks()
        self.RedTrashAnim_cd = 130
            #blue
        self.BlueTrashCurrFrame = 0
        self.BlueTrashCurrImg = self.BlueBagImgs[self.BlueTrashCurrFrame]
        self.BlueTrashAnim_cd = 600
        self.BlueupdateTrashTime = pygame.time.get_ticks()
            #blue talking
        self.BlueTalkCurrFrame = 0
        self.BlueTalkingCurrImg = self.BlueTrashTalkImgs[self.BlueTalkCurrFrame]
        self.BlueupdateTrashTalkTime = pygame.time.get_ticks()
        self.BlueTrashAnim_cd = 130
    def DialogAnim(self,screen):
            # key press
            self.keys = pygame.key.get_pressed()
            # text
            text_size = 30
            font = pygame.font.Font("PressStart2P.ttf", text_size)
            text = self.dialogues[self.curr_t]
            self.currentText = text
            text = text[:self.curr_letter]
            text_render = font.render(text, False, "Black")
            width, height = font.size(text)
            # animation
            if pygame.time.get_ticks() - self.update_text_time > self.anim_cd:
                self.update_text_time = pygame.time.get_ticks()
                self.curr_letter += 1
            # next text
            if self.keys[pygame.K_SPACE]:
                if self.curr_t == len(self.dialogues) - 1:
                    if self.next_text_cd > 300:
                        self.finish_dialog = True
                elif self.next_text_cd > 300:
                    self.curr_letter = 1
                    self.curr_t += 1
                    self.next_text_cd = 0
            self.next_text_cd += 10
            screen.blit(text_render,(screen_width//2-width//2,200))
            #Character Cues
            #main char
            if pygame.time.get_ticks() - self.updateMainCharTalkTime > self.mainCharTalkAnim_cd:
                if self.curr_t == 0 or self.curr_t >10 and self.curr_t<=12:
                    if self.curr_letter >= len(self.dialogues[self.curr_t]):
                        pass
                    else:
                        self.animateMainChar()
                        self.updateMainCharTalkTime = pygame.time.get_ticks()
            screen.blit(self.mainCharCurrImg ,(screen_width//2-self.mainCharCurrImg .get_width()//2,screen_height//2-self.mainCharCurrImg .get_height()//2))
            #Trash bags
            #red bags animation
            if self.curr_t >= 3 and self.curr_t <= 9:
                if pygame.time.get_ticks() - self.RedupdateTrashTime > self.RedTrashAnim_cd:
                    self.animateRedTrashBag()
                    self.RedupdateTrashTime = pygame.time.get_ticks()
                if pygame.time.get_ticks() - self.BlueupdateTrashTime > self.BlueTrashAnim_cd:
                    self.animateBlueTrashBag()
                    self.BlueupdateTrashTime = pygame.time.get_ticks()
                for i in range(1,self.curr_t - 1):
                    if i % 2 == 1:
                        screen.blit(self.RedTrashCurrImg ,(i * 85,screen_height//2+self.mainCharCurrImg.get_height()//2 - self.RedTrashCurrImg.get_height()))
                    if i % 2 == 0:
                        screen.blit(self.BlueTrashCurrImg, (i * 85,
                                                           screen_height // 2 + self.mainCharCurrImg.get_height() // 2 - self.RedTrashCurrImg.get_height()))
            #Talking Bags Come In
            if self.curr_t >= 10:
                #no dialogue bags
                if pygame.time.get_ticks() - self.RedupdateTrashTime > self.RedTrashAnim_cd:
                    self.animateRedTrashBag()
                    self.RedupdateTrashTime = pygame.time.get_ticks()
                if pygame.time.get_ticks() - self.BlueupdateTrashTime > self.BlueTrashAnim_cd:
                    self.animateBlueTrashBag()
                    self.BlueupdateTrashTime = pygame.time.get_ticks()
                for i in range(1,8):
                    if i % 2 == 1:
                        screen.blit(self.RedTrashCurrImg ,(i * 85,screen_height//2+self.mainCharCurrImg.get_height()//2 - self.RedTrashCurrImg.get_height()))
                    if i % 2 == 0:
                        screen.blit(self.BlueTrashCurrImg, (i * 85,
                                                           screen_height // 2 + self.mainCharCurrImg.get_height() // 2 - self.RedTrashCurrImg.get_height()))
                #Talking Red Bag
                if pygame.time.get_ticks() - self.RedupdateTrashTalkTime > self.RedTrashAnim_cd:
                    if self.curr_letter >= len(self.dialogues[self.curr_t]) or self.curr_t >10 and self.curr_t <13 or self.curr_t > 14:
                        pass
                    else:
                        self.animateTalkingRedTrashBag()
                        self.RedupdateTrashTalkTime = pygame.time.get_ticks()
                screen.blit(self.RedTalkingCurrImg, ( 9*85,
                                                    screen_height // 2 + self.mainCharCurrImg.get_height() // 2 - self.RedTrashCurrImg.get_height()))
                # Talking Blue Bag
            if self.curr_t >= 15:
                if pygame.time.get_ticks() - self.BlueupdateTrashTalkTime > self.BlueTrashAnim_cd:
                    if self.curr_letter >= len(self.dialogues[self.curr_t]) or self.curr_t > 17:
                        pass
                    else:
                        self.animateTalkingBlueTrashBag()
                        self.BlueupdateTrashTalkTime = pygame.time.get_ticks()
                screen.blit(self.BlueTalkingCurrImg, (10 * 85,
                                                     screen_height // 2 + self.mainCharCurrImg.get_height() // 2 - self.BlueTrashCurrImg.get_height()))



    def animateMainChar(self):
        if self.mainCharCurrFrame == 0:
            self.mainCharCurrFrame = 1
            self.mainCharCurrImg = self.mainChar[self.mainCharCurrFrame]
            self.mainCharCurrImg = pygame.transform.scale(self.mainCharCurrImg, (self.scalemainCharImgTo,self.scalemainCharImgTo))
        else:
            self.mainCharCurrFrame = 0
            self.mainCharCurrImg  = self.mainChar[self.mainCharCurrFrame]
            self.mainCharCurrImg = pygame.transform.scale(self.mainCharCurrImg, (self.scalemainCharImgTo, self.scalemainCharImgTo))


    def animateRedTrashBag(self):
        if self.RedTrashCurrFrame == 0:
            self.RedTrashCurrFrame = 1
            self.RedTrashCurrImg  = self.RedBagImgs[self.RedTrashCurrFrame]
            self.RedTrashCurrImg  = pygame.transform.scale(self.RedTrashCurrImg, (self.scaleTrashImgTo,self.scaleTrashImgTo))
        elif self.RedTrashCurrFrame == 1:
            self.RedTrashCurrFrame = 0
            self.RedTrashCurrImg  = self.RedBagImgs[self.RedTrashCurrFrame]
            self.RedTrashCurrImg = pygame.transform.scale(self.RedTrashCurrImg, (self.scaleTrashImgTo, self.scaleTrashImgTo))
    def animateTalkingRedTrashBag(self):
        if self.RedTalkCurrFrame == 0:
            self.RedTalkCurrFrame = 1
            self.RedTalkingCurrImg  =  self.RedTrashTalkImgs[self.RedTalkCurrFrame]
            self.RedTalkingCurrImg  = pygame.transform.scale(self.RedTalkingCurrImg, (self.scaleTrashImgTo,self.scaleTrashImgTo))
        elif self.RedTalkCurrFrame == 1:
            self.RedTalkCurrFrame = 0
            self.RedTalkingCurrImg  =  self.RedTrashTalkImgs[self.RedTalkCurrFrame]
            self.RedTalkingCurrImg = pygame.transform.scale(self.RedTalkingCurrImg, (self.scaleTrashImgTo, self.scaleTrashImgTo))

    def animateBlueTrashBag(self):
        if self.BlueTrashCurrFrame == 0:
            self.BlueTrashCurrFrame = 1
            self.BlueTrashCurrImg  = self.BlueBagImgs[self.BlueTrashCurrFrame]
            self.BlueTrashCurrImg   = pygame.transform.scale( self.BlueTrashCurrImg, (self.scaleTrashImgTo,self.scaleTrashImgTo))
        elif self.BlueTrashCurrFrame == 1:
            self.BlueTrashCurrFrame = 0
            self.BlueTrashCurrImg  = self.BlueBagImgs[self.BlueTrashCurrFrame]
            self.BlueTrashCurrImg  = pygame.transform.scale( self.BlueTrashCurrImg, (self.scaleTrashImgTo, self.scaleTrashImgTo))
    def animateTalkingBlueTrashBag(self):
        if self.BlueTalkCurrFrame == 0:
            self.BlueTalkCurrFrame = 1
            self.BlueTalkingCurrImg  = self.BlueTrashTalkImgs[self.BlueTalkCurrFrame]
            self.BlueTalkingCurrImg   = pygame.transform.scale(self.BlueTalkingCurrImg, (self.scaleTrashImgTo,self.scaleTrashImgTo))
        elif self.BlueTalkCurrFrame == 1:
            self.BlueTalkCurrFrame = 0
            self.BlueTalkingCurrImg   = self.BlueTrashTalkImgs[self.BlueTalkCurrFrame]
            self.BlueTalkingCurrImg = pygame.transform.scale(self.BlueTalkingCurrImg, (self.scaleTrashImgTo, self.scaleTrashImgTo))

#prelvl2 boss
class preLvl2BossDialogues:
    def __init__(self):
        # animation
        self.update_text_time = pygame.time.get_ticks()
        self.anim_cd = 30
        # text
        self.curr_t = 0
        self.currentText = ""
        self.curr_letter = 1
        self.dialogues = ["From months of trash, the room is airy of rot,","The stench is now so foul that it travels outside,","and the neighbors hire \"The Cleaner,\" ",
                          "the city's #1 cleaner for the worst of smells.","\"GodDANG it smells like ass in here!\"","\"Welp...at least I'm getting paid good for this..\"",
                          "\"I'm cleaning you up after I clean all this mess, buddy!\""]
        # next text
        self.next_text_cd = 0
        self.finish_dialog = False
        #Character Animation Settings
        self.scaleImgTo = 330
        self.CurrFrame = 0
        self.imgs =[pygame.image.load("boss20.png"),pygame.image.load("boss21.png")]
        self.CurrImg = self.imgs[self.CurrFrame]
        self.CurrImg = pygame.transform.scale(self.CurrImg,(self.scaleImgTo,self.scaleImgTo))
        self.updateTime = pygame.time.get_ticks()
        self.Anim_cd = 150

    def DialogAnim(self,screen):
            # key press
            self.keys = pygame.key.get_pressed()
            # text
            text_size = 25
            font = pygame.font.Font("PressStart2P.ttf", text_size)
            text = self.dialogues[self.curr_t]
            self.currentText = text
            text = text[:self.curr_letter]
            text_render = font.render(text, False, "Black")
            width, height = font.size(text)
            # animation
            if pygame.time.get_ticks() - self.update_text_time > self.anim_cd:
                self.update_text_time = pygame.time.get_ticks()
                self.curr_letter += 1
            # next text
            if self.keys[pygame.K_SPACE]:
                if self.curr_t == len(self.dialogues) - 1:
                    if self.next_text_cd > 300:
                        self.finish_dialog = True
                elif self.next_text_cd > 300:
                    self.curr_letter = 1
                    self.curr_t += 1
                    self.next_text_cd = 0
            self.next_text_cd += 10
            screen.blit(text_render,(screen_width//2-width//2,200))
            #Character Cue
            if pygame.time.get_ticks() - self.updateTime > self.Anim_cd:
                self.animate()
                self.updateTime = pygame.time.get_ticks()
            screen.blit(self.CurrImg ,(screen_width//2-self.CurrImg .get_width()//2,screen_height//2-self.CurrImg .get_height()//2))

    def animate(self):
        if self.CurrFrame == 0:
            self.CurrFrame = 1
            self.CurrImg = self.imgs[self.CurrFrame].convert_alpha()
            self.CurrImg = pygame.transform.scale(self.CurrImg, (self.scaleImgTo,self.scaleImgTo))
        else:
            self.CurrFrame = 0
            self.CurrImg  = self.imgs[self.CurrFrame].convert_alpha()
            self.CurrImg = pygame.transform.scale(self.CurrImg, (self.scaleImgTo, self.scaleImgTo))
#prelvl 3
class preLvl3Dialogues:
    def __init__(self):
        # animation
        self.update_text_time = pygame.time.get_ticks()
        self.anim_cd = 30
        # text
        self.curr_t = 0
        self.currentText = ""
        self.curr_letter = 1
        self.dialogues = ["Breaking News!","....","A man's room smells so bad,",#2 - 3
                          "\"The Cleaner\" was called in, but","he is now in the","hospital after altercations", # 5- 7
                          "with the man...","Who can stop him??", #8 -10
                          "We have report that,","the man's mom is","now at the scene!","\"Honey! Why are you doing","this to yourself??\"",
                          "\"I'm coming in there","to save you from yourself!!\"","\"It's for your own good!!\"","\"I don't need your love!!\""]
        # next text
        self.next_text_cd = 0
        self.finish_dialog = False
        #Characters
        self.momImgs = [pygame.image.load('mom0.png'),pygame.image.load('mom1.png'),pygame.image.load('mom2.png')]
        self.cleanerImgs = [pygame.image.load('boss20.png'),pygame.image.load('boss21.png'), pygame.image.load('boss26.png'),
                            pygame.image.load('boss27.png')]
        self.tvImgs = [pygame.image.load('tv0.png'), pygame.image.load('tv1.png')]
        self.scalemainCharImgTo = 150
        self.mainCharCurrFrame = 0
        self.mainCharImgs = [pygame.image.load('mainChar2.png'),pygame.image.load('mainChar6.png')]
        self.mainChar = self.mainCharImgs[self.mainCharCurrFrame]
        self.mainChar = pygame.transform.scale(self.mainChar, (self.scalemainCharImgTo, self.scalemainCharImgTo))
        #Character Animation Settings
        self.updateMainCharTalkTime = pygame.time.get_ticks()
        self.mainCharTalkAnim_cd = 120
            #tv
        self.scaleTVImgTo = 950
        self.TVCurrFrame = 0
        self.TVCurrImg = self.tvImgs[self.TVCurrFrame]
        self.TVCurrImg = pygame.transform.scale(self.TVCurrImg,(self.scaleTVImgTo,self.scaleTVImgTo))
        self.updateTVTime = pygame.time.get_ticks()
        self.TVAnim_cd = 1780
            #mom
        self.scaleMomImgTo = 160
        self.momCurrFrame = 0
        self.momCurrImg = self.momImgs[self.momCurrFrame]
        self.updateMomTime = pygame.time.get_ticks()
        self.momAnim_cd = 130
            #cleaner
        self.scaleCleanerImgTo = 150
        self.CleanerCurrFrame = 0
        self.CleanerCurrFrame2 = 2
        self.CleanerCurrImg = self.cleanerImgs[self.CleanerCurrFrame]
        self.CleanerAnim_cd = 300
        self.updateCleanerTime = pygame.time.get_ticks()

    def DialogAnim(self,screen):
        # key press
        self.keys = pygame.key.get_pressed()
        # text
        text_size = 15
        font = pygame.font.Font("PressStart2P.ttf", text_size)
        text = self.dialogues[self.curr_t]
        self.currentText = text
        text = text[:self.curr_letter]
        text_render = font.render(text, False, "Black")
        width, height = font.size(text)
        # animation
        if pygame.time.get_ticks() - self.update_text_time > self.anim_cd:
            self.update_text_time = pygame.time.get_ticks()
            self.curr_letter += 1
        # next text
        if self.keys[pygame.K_SPACE]:
            if self.curr_t == len(self.dialogues) - 1:
                if self.next_text_cd > 300:
                    self.finish_dialog = True
            elif self.next_text_cd > 300:
                self.curr_letter = 1
                self.curr_t += 1
                self.next_text_cd = 0
        self.next_text_cd += 10
        #Character Cues/ Animations
            #TV
        if pygame.time.get_ticks() - self.updateTVTime > self.TVAnim_cd:
            self.updateTVTime = pygame.time.get_ticks()
            self.animateTV()
        screen.blit(self.TVCurrImg ,(screen_width//2-self.TVCurrImg.get_width()//2 + 70,screen_height//2-self.TVCurrImg.get_height()//2))
            #Cleaner
        if self.curr_t ==2:
            screen.blit(self.mainChar,(screen_width//2-self.mainChar.get_width()//2,screen_height//2-self.mainChar.get_height()//2))
        if self.curr_t >= 3 and self.curr_t <= 4:
            if pygame.time.get_ticks() - self.updateCleanerTime > self.CleanerAnim_cd:
                self.animateCleaner()
                self.updateCleanerTime = pygame.time.get_ticks()
            screen.blit(self.CleanerCurrImg,(screen_width//2 - self.CleanerCurrImg.get_width()//2,screen_height//2-self.CleanerCurrImg.get_height()//2))
        if self.curr_t >=5 and self.curr_t <=8:
            if pygame.time.get_ticks() - self.updateCleanerTime > self.CleanerAnim_cd:
                self.CleanerCurrImg = self.cleanerImgs[self.CleanerCurrFrame]
                self.animateXXCleaner()
                self.updateCleanerTime = pygame.time.get_ticks()
            screen.blit(self.CleanerCurrImg,(screen_width//2 - self.CleanerCurrImg.get_width()//2,screen_height//2-self.CleanerCurrImg.get_height()//2))
            #mom
        if self.curr_t >= 9 and self.curr_t <= 10:
            screen.blit(self.momCurrImg,(screen_width//2-self.momCurrImg.get_width()//2,screen_height//2-self.momCurrImg.get_height()//2))
        if self.curr_t >= 11 and self.curr_t <= 15:
            if pygame.time.get_ticks() - self.updateMomTime > self.momAnim_cd:
                self.momCurrImg = self.momImgs[self.momCurrFrame]
                self.animateMom()
                self.updateMomTime = pygame.time.get_ticks()
            screen.blit(self.momCurrImg, (screen_width // 2 - self.CleanerCurrImg.get_width() // 2,
                                              screen_height // 2 - self.CleanerCurrImg.get_height() // 2))
            #text
        if self.curr_t == 16:
            self.mainChar = self.mainCharImgs[1]
            self.mainChar = pygame.transform.scale(self.mainChar,(self.scalemainCharImgTo,self.scalemainCharImgTo))
            screen.blit(self.mainChar,(screen_width//2-self.mainChar.get_width()//2,screen_height//2-self.mainChar.get_height()//2))
        screen.blit(text_render, (screen_width // 2 - width // 2, 300))

    def animateTV(self):
        if self.TVCurrFrame == 0:
            self.TVCurrFrame = 1
            self.TVCurrImg  = self.tvImgs[self.TVCurrFrame]
            self.TVCurrImg   = pygame.transform.scale(self.TVCurrImg , (self.scaleTVImgTo,self.scaleTVImgTo))
        elif self.TVCurrFrame == 1:
            self.TVCurrFrame = 0
            self.TVCurrImg  = self.tvImgs[self.TVCurrFrame]
            self.TVCurrImg = pygame.transform.scale(self.TVCurrImg, (self.scaleTVImgTo, self.scaleTVImgTo))

    def animateCleaner(self):
        if self.CleanerCurrFrame == 0:
            self.CleanerCurrFrame = 1
            self.CleanerCurrImg  = self.cleanerImgs[self.CleanerCurrFrame]
            self.CleanerCurrImg   = pygame.transform.scale(self.CleanerCurrImg, (self.scaleCleanerImgTo, self.scaleCleanerImgTo))
        elif self.CleanerCurrFrame == 1:
            self.CleanerCurrFrame = 0
            self.CleanerCurrImg  = self.cleanerImgs[self.CleanerCurrFrame]
            self.CleanerCurrImg  = pygame.transform.scale(self.CleanerCurrImg, (self.scaleCleanerImgTo, self.scaleCleanerImgTo))
    def animateXXCleaner(self):
        if self.CleanerCurrFrame2 == 2:
            self.CleanerCurrFrame2 = 3
            self.CleanerCurrImg  = self.cleanerImgs[self.CleanerCurrFrame2]
            self.CleanerCurrImg  = pygame.transform.scale(self.CleanerCurrImg, (self.scaleCleanerImgTo, self.scaleCleanerImgTo))
        elif self.CleanerCurrFrame2 == 3:
            self.CleanerCurrFrame2 = 2
            self.CleanerCurrImg  = self.cleanerImgs[self.CleanerCurrFrame2]
            self.CleanerCurrImg  = pygame.transform.scale(self.CleanerCurrImg, (self.scaleCleanerImgTo, self.scaleCleanerImgTo))

    def animateMom(self):
        if self.momCurrFrame == len(self.momImgs)-1:
            self.momCurrFrame = 0
            self.momCurrImg  = self.momImgs[self.momCurrFrame]
            self.momCurrImg   = pygame.transform.scale(self.momCurrImg, (self.scaleMomImgTo, self.scaleMomImgTo))
        else:
            self.momCurrFrame += 1
            self.momCurrImg  = self.momImgs[self.momCurrFrame]
            self.momCurrImg  = pygame.transform.scale(self.momCurrImg, (self.scaleMomImgTo, self.scaleMomImgTo))
#prelvl3 boss

class preLvl3BossDialogues:
    def __init__(self):
        # animation
        self.update_text_time = pygame.time.get_ticks()
        self.anim_cd = 30
        # text
        self.curr_t = 0
        self.currentText = ""
        self.curr_letter = 1
        self.dialogues = ["HUNDREDS...of thousands of dollars unpaid.","Angry IRS agents...","Trash not taken out...","A man in the hospital....","Ignoring mom....",
                          "Oh boy........",".......","...........","..............","She's angry."]
        # next text
        self.next_text_cd = 0
        self.finish_dialog = False
        #Characters : IRS agent
        self.updateIRSTime = pygame.time.get_ticks()
        self.IRSAnim_cd = 85
        self.IRSCurrFrame = 0
        self.scaleIRSimgTo = 200
        self.IRSimgs = [pygame.image.load("BankerBoss2.png"),pygame.image.load("BankerBoss3.png")]
        self.IRSCurrImg = self.IRSimgs[self.IRSCurrFrame]
        #Trash
        self.BagImgs = [pygame.image.load('RedTrash5.png'), pygame.image.load('RedTrash6.png')]
        self.scaleTrashImgTo = 200
        self.TrashCurrFrame = 0
        self.TrashCurrImg = self.BagImgs[self.TrashCurrFrame]
        self.TrashCurrImg = pygame.transform.scale(self.TrashCurrImg,
                                                      (self.scaleTrashImgTo, self.scaleTrashImgTo))
        self.updateTrashTime = pygame.time.get_ticks()
        self.TrashAnim_cd = 260
        # cleaner
        self.cleanerImgs = [pygame.image.load('boss26.png'), pygame.image.load('boss27.png')]
        self.scaleCleanerImgTo = 200
        self.CleanerCurrFrame = 0
        self.CleanerCurrFrame2 = 2
        self.CleanerCurrImg = self.cleanerImgs[self.CleanerCurrFrame]
        self.CleanerAnim_cd = 300
        self.updateCleanerTime = pygame.time.get_ticks()
        # mom
        self.momImgs = [pygame.image.load('mom0.png'), pygame.image.load('mom1.png'),
                        pygame.image.load('mom2.png')]
        self.scaleMomImgTo = 200
        self.momCurrFrame = 0
        self.momCurrImg = self.momImgs[self.momCurrFrame]
        self.updateMomTime = pygame.time.get_ticks()
        self.momAnim_cd = 130
    def DialogAnim(self,screen):
        # key press
        self.keys = pygame.key.get_pressed()
        # text
        text_size = 30
        font = pygame.font.Font("PressStart2P.ttf", text_size)
        text = self.dialogues[self.curr_t]
        self.currentText = text
        text = text[:self.curr_letter]
        text_render = font.render(text, False, "Black")
        width, height = font.size(text)
        # animation
        if pygame.time.get_ticks() - self.update_text_time > self.anim_cd:
            self.update_text_time = pygame.time.get_ticks()
            self.curr_letter += 1
        # next text
        if self.keys[pygame.K_SPACE]:
            if self.curr_t == len(self.dialogues) - 1:
                if self.next_text_cd > 300:
                    self.finish_dialog = True
            elif self.next_text_cd > 300:
                self.curr_letter = 1
                self.curr_t += 1
                self.next_text_cd = 0
        self.next_text_cd += 10
        screen.blit(text_render, (screen_width // 2 - width // 2, screen_height//2 - height//2))

        # Character Cues/ Animations
        # IRS
        if self.curr_t >= 1 and self.curr_t <= 4:
            if pygame.time.get_ticks() - self.updateIRSTime > self.IRSAnim_cd:
                self.updateIRSTime = pygame.time.get_ticks()
                self.animateIRS()
            screen.blit(self.IRSCurrImg, (screen_width // 2 - self.IRSCurrImg.get_width() // 2,
                                         screen_height // 2 + self.IRSCurrImg.get_height() // 2))
        # Trash
        if self.curr_t >= 2 and self.curr_t <= 4:
            if pygame.time.get_ticks() - self.updateTrashTime > self.TrashAnim_cd:
                self.animateTrash()
                self.updateTrashTime = pygame.time.get_ticks()

            screen.blit(self.TrashCurrImg, (screen_width//2 + 200,
                                               screen_height // 2 + self.TrashCurrImg.get_height() // 2))
        # # Cleaner
        if self.curr_t >= 3 and self.curr_t <= 4:
            if pygame.time.get_ticks() - self.updateCleanerTime > self.CleanerAnim_cd:
                self.CleanerCurrImg = self.cleanerImgs[self.CleanerCurrFrame]
                self.animateCleaner()
                self.updateCleanerTime = pygame.time.get_ticks()
            screen.blit(self.CleanerCurrImg, (screen_width // 2 -400,
                                              screen_height // 2 + self.CleanerCurrImg.get_height() // 2))
            # mom
        if self.curr_t ==4:
            if pygame.time.get_ticks() - self.updateMomTime > self.momAnim_cd:
                self.momCurrImg = self.momImgs[self.momCurrFrame]
                self.animateMom()
                self.updateMomTime = pygame.time.get_ticks()
            screen.blit(self.momCurrImg, (screen_width // 2 - 700,
                                          screen_height // 2 + self.CleanerCurrImg.get_height() // 2))

    def animateIRS(self):
        if self.IRSCurrFrame == 0:
            self.IRSCurrFrame = 1
            self.IRSCurrImg  = self.IRSimgs[self.IRSCurrFrame]
            self.IRSCurrImg   = pygame.transform.scale(self.IRSCurrImg , (self.scaleIRSimgTo,self.scaleIRSimgTo))
        elif self.IRSCurrFrame == 1:
            self.IRSCurrFrame = 0
            self.IRSCurrImg  = self.IRSimgs[self.IRSCurrFrame]
            self.IRSCurrImg = pygame.transform.scale(self.IRSCurrImg, (self.scaleIRSimgTo, self.scaleIRSimgTo))

    def animateTrash(self):
        if self.TrashCurrFrame == 0:
            self.TrashCurrFrame = 1
            self.TrashCurrImg = self.BagImgs[self.TrashCurrFrame]
            self.TrashCurrImg = pygame.transform.scale(self.TrashCurrImg,
                                                          (self.scaleTrashImgTo, self.scaleTrashImgTo))
        elif self.TrashCurrFrame == 1:
            self.TrashCurrFrame = 0
            self.TrashCurrImg = self.BagImgs[self.TrashCurrFrame]
            self.TrashCurrImg = pygame.transform.scale(self.TrashCurrImg,
                                                          (self.scaleTrashImgTo, self.scaleTrashImgTo))

    def animateCleaner(self):
        if self.CleanerCurrFrame == 0:
            self.CleanerCurrFrame = 1
            self.CleanerCurrImg  = self.cleanerImgs[self.CleanerCurrFrame]
            self.CleanerCurrImg   = pygame.transform.scale(self.CleanerCurrImg, (self.scaleCleanerImgTo, self.scaleCleanerImgTo))
        elif self.CleanerCurrFrame == 1:
            self.CleanerCurrFrame = 0
            self.CleanerCurrImg  = self.cleanerImgs[self.CleanerCurrFrame]
            self.CleanerCurrImg  = pygame.transform.scale(self.CleanerCurrImg, (self.scaleCleanerImgTo, self.scaleCleanerImgTo))

    def animateMom(self):
        if self.momCurrFrame == len(self.momImgs)-1:
            self.momCurrFrame = 0
            self.momCurrImg  = self.momImgs[self.momCurrFrame]
            self.momCurrImg   = pygame.transform.scale(self.momCurrImg, (self.scaleMomImgTo, self.scaleMomImgTo))
        else:
            self.momCurrFrame += 1
            self.momCurrImg  = self.momImgs[self.momCurrFrame]
            self.momCurrImg  = pygame.transform.scale(self.momCurrImg, (self.scaleMomImgTo, self.scaleMomImgTo))


#game end
class gameEndDialogues:
    def __init__(self):
        # animation
        self.update_text_time = pygame.time.get_ticks()
        self.anim_cd = 30
        # text
        self.curr_t = 0
        self.currentText = ""
        self.curr_letter = 1
        self.dialogues = ["Despite countless efforts from people from all over,","he continues to be a menace to society.","...",".......","..............","The End.",
                          "Thanks for playing!","Music by: Garoslaw,ChillMindscapes"]
        # next text
        self.next_text_cd = 0
        self.finish_dialog = False
        # Characters : IRS agent
        self.updateIRSTime = pygame.time.get_ticks()
        self.IRSAnim_cd = 85
        self.IRSCurrFrame = 0
        self.scaleIRSimgTo = 200
        self.IRSimgs = [pygame.image.load("BankerBoss2.png"),
                        pygame.image.load("BankerBoss3.png")]
        self.IRSCurrImg = self.IRSimgs[self.IRSCurrFrame]
        # Trash
        self.BagImgs = [pygame.image.load('RedTrash5.png'), pygame.image.load('RedTrash6.png')]
        self.scaleTrashImgTo = 200
        self.TrashCurrFrame = 0
        self.TrashCurrImg = self.BagImgs[self.TrashCurrFrame]
        self.TrashCurrImg = pygame.transform.scale(self.TrashCurrImg,
                                                   (self.scaleTrashImgTo, self.scaleTrashImgTo))
        self.updateTrashTime = pygame.time.get_ticks()
        self.TrashAnim_cd = 260
        # cleaner
        self.cleanerImgs = [pygame.image.load('boss26.png'), pygame.image.load('boss27.png')]
        self.scaleCleanerImgTo = 200
        self.CleanerCurrFrame = 0
        self.CleanerCurrFrame2 = 2
        self.CleanerCurrImg = self.cleanerImgs[self.CleanerCurrFrame]
        self.CleanerAnim_cd = 300
        self.updateCleanerTime = pygame.time.get_ticks()
        # mom
        self.momImgs = [pygame.image.load('mom0.png'), pygame.image.load('mom1.png'),
                        pygame.image.load('mom2.png')]
        self.scaleMomImgTo = 200
        self.momCurrFrame = 0
        self.momCurrImg = self.momImgs[self.momCurrFrame]
        self.updateMomTime = pygame.time.get_ticks()
        self.momAnim_cd = 130

    def DialogAnim(self, screen):
        # key press
        self.keys = pygame.key.get_pressed()
        # text
        text_size = 30
        font = pygame.font.Font("PressStart2P.ttf", text_size)
        text = self.dialogues[self.curr_t]
        self.currentText = text
        text = text[:self.curr_letter]
        text_render = font.render(text, False, "Black")
        width, height = font.size(text)
        # animation
        if pygame.time.get_ticks() - self.update_text_time > self.anim_cd:
            self.update_text_time = pygame.time.get_ticks()
            self.curr_letter += 1
        # next text
        if self.keys[pygame.K_SPACE]:
            if self.curr_t == len(self.dialogues) - 1:
                if self.next_text_cd > 300:
                    self.finish_dialog = True
            elif self.next_text_cd > 300:
                self.curr_letter = 1
                self.curr_t += 1
                self.next_text_cd = 0
        self.next_text_cd += 10
        screen.blit(text_render, (screen_width // 2 - width // 2, screen_height // 2 - height // 2))

        # Character Cues/ Animations
        # IRS
        if pygame.time.get_ticks() - self.updateIRSTime > self.IRSAnim_cd:
            self.updateIRSTime = pygame.time.get_ticks()
            self.animateIRS()
        screen.blit(self.IRSCurrImg, (screen_width // 2 - self.IRSCurrImg.get_width() // 2,
                                      screen_height // 2 + self.IRSCurrImg.get_height() // 2))
        # Trash
        if pygame.time.get_ticks() - self.updateTrashTime > self.TrashAnim_cd:
            self.animateTrash()
            self.updateTrashTime = pygame.time.get_ticks()

        screen.blit(self.TrashCurrImg, (screen_width // 2 + 200,
                                        screen_height // 2 + self.TrashCurrImg.get_height() // 2))
        # # Cleaner
        if pygame.time.get_ticks() - self.updateCleanerTime > self.CleanerAnim_cd:
            self.CleanerCurrImg = self.cleanerImgs[self.CleanerCurrFrame]
            self.animateCleaner()
            self.updateCleanerTime = pygame.time.get_ticks()
        screen.blit(self.CleanerCurrImg, (screen_width // 2 - 400,
                                          screen_height // 2 + self.CleanerCurrImg.get_height() // 2))
        # mom
        if pygame.time.get_ticks() - self.updateMomTime > self.momAnim_cd:
            self.momCurrImg = self.momImgs[self.momCurrFrame]
            self.animateMom()
            self.updateMomTime = pygame.time.get_ticks()
        screen.blit(self.momCurrImg, (screen_width // 2 - 700,
                                      screen_height // 2 + self.CleanerCurrImg.get_height() // 2))

    def animateIRS(self):
        if self.IRSCurrFrame == 0:
            self.IRSCurrFrame = 1
            self.IRSCurrImg = self.IRSimgs[self.IRSCurrFrame]
            self.IRSCurrImg = pygame.transform.scale(self.IRSCurrImg, (self.scaleIRSimgTo, self.scaleIRSimgTo))
        elif self.IRSCurrFrame == 1:
            self.IRSCurrFrame = 0
            self.IRSCurrImg = self.IRSimgs[self.IRSCurrFrame]
            self.IRSCurrImg = pygame.transform.scale(self.IRSCurrImg, (self.scaleIRSimgTo, self.scaleIRSimgTo))

    def animateTrash(self):
        if self.TrashCurrFrame == 0:
            self.TrashCurrFrame = 1
            self.TrashCurrImg = self.BagImgs[self.TrashCurrFrame]
            self.TrashCurrImg = pygame.transform.scale(self.TrashCurrImg,
                                                       (self.scaleTrashImgTo, self.scaleTrashImgTo))
        elif self.TrashCurrFrame == 1:
            self.TrashCurrFrame = 0
            self.TrashCurrImg = self.BagImgs[self.TrashCurrFrame]
            self.TrashCurrImg = pygame.transform.scale(self.TrashCurrImg,
                                                       (self.scaleTrashImgTo, self.scaleTrashImgTo))

    def animateCleaner(self):
        if self.CleanerCurrFrame == 0:
            self.CleanerCurrFrame = 1
            self.CleanerCurrImg = self.cleanerImgs[self.CleanerCurrFrame]
            self.CleanerCurrImg = pygame.transform.scale(self.CleanerCurrImg,
                                                         (self.scaleCleanerImgTo, self.scaleCleanerImgTo))
        elif self.CleanerCurrFrame == 1:
            self.CleanerCurrFrame = 0
            self.CleanerCurrImg = self.cleanerImgs[self.CleanerCurrFrame]
            self.CleanerCurrImg = pygame.transform.scale(self.CleanerCurrImg,
                                                         (self.scaleCleanerImgTo, self.scaleCleanerImgTo))

    def animateMom(self):
        if self.momCurrFrame == len(self.momImgs) - 1:
            self.momCurrFrame = 0
            self.momCurrImg = self.momImgs[self.momCurrFrame]
            self.momCurrImg = pygame.transform.scale(self.momCurrImg, (self.scaleMomImgTo, self.scaleMomImgTo))
        else:
            self.momCurrFrame += 1
            self.momCurrImg = self.momImgs[self.momCurrFrame]
            self.momCurrImg = pygame.transform.scale(self.momCurrImg, (self.scaleMomImgTo, self.scaleMomImgTo))
#ENEMIES---#
class Enemy(Sprite):
    def __init__(self):
        super().__init__()
        #load img
        self.imgScaleTo = 60
        self.img = [pygame.image.load('card2.png'),pygame.image.load('card3.png')]
        self.frame = 0
        self.image = pygame.transform.scale(self.img[self.frame],(self.imgScaleTo,self.imgScaleTo))
        #enemy spawn
        self.x_pos = random.randint(-self.imgScaleTo, screen_width + self.imgScaleTo//2)
        self.y_pos = random.choices([-self.imgScaleTo,screen_height+self.imgScaleTo//2])
        self.y_pos = self.y_pos[0]
        self.rect = self.image.get_rect(topleft= (self.x_pos,self.y_pos))
        self.enemy_speed = 3.6
        self.health = 1

    def update(self,player,bullet_group):
        player_vec = pygame.math.Vector2(player.center)
        enemy_vec = pygame.math.Vector2(self.rect.center)
        dir = (player_vec - enemy_vec).normalize()
        self.rect.left += dir[0] * self.enemy_speed
        self.rect.top += dir[1] * self.enemy_speed
        #collision
        if pygame.sprite.spritecollide(self,bullet_group,True):
            self.health -=1
        if self.health == 0:
            self.kill()

    def animate(self):
        if self.frame == 0:
            self.frame = 1
            self.image = self.img[self.frame]
        else:
            self.frame = 0
            self.image = self.img[self.frame]
class Spawn_Enemy():
    def __init__(self):
        self.update_time = pygame.time.get_ticks()
        self.enemy_group = pygame.sprite.Group()
        self.spawn_cooldown = 300
        self.total_enemies = 0
        # animation
        self.update_animTime = pygame.time.get_ticks()
        self.anim_cd = 200

    def spawn(self,screen,player,bullet_group):
        if pygame.time.get_ticks() - self.update_time > self.spawn_cooldown:
            self.total_enemies  +=1
            self.update_time = pygame.time.get_ticks()
            if len(self.enemy_group)<30:
                self.enemy_group.add(Enemy())
        if pygame.time.get_ticks() - self.update_animTime > self.anim_cd:
            self.update_animTime = pygame.time.get_ticks()
            for e in self.enemy_group:
                e.animate()
        self.enemy_group.update(player,bullet_group)
        self.enemy_group.draw(screen)

trail_group = pygame.sprite.Group()
class lvl2Enemy(Sprite):
    def __init__(self):
        super().__init__()
        #special atk
        self.update_time = pygame.time.get_ticks()
        self.atk_cd = 2100
        self.spawn_trail = False
        #Animation Imgs
        self.Blueframe = 0
        self.BlueImgs = [pygame.image.load("BlueTrash1.png").convert_alpha(),pygame.image.load("BlueTrash2.png").convert_alpha()]
        self.Redframe = 0
        self.RedImgs = [pygame.image.load("RedTrash3.png").convert_alpha(), pygame.image.load("RedTrash4.png").convert_alpha()]
        #Health/DMG
        self.width = 30
        self.height = 30
        self.image = self.BlueImgs[self.Blueframe]
        self.x_pos = random.randint(-self.image.get_width(), screen_width + self.image.get_width())
        self.y_pos = random.choices([-self.image.get_height(), screen_height + self.image.get_height()])
        self.rect = self.image.get_rect(topleft=(self.x_pos, self.y_pos[0]))
        self.enemy_speed = 3.2
        self.health = 1

    def update(self,player,bullet_groups,screen):
        player_vec = pygame.math.Vector2(player.center)
        enemy_vec = pygame.math.Vector2(self.rect.center)
        dir = (player_vec - enemy_vec).normalize()
        self.rect.left += dir[0] * self.enemy_speed
        self.rect.top += dir[1] * self.enemy_speed

        if pygame.sprite.spritecollide(self,bullet_groups,True):
            self.health -=1
        if self.health == 0:
            self.kill()

        if pygame.time.get_ticks() - self.update_time > self.atk_cd and self.spawn_trail == False:
            self.spawn_trail = True
            self.update_time = pygame.time.get_ticks()
            turd = Turd_Trail(self.rect)
            trail_group.add(turd)

        if pygame.time.get_ticks() - self.update_time < self.atk_cd:
            self.spawn_trail = False

    def Blueanimate(self):
        if self.Blueframe == 0:
            self.Blueframe = 1
            self.image = self.BlueImgs[self.Blueframe].convert_alpha()
        else:
            self.Blueframe = 0
            self.image = self.BlueImgs[self.Blueframe].convert_alpha()

    def Redanimate(self):
        if self.Redframe == 0:
            self.Redframe = 1
            self.image = self.RedImgs[self.Redframe].convert_alpha()
        else:
            self.Redframe = 0
            self.image = self.RedImgs[self.Redframe].convert_alpha()



class Turd_Trail(Sprite):
    def __init__(self,trash_pos):
        super().__init__()
        self.frame = 0
        self.imgs = [pygame.image.load("Poop1.png").convert_alpha(),pygame.image.load("Poop2.png").convert_alpha()]
        self.image = self.imgs[self.frame].convert_alpha()
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.trash_pos = trash_pos
        self.rect = self.image.get_rect(midleft=(self.trash_pos.midleft[0],self.trash_pos.midleft[1]))

    def animatePoop(self):
        if self.frame == 0:
            self.frame = 1
            self.image = self.imgs[self.frame].convert_alpha()
            self.image = pygame.transform.scale(self.image,(30,30)).convert_alpha()
        else:
            self.frame = 0
            self.image = self.imgs[self.frame].convert_alpha()
            self.image = pygame.transform.scale(self.image,(30,30)).convert_alpha()

    def update(self):
        if self.rect.right < 0 or self.rect.top > screen_height or self.rect.bottom < 0 or self.rect.left > screen_width:
            self.kill()

class Spawn_lvl2Enemy():
    def __init__(self):
        self.update_time = pygame.time.get_ticks()
        self.enemy_group = pygame.sprite.Group()
        self.enemy_group2 = pygame.sprite.Group()
        self.spawn_cooldown = 755
        self.total_enemies= 1
        #animation
        self.update_animTime = pygame.time.get_ticks()
        self.anim_cd = 200
    def spawn(self,screen,player,bullet_group):
        global trail_group
        if pygame.time.get_ticks() - self.update_time > self.spawn_cooldown:
            self.total_enemies  +=1
            self.update_time = pygame.time.get_ticks()
            if len(self.enemy_group)<10:
                self.enemy_group.add(lvl2Enemy())
                self.enemy_group2.add(lvl2Enemy())

        #animation
        if pygame.time.get_ticks() - self.update_animTime > self.anim_cd:
            self.update_animTime = pygame.time.get_ticks()
            for e in self.enemy_group:
                e.Blueanimate()
            for e in self.enemy_group2:
                e.Redanimate()
            for p in trail_group:
                p.animatePoop()
        self.enemy_group.update(player,bullet_group,screen)
        self.enemy_group.draw(screen)
        self.enemy_group2.update(player, bullet_group, screen)
        self.enemy_group2.draw(screen)
        trail_group.update()
        trail_group.draw(screen)

    def spawnTrailsOnly(self,screen):
        global trail_group
        if pygame.time.get_ticks() - self.update_animTime > self.anim_cd:
            self.update_animTime = pygame.time.get_ticks()
            for p in trail_group:
                p.animatePoop()
        trail_group.update()
        trail_group.draw(screen)
class lvl3Enemy(Sprite):
    def __init__(self):
        super().__init__()
        self.scaleImgTo = 75
        #imgs
        self.frame = 0
        self.imgs = [pygame.image.load("mom5.png"),pygame.image.load("mom6.png"),pygame.image.load("mom7.png")]
        self.image = self.imgs[self.frame]
        self.image = pygame.transform.scale(self.image,(self.scaleImgTo,self.scaleImgTo))
        #spawn
        self.x_pos = random.randint(-self.image.get_width(), screen_width + self.image.get_width())
        self.y_pos = random.choices([-self.image.get_height(), screen_height + self.image.get_height()])
        self.y_pos = self.y_pos[0]
        self.rect = self.image.get_rect(topleft=(self.x_pos, self.y_pos))
        self.enemy_speed = 2
        self.health = 1

    def update(self, player, player_bullet_group):
        player_vec = pygame.math.Vector2(player.center)
        enemy_vec = pygame.math.Vector2(self.rect.center)
        dir = (player_vec - enemy_vec).normalize()
        self.rect.left += dir[0] * self.enemy_speed
        self.rect.top += dir[1] * self.enemy_speed
        if pygame.sprite.spritecollide(self, player_bullet_group, True):
            self.health -= 1
        if self.health == 0:
            self.kill()

    def animate(self):
        if self.frame == len(self.imgs)-1:
            self.frame = 0
            self.image = self.imgs[self.frame].convert_alpha()
            self.image = pygame.transform.scale(self.image,(self.scaleImgTo,self.scaleImgTo))
        else:
            self.frame += 1
            self.image = self.imgs[self.frame].convert_alpha()
            self.image = pygame.transform.scale(self.image,(self.scaleImgTo,self.scaleImgTo))

#Spawn Enemies
class Spawn_lvl3Enemy():
    def __init__(self):
        self.update_time = pygame.time.get_ticks()
        self.enemy_group = pygame.sprite.Group()
        self.spawn_cooldown = 740
        self.total_enemies= 0
        # special atk
        self.enemy_shooting = False
        self.enemy_bullet_group = pygame.sprite.Group()
        self.update_shoot_time = pygame.time.get_ticks()
        self.atk_cd = 540
        #animation
        self.update_animTime = pygame.time.get_ticks()
        self.anim_cd = 100

    def spawn(self,screen,player,bullet_group):
        if pygame.time.get_ticks() - self.update_time > self.spawn_cooldown:
            self.total_enemies  +=1
            self.update_time = pygame.time.get_ticks()
            if len(self.enemy_group)<30:
                self.enemy_group.add(lvl3Enemy())
        self.enemy_group.update(player,bullet_group)
        self.enemy_group.draw(screen)
        #animations for enemies
        if pygame.time.get_ticks() - self.update_animTime > self.anim_cd:
            self.update_animTime = pygame.time.get_ticks()
            for e in (self.enemy_group):
                e.animate()

    def shoot(self,player,screen):
        if pygame.time.get_ticks() - self.update_shoot_time > self.atk_cd and self.enemy_shooting == False:
            self.enemy_shooting = True
            self.update_shoot_time = pygame.time.get_ticks()
            for e in self.enemy_group:
                self.enemy_bullet_group.add(Lvl3Enemy_Bullet(e.rect, player))
        self.enemy_bullet_group.update()
        self.enemy_bullet_group.draw(screen)

        if pygame.time.get_ticks() - self.update_shoot_time < self.atk_cd:
            self.enemy_shooting = False

#Enemy special atk
class Lvl3Enemy_Bullet(Sprite):
    def __init__(self,enemy_pos,player_pos):
        super().__init__()
        self.image = pygame.image.load("heart0.png").convert_alpha()
        self.image = pygame.transform.scale(self.image,(20,20))
        self.enemy_pos = enemy_pos
        self.rect = self.image.get_rect(midleft=(self.enemy_pos.midleft[0],self.enemy_pos.midleft[1]))
        self.player_pos = player_pos
        self.x_dist = self.player_pos.midleft[0] - self.enemy_pos.midleft[0]
        self.y_dist = self.player_pos.midleft[1] - self.enemy_pos.midleft[1]
        self.rad = math.atan2(self.y_dist, self.x_dist)
        self.dx = math.cos(self.rad)
        self.dy = math.sin(self.rad)
        self.bullet_speed = 8.3

    def update(self):
        self.rect.left += self.dx * self.bullet_speed
        self.rect.top += self.dy * self.bullet_speed
        if self.rect.right < 0 or self.rect.top > screen_height or self.rect.bottom < 0 or self.rect.left > screen_width:
            self.kill()





#BOSSES---#
class Boss1(Sprite):
    def __init__(self):
        super().__init__()
        self.width = 150
        self.height = 150
        self.img = [pygame.image.load("BankerBoss2.png"),pygame.image.load("BankerBoss3.png")]
        self.frame = 0
        self.image = self.img[self.frame]
        self.x_pos= random.randint(-self.width,screen_width+ self.width)
        self.y_pos = random.choices([-self.height,screen_height+self.height])
        self.y_pos = self.y_pos[0]
        self.rect = self.image.get_rect(topleft= (self.x_pos,self.y_pos))
        self.enemy_speed = 3.28
        self.health = 140
        self.died = False
        self.boss_bullet = pygame.sprite.Group()
        #special atk
        self.boss_shooting = False
        self.atk_cd = 400
        self.update_time = pygame.time.get_ticks()
        #animation, dmg anim
        self.dmgAnim = False
        self.dmgAnimCD = 0
        self.anim_cd = 100
        self.update_animTime = pygame.time.get_ticks()
        self.bulletFrame = 0
        #bullet anim
        self.anim_BulletCD = 500
        self.update_BulletanimTime = pygame.time.get_ticks()

    def update(self,screen,player,bullet_group):
        player_vec = pygame.math.Vector2(player.center)
        boss_vec = pygame.math.Vector2(self.rect.center)
        dir = (player_vec - boss_vec).normalize()
        self.rect.left += dir[0] * self.enemy_speed
        self.rect.top += dir[1] * self.enemy_speed
        #collision/dmg animation
        if pygame.sprite.spritecollide(self,bullet_group,True):
            self.health -=1
            self.dmgAnim = True
        if self.health == 0:
            self.died = True
        if self.dmgAnim == True:
            imgCopy = self.image.copy()
            imgCopy.fill("Red",special_flags=pygame.BLEND_RGBA_MULT)
            if self.dmgAnimCD <= 50:
                screen.blit(imgCopy,self.rect)
                self.dmgAnimCD +=1
            elif self.dmgAnimCD > 50:
                self.dmgAnim = False
                self.dmgAnimCD = 0
                screen.blit(self.image, self.rect)
        elif self.dmgAnim == False:
            screen.blit(self.image, self.rect)

        #animation
        if pygame.time.get_ticks() - self.update_animTime > self.anim_cd:
            self.update_animTime = pygame.time.get_ticks()
            self.animate()
        #bullet animation
        if pygame.time.get_ticks() - self.update_BulletanimTime > self.anim_BulletCD:
            self.update_BulletanimTime = pygame.time.get_ticks()
            for e in self.boss_bullet:
                e.animateBullet()
        # boss name
        text_size = 30
        font = pygame.font.Font("PressStart2P.ttf", text_size)
        text = "IRS Agent"
        text_render = font.render(text, False, "Black")
        width, height = font.size(text)
        screen.blit(text_render, (screen_width // 2 - (width // 2), screen_height - 200))
        # health
        for i in range(1, self.health + 1):
            health_surf = pygame.Surface((10, 15))
            screen.blit(health_surf, (screen_width // 2 - 750+(i*health_surf.get_width()), screen_height -130))

    def boss_shoot(self,player,screen):
        if pygame.time.get_ticks() - self.update_time > self.atk_cd and self.boss_shooting == False:
            self.boss_shooting = True
            self.update_time = pygame.time.get_ticks()
            s = Boss_Bullet(self.rect, player)
            self.boss_bullet.add(s)
        self.boss_bullet.update()
        self.boss_bullet.draw(screen)

        if pygame.time.get_ticks() - self.update_time < self.atk_cd:
            self.boss_shooting = False

    def animate(self):
        if self.frame == 0:
            self.frame =1
            self.image = self.img[self.frame]
        else:
            self.frame = 0
            self.image = self.img[self.frame]

class Boss_Bullet(Sprite):
    def __init__(self,boss_pos,player_pos):
        super().__init__()
        self.img = [pygame.image.load('Boss1Weapon0.png'),pygame.image.load('Boss1Weapon1.png'),
                    pygame.image.load('Boss1Weapon2.png'),pygame.image.load('Boss1Weapon3.png')]
        self.bulletFrame = 0
        self.image = self.img[self.bulletFrame]
        self.boss_pos = boss_pos
        self.rect = self.image.get_rect(midleft=(self.boss_pos.midleft[0],self.boss_pos.midleft[1]))
        self.player_pos = player_pos
        self.x_dist = self.player_pos.midleft[0] - self.boss_pos.midleft[0]+ 0.000001
        self.y_dist = self.player_pos.midleft[1] - self.boss_pos.midleft[1] + 0.000001
        self.rad = math.atan2(self.y_dist, self.x_dist)
        self.dx = math.cos(self.rad)
        self.dy = math.sin(self.rad)
        self.bullet_speed = 16.8

    def update(self):
        self.rect.left += self.dx * self.bullet_speed
        self.rect.top += self.dy * self.bullet_speed

        if self.rect.right < 0 or self.rect.top > screen_height or self.rect.bottom < 0 or self.rect.left > screen_width:
            self.kill()

    def animateBullet(self):
        if self.bulletFrame == len(self.img)-1:
            self.bulletFrame =0
            self.image = self.img[self.bulletFrame]
        else:
            self.bulletFrame +=1
            self.image = self.img[self.bulletFrame]

class Boss2(Sprite):
    def __init__(self):
        super().__init__()
        self.CurrFrame = 0
        self.imgs = [pygame.image.load("boss22.png"), pygame.image.load("boss23.png"),
                     pygame.image.load("boss24.png"), pygame.image.load("boss25.png")]
        self.image = self.imgs[self.CurrFrame]
        #spawn
        self.x_pos= random.randint(-self.image.get_width(),screen_width+ self.image.get_width())
        self.y_pos = random.choices([-self.image.get_height(),screen_height+self.image.get_height()])
        self.y_pos = self.y_pos[0]
        self.rect = self.image.get_rect(topleft= (self.x_pos,self.y_pos))
        #settings
        self.enemy_speed = 2.1
        self.health = 125
        self.died = False
        self.closest = []
        self.updateTime = pygame.time.get_ticks()
        self.Anim_cd = 200
        #dmg
        self.dmgAnim = False
        self.dmgAnimCD = 0

    def update(self,screen,player,bullet_group,trail):
        trail_vec = pygame.math.Vector2(player.center)
        closest = 0
        for i,t in enumerate(trail):
            x_dist = self.rect.center[0] - t.rect.center[0] + 0.000001
            y_dist = t.rect.center[1] - self.rect.center[1] + 0.000001
            dist = ((x_dist) ** 2 + (y_dist) ** 2) ** (1 / 2)
            if closest == 0:
                closest = dist
            if dist < closest:
                closest = dist
                trail_vec = pygame.math.Vector2(t.rect.center)
            if len(trail)==1:
                trail_vec = pygame.math.Vector2(t.rect.center)
        if len(trail) == 0:
            self.enemy_speed = 5.2

        boss_vec = pygame.math.Vector2(self.rect.center)
        dir = (trail_vec - boss_vec).normalize()
        self.rect.left += dir[0] * self.enemy_speed
        self.rect.top += dir[1] * self.enemy_speed
        #Clean up mechanics
        trail.draw(screen)
        pygame.sprite.spritecollide(self,trail,True)
        #animate boss
        if pygame.time.get_ticks() - self.updateTime > self.Anim_cd:
            self.animate()
            self.updateTime = pygame.time.get_ticks()
        # Boss hit animation
        if pygame.sprite.spritecollide(self, bullet_group, True):
            self.health -= 1
            self.dmgAnim = True
        if self.health == 0:
            self.died = True
        if self.dmgAnim == True:
            imgCopy = self.image.copy()
            imgCopy.fill("Red", special_flags=pygame.BLEND_RGBA_MULT)
            if self.dmgAnimCD <= 50:
                screen.blit(imgCopy, self.rect)
                self.dmgAnimCD += 1
            elif self.dmgAnimCD > 50:
                self.dmgAnim = False
                self.dmgAnimCD = 0
                screen.blit(self.image, self.rect)
        elif self.dmgAnim == False or self.died == False:
            screen.blit(self.image, self.rect)
        # boss name
        text_size = 30
        font = pygame.font.Font("PressStart2P.ttf", text_size)
        text = "\"The Cleaner\""
        text_render = font.render(text, False, "Black")
        width, height = font.size(text)
        screen.blit(text_render, (screen_width // 2 - (width // 2), 20))
        # health
        for i in range(1, self.health + 1):
            health_surf = pygame.Surface((10, 15))
            screen.blit(health_surf, (screen_width // 2 - 650 + (i * health_surf.get_width()), height + 40))

    def animate(self):
        if self.CurrFrame == len(self.imgs)-1:
            self.CurrFrame = 0
            self.image = self.imgs[self.CurrFrame].convert_alpha()
        else:
            self.CurrFrame += 1
            self.image  = self.imgs[self.CurrFrame].convert_alpha()

class Boss3(Sprite):
    def __init__(self):
        super().__init__()
        self.scaleImgTo = 75
        # imgs
        self.frame = 0
        self.imgs = [pygame.image.load("mom3.png").convert_alpha(),pygame.image.load("mom4.png").convert_alpha(), pygame.image.load("mom5.png").convert_alpha()]
        self.image = self.imgs[self.frame]
        self.image = pygame.transform.scale(self.image, (self.scaleImgTo, self.scaleImgTo))
        # spawn
        self.x_pos = random.randint(-self.image.get_width(), screen_width + self.image.get_width())
        self.y_pos = random.choices([-self.image.get_height(), screen_height + self.image.get_height()])
        self.y_pos = self.y_pos[0]
        self.rect = self.image.get_rect(topleft=(self.x_pos, self.y_pos))
        self.enemy_speed = 3
        self.health = 100
        self.died = False
        self.boss_bullet = pygame.sprite.Group()
        self.second_bullet = pygame.sprite.Group()
        #special atk
        self.boss_shooting = False
        self.atk_cd = 1000
        self.update_time = pygame.time.get_ticks()
        #2nd special atk
        self.projectile_group = pygame.sprite.Group()
        #stop cooldown
        self.walk_cd = 2000
        self.update_stop_time = pygame.time.get_ticks()
        self.stopping_cd = 0
        #dmg animation
        self.updateTime = pygame.time.get_ticks()
        self.dmgAnim = False
        self.dmgAnimCD = 0
        self.Anim_cd = 90

    def update(self,screen,player,bullet_group):
        player_vec = pygame.math.Vector2(player.center)
        boss_vec = pygame.math.Vector2(self.rect.center)
        dir = (player_vec - boss_vec).normalize()
        if pygame.time.get_ticks() - self.update_stop_time < self.walk_cd:
            self.rect.left += dir[0] * self.enemy_speed
            self.rect.top += dir[1] * self.enemy_speed
        if pygame.time.get_ticks() - self.update_stop_time > self.walk_cd:
            self.stopping_cd += 15
            if self.stopping_cd == 900:
                self.update_stop_time = pygame.time.get_ticks()
                self.stopping_cd = 0
                for x in range(-4, 5, 4):
                    if x ==-4 or x == 4:
                        for y in range(-4, 5, 4):
                            p = Projectiles(self.rect,x,y)
                            self.projectile_group.add(p)
        # animate boss
        if pygame.time.get_ticks() - self.updateTime > self.Anim_cd:
            self.animate()
            self.updateTime = pygame.time.get_ticks()
        # Boss hit animation
        if pygame.sprite.spritecollide(self, bullet_group, True):
            self.health -= 1
            self.dmgAnim = True
        if self.health == 0:
            self.died = True
        if self.dmgAnim == True:
            imgCopy = self.image.copy()
            imgCopy.fill("Red", special_flags=pygame.BLEND_RGBA_MULT)
            if self.dmgAnimCD <= 50:
                screen.blit(imgCopy, self.rect)
                self.dmgAnimCD += 1
            elif self.dmgAnimCD > 50:
                self.dmgAnim = False
                self.dmgAnimCD = 0
                screen.blit(self.image, self.rect)
        elif self.dmgAnim == False or self.died == False:
            screen.blit(self.image, self.rect)
            # boss name
        text_size = 30
        font = pygame.font.Font("PressStart2P.ttf", text_size)
        text = "One Angry Mom"
        text_render = font.render(text, False, "Black")
        width, height = font.size(text)
        screen.blit(text_render, (screen_width // 2 - (width // 2), 20))
        # health
        for i in range(1, self.health + 1):
            health_surf = pygame.Surface((10, 15))
            screen.blit(health_surf, (screen_width // 2 - 550 + (i * health_surf.get_width()), height + 40))

    def boss_shoot(self,player,screen):
        if pygame.time.get_ticks() - self.update_time > self.atk_cd and self.boss_shooting == False:
            self.boss_shooting = True
            self.update_time = pygame.time.get_ticks()
            for i in range(1,3):
                s = ThirdBoss_Bullet(self.rect, player,i)
                self.boss_bullet.add(s)
        self.boss_bullet.update()
        self.boss_bullet.draw(screen)
        if pygame.time.get_ticks() - self.update_time < self.atk_cd:
            self.boss_shooting = False

    def circular_atk(self,screen):
        self.projectile_group.update()
        self.projectile_group.draw(screen)

    def animate(self):
        if self.frame == len(self.imgs)-1:
            self.frame = 0
            self.image = self.imgs[self.frame].convert_alpha()
        else:
            self.frame += 1
            self.image  = self.imgs[self.frame].convert_alpha()

class ThirdBoss_Bullet(Sprite):
    def __init__(self,boss_pos,player_pos,dir):
        super().__init__()
        self.image = pygame.image.load("heart0.png").convert_alpha()
        self.image = pygame.transform.scale(self.image,(20,20))
        self.boss_pos = boss_pos
        self.rect = self.image.get_rect(midleft=(self.boss_pos.midleft[0],self.boss_pos.midleft[1]))
        self.player_pos = player_pos
        self.x_dist = self.player_pos.midleft[0] - self.boss_pos.midleft[0] + 0.000001
        self.y_dist = self.player_pos.midleft[1] - self.boss_pos.midleft[1] + 0.000001
        self.rad = math.atan2(self.y_dist, self.x_dist)
        self.dx = math.cos(self.rad)
        self.dy = math.sin(self.rad)
        self.bullet_speed = 11
        self.dir = dir

    def update(self):
        self.rect.left += self.dx * self.bullet_speed + self.dir
        self.rect.top += self.dy * self.bullet_speed
        if self.rect.right < 0 or self.rect.top > screen_height or self.rect.bottom < 0 or self.rect.left > screen_width:
            self.kill()

class Projectiles(Sprite):
    def __init__(self,boss_pos,dirx,diry):
        super().__init__()
        self.image = pygame.image.load("heart0.png").convert_alpha()
        self.image = pygame.transform.scale(self.image,(90, 90))
        self.boss_pos = boss_pos
        self.rect = self.image.get_rect(midleft=(self.boss_pos.midleft[0],self.boss_pos.midleft[1]))
        self.dirx = dirx
        self.diry =diry

    def update(self):
        self.rect.left += self.dirx * 1.6
        self.rect.top += self.diry * 1.6
        if self.rect.right < 0 or self.rect.top > screen_height or self.rect.bottom < 0 or self.rect.left > screen_width:
            self.kill()

#LEVEL IMPORTS------------------------------------------------------#
#scenes, menu,game over
class Intro:
    def __init__(self):
        self.text = Texts()
        self.main_char = main_char()
        self.banker_boss = banker_boss()
        self.mom = Mom()
        self.pressed_Space = False
    def run(self,screen):
        # next screen
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.pressed_Space == False:
            self.pressed_Space = True
        if self.pressed_Space == True:
            self.text.howToPlay(screen)
        else:
            self.text.display_Title(screen)
            self.text.P2Play(screen)
            # characters
            self.main_char.animate(screen)
            self.banker_boss.animate(screen)
            self.mom.animate(screen)
class GameOver:
    def __init__(self):
        self.gamOverScene = gameOverDialogues()
    def run(self,screen):
        self.gamOverScene.DialogAnim(screen)
class lvl1Scenes:
    def __init__(self):
        self.main_char = Lvl1_main_char()

    def run(self,screen):
        self.main_char.animate(screen)

class preLvl1Boss_Scene:
    def __init__(self):
        self.dialogs = Dialogues()
        self.anims = charAnims()
    def run(self,screen):
        self.dialogs.displayTexts(screen)
        self.anims.animate(screen,self.dialogs)

class prelvl2Scene:
    def __init__(self):
        self.dialogues = preLvl2Dialogues()
    def run(self,screen):
        self.dialogues.DialogAnim(screen)

class prelvl2BossScene():
    def __init__(self):
        self.dialogues = preLvl2BossDialogues()
    def run(self,screen):
        self.dialogues.DialogAnim(screen)

class prelvl3Scene():
    def __init__(self):
        self.dialogues = preLvl3Dialogues()
    def run(self,screen):
        self.dialogues.DialogAnim(screen)
class preLvl3BossScene():
    def __init__(self):
        self.dialogues = preLvl3BossDialogues()
    def run(self,screen):
        self.dialogues.DialogAnim(screen)
class gameEnd_Scene():
    def __init__(self):
        self.dialogues = gameEndDialogues()
    def run(self,screen):
        self.dialogues.DialogAnim(screen)

#playable levels
class Level:
    def __init__(self):
        self.player = Player()
        #enemy
        self.enemy = Spawn_Enemy()

    def run(self,screen):
        self.player.get_input()
        self.player.update(screen,self.enemy)
        self.player.shoot()
        #enemy
        self.enemy.spawn(screen,self.player.player,self.player.bullet_group)

class Level2:
    def __init__(self):
        self.player = Player()
        self.spawn_enemy = Spawn_lvl2Enemy()
        self.trails = trail_group

    def run(self,screen):
        self.player.get_input()
        self.player.updateForLvl2Enemy(screen,self.spawn_enemy,self.trails)
        self.player.shoot()
        self.spawn_enemy.spawn(screen,self.player.player,self.player.bullet_group)

class Level3:
    def __init__(self):
        self.player = Player()
        self.spawn_enemy = Spawn_lvl3Enemy()


    def run(self,screen):
        #enemies & its special atks
        self.spawn_enemy.spawn(screen,self.player.player,self.player.bullet_group)
        self.spawn_enemy.shoot(self.player.player,screen)
        #player
        self.player.get_input()
        self.player.updateForLvl3Enemy(screen, self.spawn_enemy)
        self.player.shoot()

class Boss1Level:
    def __init__(self):
        self.player = Player()
        self.boss = Boss1()
        self.update_time = pygame.time.get_ticks()
        self.special_atk_cd = 1500
    def run(self,screen):
        self.player.get_input()
        self.player.updateForBoss(screen,self.boss)
        self.player.shoot()
        #Boss
        self.boss.update(screen,self.player.player,self.player.bullet_group)
        self.boss.boss_shoot(self.player.player,screen)

class Boss2Level:
    def __init__(self):
        self.player = Player()
        self.boss = Boss2()
        self.trails = Spawn_lvl2Enemy()
    def run(self,screen):
        self.player.get_input()
        self.player.updateForBoss2(screen,self.boss,trail_group)
        self.player.shoot()
        #Boss
        self.boss.update(screen,self.player.player,self.player.bullet_group,trail_group)
        self.trails.spawnTrailsOnly(screen)

class Boss3Level:
    def __init__(self):
        self.player = Player()
        self.boss = Boss3()
    def run(self,screen):
        self.player.get_input()
        self.player.updateForLvl3Boss(screen,self.boss)
        self.player.shoot()
        #Boss
        self.boss.update(screen,self.player.player,self.player.bullet_group)
        self.boss.boss_shoot(self.player.player, screen)
        self.boss.circular_atk(screen)


#MAIN GAME--------------#
#scenes
MainMenu = Intro()
gameover = GameOver()
lvl1Scenes = lvl1Scenes()
prelvl1BossScene = preLvl1Boss_Scene()
prelvl2Scene = prelvl2Scene()
prelvl2BossScene = prelvl2BossScene()
prelvl3 = prelvl3Scene()
prelvl3BossScene = preLvl3BossScene()
gameEndScene = gameEnd_Scene()
#levels
level = Level()
level2 = Level2()
level3 = Level3()
#bosses
boss1 = Boss1Level()
boss2 = Boss2Level()
boss3 = Boss3Level()
class GameState():
    def __init__(self):
        self.state = "intro"
        self.pressed = False
        self.last_state = ""
        self.keys = pygame.key.get_pressed()
        #background music
        self.sound = pygame.mixer.Sound("Sweet Crazy.WAV")
        self.sound.set_volume(1)
        self.last_song = ""
        self.last_volume = 0

    #Scenes
    def intro(self):
        screen.fill((140,2,239))
        MainMenu.run(screen)
        self.sound.play(-1)
        if MainMenu.text.next_screen == True:
            self.state = "lvl1_scenes"
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()

    def game_over(self):
        self.sound.play(-1)
        screen.fill((230,230,0))
        gameover.run(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()
        #load last game
        if gameover.gamOverScene.finish_dialog == True:
            self.state = self.last_state
            self.sound.stop()
            self.sound = pygame.mixer.Sound(self.last_song)
            self.sound.set_volume(self.last_volume)


    def gameEnd(self):
        self.sound.play(-1)
        screen.fill((125,200,220))
        gameEndScene.run(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()
    def lvl1_scenes(self):
        screen.fill((102,0,204))
        lvl1Scenes.run(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()
        if lvl1Scenes.main_char.lvl1_txts.finish_dialog ==True:
            self.state = "lvl_1"
            self.sound.stop()
            self.sound = pygame.mixer.Sound("Fire in the Hole.mp3")
            self.sound.set_volume(0.1)

    def prelvl1_bossScene(self):
        self.sound.play(-1)
        screen.fill("orange")
        prelvl1BossScene.run(screen)
        if prelvl1BossScene.dialogs.finish_dialog == True:
            self.state = "lvl_1_boss"
            self.sound.stop()
            self.sound = pygame.mixer.Sound("The Apparition.mp3")
            self.sound.set_volume(0.1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()

    def preLvl2Scene(self):
        self.sound.play(-1)
        screen.fill((164,238,255))
        prelvl2Scene.run(screen)
        if prelvl2Scene.dialogues.finish_dialog == True:
            self.state = "lvl2"
            self.sound.stop()
            self.sound = pygame.mixer.Sound("Rivaling Force.mp3")
            self.sound.set_volume(0.06)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()
    def preLvl2BossScene(self):
        self.sound.play(-1)
        screen.fill("pink")
        prelvl2BossScene.run(screen)
        if prelvl2BossScene.dialogues.finish_dialog == True:
            self.state = "lvl2_boss"
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()
    def prelvl3Scene(self):
        self.sound.play(-1)
        screen.fill("gray")
        prelvl3.run(screen)
        if prelvl3.dialogues.finish_dialog == True:
            self.state = "lvl3"
            self.sound.stop()
            self.sound = pygame.mixer.Sound("Coffee Break.mp3")
            self.sound.set_volume(0.06)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()

    def prelvl3Boss(self):
        screen.fill((120,220,240))
        prelvl3BossScene.run(screen)
        if prelvl3BossScene.dialogues.finish_dialog == True:
            self.state = 'lvl3_boss'
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()

    #Playable levels
    def lvl_1(self):
        self.sound.play(-1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill("white")
        level.run(screen)
        pygame.display.update()

        if level.enemy.total_enemies == 195:
            self.state ='prelvl1_bossScene'
            self.sound.stop()
            self.sound = pygame.mixer.Sound("Sure Forever.WAV")
            self.sound.set_volume(0.6)
        elif level.player.dues <= 0:
            self.state = "gameOver"
            self.last_state = "lvl_1"
            level.enemy.total_enemies = 0
            level.player.dues = 10000
            #sound
            self.sound.stop()
            self.sound = pygame.mixer.Sound("Null and Void.mp3")
            self.sound.set_volume(0.1)
            self.last_volume = 0.1
            self.last_song = "Fire in the Hole.mp3"

    def lvl_2(self):
        self.sound.play(-1)
        screen.fill("white")
        level2.run(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()

        if level2.spawn_enemy.total_enemies == 95:
            for remaining_enemies in level2.spawn_enemy.enemy_group:
                remaining_enemies.kill()
            self.state = "preLvl2Boss"
            self.sound.stop()
            self.sound = pygame.mixer.Sound("Against All Odds.mp3")
            self.sound.set_volume(0.06)
        elif level2.player.health == 0 or level2.player.TrashTakenOut == 0:
            self.last_state = "lvl2"
            level2.spawn_enemy.total_enemies = 0
            level2.player.health = 10
            level2.player.TrashTakenOut = 10
            for remaining_enemies in level2.spawn_enemy.enemy_group:
                remaining_enemies.kill()
            for remaining_enemies in level2.spawn_enemy.enemy_group2:
                remaining_enemies.kill()
            for t in trail_group:
                t.kill()
            self.state = "gameOver"
            self.sound.stop()
            self.sound = pygame.mixer.Sound("Null and Void.mp3")
            self.sound.set_volume(0.1)
            self.last_volume = 0.06
            self.last_song = "Rivaling Force.mp3"

    def lvl3(self):
        self.sound.play(-1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()
        screen.fill("white")
        level3.run(screen)
        if level3.spawn_enemy.total_enemies == 115:
            for remaining_enemies in level3.spawn_enemy.enemy_group:
                remaining_enemies.kill()
            self.state = "prelvl3Boss"
            self.sound.stop()
            self.sound = pygame.mixer.Sound("Ex Machina.mp3")
            self.sound.set_volume(0.06)
        elif level3.player.hearts == 32:
            level3.spawn_enemy.total_enemies = 0
            level3.player.hearts = 0
            for remaining in level3.spawn_enemy.enemy_group:
                remaining.kill()
            for remaining in level3.spawn_enemy.enemy_bullet_group:
                remaining.kill()
            self.last_state = "lvl3"
            self.state = "gameOver"
            self.sound.stop()
            self.sound = pygame.mixer.Sound("Null and Void.mp3")
            self.sound.set_volume(0.1)
            self.last_volume = 0.06
            self.last_song = "Coffee Break.mp3"
    #Bosses
    def lvl_1_boss(self):
        self.sound.play(-1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill("white")
        boss1.run(screen)
        if boss1.boss.died == True:
            self.state = "preLvl2Scene"
            self.sound.stop()
            self.sound = pygame.mixer.Sound("Bounty Hunter.mp3")
            self.sound.set_volume(0.06)
        elif boss1.player.IRSdues <= 0:
            self.state = "gameOver"
            self.last_state = "lvl_1_boss"
            boss1.player.IRSdues = 100000
            boss1.boss.health = 100
            self.sound.stop()
            self.sound = pygame.mixer.Sound("Null and Void.mp3")
            self.sound.set_volume(0.1)
            self.last_volume = 0.1
            self.last_song = "The Apparition.mp3"
        pygame.display.update()

    def lvl2_boss(self):
        self.sound.play(-1)
        global trail_group
        screen.fill("white")
        boss2.run(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if boss2.boss.died == True:
            self.state = "prelvl3Scene"
            self.sound.stop()
            self.sound = pygame.mixer.Sound("Stray Cat.mp3")
            self.sound.set_volume(0.06)
        elif boss2.player.lvl2_hearts == 0:
            boss2.player.lvl2_hearts = 10
            boss2.boss.health = 120
            self.last_state = "lvl2_boss"
            self.state = "gameOver"
            self.sound.stop()
            self.sound = pygame.mixer.Sound("Null and Void.mp3")
            self.sound.set_volume(0.1)
            self.last_volume = 0.06
            self.last_song = "Against All Odds.mp3"
        pygame.display.update()

    def lvl3_boss(self):
        self.sound.play(-1)
        screen.fill("white")
        boss3.run(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if boss3.boss.died == True:
            self.state = "gameEnd"
            self.sound.stop()
            self.sound = pygame.mixer.Sound("Thought Soup.mp3")
            self.sound.set_volume(0.06)
        elif boss3.player.life == 0:
            self.sound.stop()
            self.sound = pygame.mixer.Sound("Null and Void.mp3")
            self.sound.set_volume(0.1)
            self.last_state = "lvl3_boss"
            self.state = "gameOver"
            self.last_song ="Ex Machina.mp3"
            self.last_volume = 0.06
            boss3.boss.health = 100
            boss3.player.life = 10
        pygame.display.update()

    def state_manager(self):
        #scenes
        if self.state == 'intro':
            self.intro()
        if self.state =='lvl1_scenes':
            self.lvl1_scenes()
        if self.state =='prelvl1_bossScene':
            self.prelvl1_bossScene()
        if self.state =="preLvl2Scene":
            self.preLvl2Scene()
        if self.state == "preLvl2Boss":
            self.preLvl2BossScene()
        if self.state == "prelvl3Scene":
            self.prelvl3Scene()
        if self.state == "prelvl3Boss":
            self.prelvl3Boss()
        if self.state == "gameEnd":
            self.gameEnd()
        #playable levels
        if self.state =='lvl_1':
            self.lvl_1()
        if self.state == 'lvl2':
            self.lvl_2()
        if self.state == 'lvl3':
            self.lvl3()
        #bosses
        if self.state == 'lvl_1_boss':
            self.lvl_1_boss()
        if self.state =='lvl2_boss':
            self.lvl2_boss()
        if self.state =='lvl3_boss':
            self.lvl3_boss()
        if self.state =='gameOver':
            self.game_over()

game_state = GameState()
async def main():
    while True:
        game_state.state_manager()
        clock.tick(100)
        await asyncio.sleep(0)
asyncio.run(main())
