import pygame
import math
pygame.init()

screen_width, screen_height = 1440, 720
screen = pygame.display.set_mode((screen_width, screen_height))

# 加载并缩放图片
scaled_image = pygame.transform.scale(pygame.image.load('pic/block.png'), (64, 64))

# 方块类
class Block:
    def __init__(self, pos, target_pos):
        self.image = scaled_image
        self.rect = self.image.get_rect(center=pos)
        self.speed = [0.1, -0.3]
        self.acc = [0, 0.0002]
        self.pos = pos
        rad = self.calc_degree(pos, target_pos)
        self.speed[0] += 0.3 * math.cos(rad)
        self.speed[1] += 0.3 * math.sin(rad)

    def update(self):
        self.speed[0] += self.acc[0]
        self.speed[1] += self.acc[1]
        self.pos[0] += self.speed[0]
        self.pos[1] += self.speed[1]
        self.rect.x, self.rect.y = self.pos
        if self.rect.right > screen_width:
            self.speed[0] = -self.speed[0]
        if self.rect.y < 0:
            self.speed[1] = -self.speed[1]
        if self.rect.bottom > screen_height and self.rect.x > screen_width/2:
             self.speed = [0,0]
             self.acc = [0,0]

    
    def calc_degree(self, ori, tar) :
        dx = tar[0] - ori[0]
        dy = tar[1] - ori[1]
        if dx == 0 and dy == 0:
            return math.atan2(1, 0)
        return math.atan2(dy, dx)

# 存储所有方块
blocks = []

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 左键点击
            # 在鼠标位置发射方块
            mouse_pos = pygame.mouse.get_pos()
            blocks.append(Block([0, screen_height], mouse_pos))

    screen.fill((0, 0, 0))  # 填充背景

    # 更新并绘制所有方块
    for block in blocks[:]:  # 使用切片避免修改列表时的错误
        block.update()
        screen.blit(block.image, block.rect)

    pygame.display.flip()

pygame.quit()