# coding=utf-8
from activity import *
from plane_class_method import *


class GameActivity(Activity):
    MAXFPS = 30

    def __init__(self, screen, background_fn):
        Activity.__init__(self, screen, background_fn)

        self.achievement_sound = load_sound(constants.achievement_sound_fn)
        # 打破记录时的音效
        self.game_bgm = load_sound(constants.game_bgm_fn)
        self.takeoff_sound = load_sound(constants.takeoff_sound_fn)
        self.bullet_sound = load_sound(constants.launch_bullet_sound_fn)
        self.short_boom_sound = load_sound(constants.short_boom_sound_fn)
        self.great_boom_sound = load_sound(constants.great_boom_sound_fn)
        self.launch_bomb_sound = load_sound(constants.launch_bomb_sound_fn)
        self.baozou_sound = load_sound(constants.plane_thrash_sound_fn)
        self.plane_explode_sound = load_sound(constants.plane_explo_sound_fn)
        self.enemy_appear_sound = load_sound(constants.enemy3_appear_sound_fn)

        # font
        self.font = load_font(constants.font_fn, constants.font_size)
        self.show_score_font = load_font(constants.show_score_font_fn, 50)
        self.lose_a_life = False
        self.collide_mask = pygame.sprite.collide_mask

        self._life_count = 0
        self._bomb_count = 0
        self._tick_count = 0
        self._boss_count = 0

    def setup(self):

        self.boss = Boss()
        self.bubble = bubble()
        self.allSprites = MyGroup()
        self.enemy1_group = pygame.sprite.RenderPlain()
        self.enemy2_group = pygame.sprite.RenderPlain()
        self.enemy3_group = pygame.sprite.RenderPlain()
        self.boss_group = MyGroup()
        self.all_enemies = MyGroup()
        self.no_colli_group = MyGroup()

        self.bullet_group = pygame.sprite.RenderPlain()
        self.bullet1_group = pygame.sprite.RenderPlain()
        self.bullet2_group = pygame.sprite.RenderPlain()
        self.bullet3_group = pygame.sprite.RenderPlain()

        self.enemy_bullets = pygame.sprite.RenderPlain()

        ##---------炸弹-------####
        self.bomb_group = pygame.sprite.RenderPlain()
        bomb_icon_y = self.screen.get_rect().height - 175
        self.bomb_location_group = ((20, bomb_icon_y), (50, bomb_icon_y), (80, bomb_icon_y), (110, bomb_icon_y))

        self.bomb_icon_group = [BombIcon(x) for x in self.bomb_location_group]
        # 创建炸弹图标的列表

        self.plane = Plane()
        self.plane.add(self.allSprites)

        plane_icon_y = self.screen.get_rect().height - 175
        self.plane_location_group = ((388, plane_icon_y), (388 + 30, plane_icon_y), (388 + 60, plane_icon_y))
        self.plane_icon_group = [PlaneIcon(x) for x in self.plane_location_group]

        # 初始化飞机图标列表
        self.ufo1 = UFO1()
        self.ufo2 = UFO2()
        self.float_bubble = floatBubble()
        self.ufo1_group = pygame.sprite.RenderPlain()
        self.ufo2_group = pygame.sprite.RenderPlain()
        self.ufo_group = pygame.sprite.RenderPlain()
        self.float_bubble_group = pygame.sprite.RenderPlain()
        self.ufo1.add(self.ufo_group, self.ufo1_group, self.allSprites)
        self.ufo2.add(self.ufo_group, self.ufo2_group, self.allSprites)
        self.float_bubble.add(self.ufo_group, self.float_bubble_group, self.allSprites)

        self.score = 0
        # 记录分数
        self.pause = False
        self.gameover = False

        # set volume
        self.game_bgm.set_volume(1.0)
        self.bullet_sound.set_volume(0.2)
        self.great_boom_sound.set_volume(0.2)
        self.short_boom_sound.set_volume(0.2)
        self.enemy_appear_sound.set_volume(0.2)

        Enemy.enemy_down1_pic = load_image(constants.enemy1_down1_fn, alpha=True)[0]
        Enemy.enemy_down2_pic = load_image(constants.enemy1_down2_fn, alpha=True)[0]
        Enemy.enemy_down3_pic = load_image(constants.enemy1_down3_fn, alpha=True)[0]
        Enemy.enemy_down4_pic = load_image(constants.enemy1_down4_fn, alpha=True)[0]
        # Enemy2.enemy_down1_pic = load_image(constants.enemy1_down1_fn, alpha=True)[0]
        # Enemy2.enemy_down2_pic = load_image(constants.enemy1_down2_fn, alpha=True)[0]
        # Enemy2.enemy_down3_pic = load_image(constants.enemy1_down3_fn, alpha=True)[0]
        # Enemy2.enemy_down4_pic = load_image(constants.enemy1_down4_fn, alpha=True)[0]
        # Enemy3.enemy_down1_pic = load_image(constants.enemy1_down1_fn, alpha=True)[0]
        # Enemy3.enemy_down2_pic = load_image(constants.enemy1_down2_fn, alpha=True)[0]
        # Enemy3.enemy_down3_pic = load_image(constants.enemy1_down3_fn, alpha=True)[0]
        # Enemy3.enemy_down4_pic = load_image(constants.enemy1_down4_fn, alpha=True)[0]

        pygame.mouse.set_visible(False)

    def settimers(self):
        pygame.time.set_timer(constants.ENEMY_APPEAR_EVENT, constants.enemy12_interval)
        pygame.time.set_timer(constants.BULLET_SHOOT_EVENT, 100)
        self.timer_ufo1 = threading.Timer(constants.ufo1_interval, self.ufo1_appear, ())
        self.timer_ufo1.start()
        self.timer_ufo2 = threading.Timer(constants.ufo2_interval, self.ufo2_appear, ())
        self.timer_ufo2.start()
        self.timer_bubble = threading.Timer(constants.bubble_interval, self.bubble_appear, ())
        self.timer_bubble.start()
        self.timer_e3 = threading.Timer(constants.enemy3_interval, self.enemy3_appear, ())
        self.timer_e3.start()

    def run(self):
        self.screen.blit(self.background, (0, 0))
        self.setup()
        self.settimers()
        pygame.display.update()
        self.game_bgm.play(loops=-1)
        while True:
            self.change_level()
            self.clock.tick(MAXFPS)
            self.handle_events()
            self.detect_collision()
            self.draw_spirites()
            if self.quit:
                self.finished()
                #pygame.time.wait()
                break

    def handle_events(self):
        for event in self.get_event():
            if event.type == pygame.KEYDOWN:
                if event.key == K_SPACE and len(self.bomb_group) < 4:
                    if len(self.bomb_icon_group) > 0:
                        Bomb().add(self.bomb_group, self.allSprites)
                        self.bomb_icon_group.pop(-1)
                        self.score += 500
                        # 如果按下空格键，那么发射一枚炸弹,播放音效
                if event.key == K_v:
                    if not self.pause:
                        self.allSprites.suspend()
                        pygame.mixer.pause()
                    else:
                        pygame.mixer.unpause()
                        self.allSprites.recover()
                    self.pause = not self.pause
                # if event.key == K_a:
                #     self.bubble.activate()
                #     self.plane.enable_shield()
                    # self.bubble.add(self.allSprites)
                # if self.pause:
                #     self.allSprites.suspend()
                #     pygame.mixer.pause()

            elif event.type == constants.ENEMY_APPEAR_EVENT:
                if not self.pause:
                    if len(self.enemy1_group) <= self.max_enemy1:
                        Enemy1().add(self.enemy1_group, self.all_enemies, self.allSprites, self.no_colli_group)
                    for e in self.enemy1_group.sprites():
                        if not e.active:
                            e.activate()
                    if len(self.enemy2_group) <= self.max_enemy2:
                        Enemy2().add(self.enemy2_group, self.all_enemies, self.allSprites, self.no_colli_group)
                        self.enemy_appear_sound.play()
                    for e in self.enemy2_group.sprites():
                        if not e.active:
                            e.activate()

            elif event.type == constants.BULLET_SHOOT_EVENT:
                if not self.pause:
                    if len(self.bullet1_group) <= 10:
                        Bullet1().add(self.bullet1_group, self.bullet_group, self.allSprites)
                    if self.plane.has_bullet2 and len(self.bullet2_group) <= 10:
                        Bullet2(self.plane.rect.bottomleft).add(self.bullet2_group, self.bullet_group, self.allSprites)
                        Bullet2(self.plane.rect.bottomright).add(self.bullet2_group, self.bullet_group, self.allSprites)
                    if self.plane.has_bullet3 and len(self.bullet3_group) < 10:
                        Bullet3(self.plane.rect.topleft, direction=False).add(self.bullet3_group, self.bullet_group,
                                                                              self.allSprites)
                        Bullet3(self.plane.rect.topright, direction=True).add(self.bullet3_group, self.bullet_group,
                                                                              self.allSprites)

                    self.bullet_sound.play()

    def detect_collision(self):
        self.screen.blit(self.background, (0, 0))
        if not self.gameover and not self.pause:

            for enemy in pygame.sprite.groupcollide(self.all_enemies, self.bullet_group, 0, 1,
                                                    self.collide_mask).keys():
                if enemy in self.boss_group:
                    enemy.hurt()
                else:
                    if enemy in self.enemy1_group:
                        self.score += 100
                    elif enemy in self.enemy2_group:
                        self.score += 300
                    elif enemy in self.enemy3_group:
                        self.score += 500
                    enemy.explode()
                self.short_boom_sound.play()

            for bomb, enemies in pygame.sprite.groupcollide(self.bomb_group, self.all_enemies, 0, 0,
                                                            self.collide_mask).items():
                bomb.explode(self.no_colli_group)
                for enemy in enemies:
                    enemy.explode()
                self.great_boom_sound.play()

            for enemy in pygame.sprite.spritecollide(self.bubble, self.no_colli_group, 0, collided=self.collide_mask):
                if enemy not in self.boss_group:
                    enemy.explode()

            if not self.plane.invincible:
                for e in self.no_colli_group.sprites():
                    if pygame.sprite.collide_mask(self.plane, e):
                        pygame.time.wait(500)
                        for s in self.no_colli_group.sprites():
                            if s in self.boss_group:
                                pass
                            else:
                                s.kill()
                        self.plane.explode()
                        e.explode()
                        if len(self.plane_icon_group) > 0:
                            self.plane_icon_group.pop(0)
                        if self.plane.life > 0:
                            self.continue_tip = self.font.render("Press v to continue", True, (0, 0, 0))
                            self.screen.blit(self.continue_tip, (40, 500))
                            pygame.display.update()
                        self.plane_explode_sound.play()
                        self.great_boom_sound.play()
                        self.pause = True
                        break

            for ufo in pygame.sprite.spritecollide(self.plane, self.ufo_group, 0, collided=pygame.sprite.collide_mask):
                if ufo in self.ufo1_group:
                    ufo.restart()
                    self.plane.has_bullet2 = True
                    self.baozou_sound.play()
                    self.plane.reset_bullet2_timer()
                    threading.Timer(constants.bullet2_last, self.plane.lose_bullet2, ()).start()
                elif ufo in self.ufo2_group:
                    ufo.restart()
                    self.plane.has_bullet3 = True
                    self.baozou_sound.play()
                    self.plane.reset_bullet3_timer()
                    threading.Timer(constants.bullet3_last, self.plane.lose_bullet3, ()).start()
                elif ufo in self.float_bubble_group:
                    ufo.restart()
                    self.bubble.activate()
                    self.plane.enable_shield()
                    threading.Timer(constants.bubble_last, self.plane.disable_shield, (self.bubble, )).start()

        if self.plane.life <= 0:
            self.plane.kill()
            self.game_bgm.stop()
            self.update_highscore()
            self.show_score()
            self.quit = True

    def draw_spirites(self):
        if not self.pause:
            self._tick_count += 1
            if len(self.enemy_bullets) < 30 and self._tick_count % 300 == 0:
                for e in self.all_enemies.sprites():
                    if e.has_bullet_left():
                        e.shoot_bullet()
                        EnemyBullet(random.choice([e.rect.midbottom, e.rect.bottomleft, e.rect.bottomright]))\
                            .add(self.enemy_bullets, self.allSprites, self.no_colli_group)
                        self.bullet_sound.play()

            for e in self.enemy3_group.sprites():
                e.get_player_pos(self.plane)

            try:
                #draw the bubble
                if self.bubble.active:
                    self.bubble.update()
                    self.screen.blit(self.bubble.image, self.bubble.rect.topleft)
                self.allSprites.update()
                self.allSprites.draw(self.screen)
            except: pass

            for boss in self.boss_group.sprites():
                if boss.active:
                    hp_color = constants.COLORS['green'] if boss.gethealthy() else constants.COLORS['red']
                    endpos = (boss.rect.x + boss.rect.width * boss.get_energy_ratio(), boss.rect.y)
                    pygame.draw.line(self.screen, hp_color, boss.rect.topleft, endpos, 8)

            for bomb_list in self.bomb_icon_group:
                self.screen.blit(bomb_list.image, bomb_list.rect)

            for plane_list in self.plane_icon_group:
                self.screen.blit(plane_list.image, plane_list.rect)
            # 绘制炸弹图标和我军飞机小图标

            text = self.font.render("Score: %d" % self.score, 1, (0, 0, 100))
            self.screen.blit(text, (0, 0))
            pygame.display.update()

    def change_level(self):
        self.check_life_add()
        self.check_bomb_add()
        self.check_boss_add()
        if 0 <= self.score < 4000:
            self.max_enemy1 = 5
            self.max_enemy2 = 0
            self.max_enemy3 = 0
            constants.enemy3_chongci_dis = 500
        elif 4000 < self.score < 10000:
            self.max_enemy1 = 5
            self.max_enemy2 = 2
            self.max_enemy3 = 0
        elif 10000 < self.score < 18000:
            self.max_enemy1 = 2
            self.max_enemy2 = 0
            self.max_enemy3 = 2
            constants.enemy3_team = 2
            constants.enemy3_interval = 3.0
            constants.enemy3_chongci_dis = 400
        elif 18000 < self.score < 28000:
            self.max_enemy1 = 6
            self.max_enemy2 = 5
            self.max_enemy3 = 3
            constants.enemy3_team = 2
            constants.enemy3_interval = 3.0
        elif 40000 > self.score > 28000:
            self.max_enemy1 = 2
            self.max_enemy2 = 1
            self.max_enemy3 = 4
            constants.ufo1_interval = 23.0
            constants.ufo2_interval = 33.0
            constants.enemy3_chongci_dis = 300
            constants.enemy3_interval = 1.0
            constants.enemy3_team = 2
        elif 50000 > self.score > 40000:
            self.max_enemy1 = 2
            self.max_enemy2 = 10
            self.max_enemy3 = 0
            constants.enemy3_interval = 5.0
        elif 80000 > self.score > 50000:
            self.max_enemy1 = 0
            self.max_enemy2 = 8
            self.max_enemy3 = 3
            constants.enemy3_team = 3
            constants.enemy3_chongci_dis = 250
            constants.enemy3_interval = 1.0
        elif 100000 > self.score > 80000:
            self.max_enemy1 = 5
            self.max_enemy2 = 0
            self.max_enemy3 = 4
            constants.enemy3_team = 4
            constants.ufo1_interval = 30.0
            constants.ufo2_interval = 28.0
            constants.enemy3_interval = 2.0
            constants.enemy3_chongci_dis = 350
        elif 150000 > self.score > 100000:
            self.max_enemy1 = 20
            self.max_enemy2 = 0
            self.max_enemy3 = 0
            constants.ufo1_interval = 28.0
            constants.ufo2_interval = 20.0
            constants.enemy3_interval = 3.0
            constants.enemy3_chongci_dis = 180
        elif 200000 > self.score > 150000:
            self.max_enemy1 = 5
            self.max_enemy2 = 5
            self.max_enemy3 = 5
            constants.enemy3_team = 5
            constants.ufo1_interval = 25.0
            constants.ufo2_interval = 28.0
            constants.enemy3_interval = 2.0
            constants.enemy3_chongci_dis = 300
        elif self.score > 200000:
            self.max_enemy1 = 15
            self.max_enemy2 = 15
            self.max_enemy3 = 3
            constants.enemy3_team = 2
            constants.ufo1_interval = 40.0
            constants.ufo2_interval = 40.0
            constants.enemy3_interval = 1
            constants.enemy3_chongci_dis = 200
        else:
            pass

    def ufo1_appear(self):
        self.ufo1.active = True
        threading.Timer(constants.ufo1_interval, self.ufo1_appear, ()).start()

    def ufo2_appear(self):
        self.ufo2.active = True
        threading.Timer(constants.ufo2_interval, self.ufo2_appear, ()).start()

    def bubble_appear(self):
        self.float_bubble.active = True
        threading.Timer(constants.bubble_interval, self.bubble_appear, ()).start()

    def enemy3_appear(self):
        cnt = 0
        for _ in range(0, constants.enemy3_team):
            if len(self.enemy3_group) <= self.max_enemy3:
                Enemy3().add(self.enemy3_group, self.all_enemies, self.allSprites, self.no_colli_group)
                cnt += 1
        for e in self.enemy3_group:
            if cnt >= constants.enemy3_team:
                break
            if not e.active:
                e.activate()
                cnt += 1
        threading.Timer(constants.enemy3_interval, self.enemy3_appear, ()).start()

    def update_highscore(self):

        with open("high_score.txt", "r") as f:
            scores = f.readlines()
        scores = map(lambda x: int(x.strip()), scores)

        if len(scores) > 0 and self.score > max(scores) or len(scores) == 0:
            break_score = self.font.render("WOW,Break the score!", 1, (100, 100, 0))
            self.achievement_sound.play()
            self.screen.blit(break_score, (50, 300))

        if len(scores) > 0 and self.score > min(scores) or len(scores) == 0:
            scores.append(self.score)
            scores.sort(reverse=True)
            scores = scores[:10]

        scores = [str(x) + "\n" for x in scores]
        with open("high_score.txt", 'w') as f:
            f.writelines(scores)

            # 将最高分写入文件

    def show_score(self):
        score_get = self.show_score_font.render("The score is %d" % self.score, 1, (80, 90, 205))
        self.screen.blit(score_get, (30, 500))
        pygame.display.update()

    def finished(self):
        pygame.mouse.set_visible(True)
        pygame.time.set_timer(constants.ENEMY_APPEAR_EVENT, 0)
        pygame.time.set_timer(constants.BULLET_SHOOT_EVENT, 0)

        self.timer_ufo1.cancel()
        self.timer_ufo2.cancel()
        self.timer_e3.cancel()
        self.timer_bubble.cancel()
        pygame.event.set_blocked([constants.ENEMY_APPEAR_EVENT, constants.BULLET_SHOOT_EVENT])
        pygame.event.post(pygame.event.Event(constants.RESTART_EVENT))

    def check_boss_add(self):
        if self.score / 30000 > self._boss_count:
            self.add_boss()
            self._boss_count = self.score / 30000

    def add_boss(self):
        self.boss.activate()
        self.boss.add(self.boss_group, self.no_colli_group, self.allSprites, self.all_enemies)

    def check_life_add(self):

        if self.score / 50000 > self._life_count:
            self.add_life()
            self._life_count = self.score / 50000

    def add_life(self):
        if self.plane.life < 3:
            self.plane.life += 1
            self.plane_icon_group.insert(0, PlaneIcon(self.plane_location_group[2 - len(self.plane_icon_group)]))

    def check_bomb_add(self):
        if self.score / 20000 > self._bomb_count:
            self.add_bomb()
            self._bomb_count = self.score / 20000

    def add_bomb(self):
        if len(self.bomb_icon_group) < 4:
            self.bomb_icon_group.append(BombIcon(self.bomb_location_group[len(self.bomb_icon_group)]))

    def get_event(self):
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                self.quit = True
                #self.finished()
                #pygame.quit()
                #exit()
        return events
