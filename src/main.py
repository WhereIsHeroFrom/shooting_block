import pygame
import math
pygame.init()

screen_width, screen_height = 1408, 704
block_size = 64
screen = pygame.display.set_mode((screen_width, screen_height))

# 加载并缩放图片
scaled_image = pygame.transform.scale(pygame.image.load('pic/block.png'), (block_size, block_size))
back_image = pygame.transform.scale(pygame.image.load('pic/back.png'), (block_size, block_size))
images = []
for x in [2, 4, 8, 16, 32, 64]:
    image = pygame.transform.scale(pygame.image.load('pic/blocknum/%d.png' % x), (block_size, block_size))
    images.append(image)
        
class Block:
    def __init__(self, pos, target_pos, level):
        self.level = level
        self.image = images[self.level]
        self.rect = self.image.get_rect(center=pos)
        self.speed = [0.1, -0.3]
        self.acc = [0, 0.0002]
        self.pos = list(pos)
        self.active = True  # 新增状态标识  

        
        # 计算初始速度矢量
        rad = self.calc_degree(pos, target_pos)
        self.speed[0] += 0.3 * math.cos(rad)
        self.speed[1] += 0.3 * math.sin(rad)

    def update_movement(self, delta_time):
        if self.active:  # 仅活动方块需要更新物理运动
            self.speed[0] += self.acc[0] * delta_time
            self.speed[1] += self.acc[1] * delta_time
            self.pos[0] += self.speed[0] * delta_time
            self.pos[1] += self.speed[1] * delta_time
            self.rect.center = self.pos

    def calc_degree(self, ori, tar):
        dx = tar[0] - ori[0]
        dy = tar[1] - ori[1]
        return math.atan2(dy, dx) if dx or dy else math.atan2(1, 0)

    def is_horizontal_collision(self, received):
        dx = min(self.rect.right, received.rect.right) - max(self.rect.left, received.rect.left)
        dy = min(self.rect.bottom, received.rect.bottom) - max(self.rect.top, received.rect.top)
        return dx <= dy
    
    def level_up(self):
        if self.level < 5:
            self.level += 1
            self.image = images[self.level]
            return True
        return False
    
# 分离为两个列表
active_blocks = []  # 发射中的方块
received_blocks = []  # 已接收的方块

back_blocks = {}
for i in range(screen_height//block_size):
    for j in range(screen_width//2//block_size):
        rect = pygame.rect.Rect(screen_width//2 + j*block_size, i*block_size, block_size, block_size)
        back_blocks[ (i,j) ] = rect
    
running = True
clock = pygame.time.Clock()
delta_time = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            import random
            level = random.randint(0, 2)
            active_blocks.append(Block([0, screen_height], mouse_pos, level))

    screen.fill((0, 0, 0))

    # 临时存储需要转移的方块
    to_receive = []
    
    # 更新活动方块
    for block in active_blocks[:]:
        block.update_movement(delta_time)
        
        # 保留原始边界碰撞逻辑
        if block.rect.right > screen_width:
            block.speed[0] = -abs(block.speed[0])
        if block.rect.left < 0:
            block.speed[0] = abs(block.speed[0])
        if block.rect.top < 0:
            block.speed[1] = abs(block.speed[1])
        
        # 下边界接收条件（保持原始逻辑）
        if block.rect.bottom > screen_height and block.rect.x > screen_width/2:
            block.speed = [0, 0]
            block.acc = [0, 0]
            block.active = False
            to_receive.append(block)
        
        # 与已接收方块的碰撞检测[1,3]
        for received in received_blocks:
            if block.rect.colliderect(received.rect):
                if block.level == received.level:
                    active_blocks.remove(block)
                    received.level_up()
                    break
                if block.is_horizontal_collision(received):
                    block.speed[0] = 0
                    block.acc[0] = 0
                else:
                    block.speed = [0, 0]
                    block.acc = [0, 0]
                    block.active = False
                    to_receive.append(block)
                    break

    # 转移符合条件的方块
    for block in to_receive:
        if block in active_blocks:
            active_blocks.remove(block)
            received_blocks.append(block)
    
    received_blocks.sort(key = lambda b : b.rect.y)
    rb_len = len(received_blocks)
    for i in range(rb_len):
        flag = False
        a = received_blocks[i]
        for j in range(i+1, rb_len):
            b = received_blocks[j]
            if a.level != b.level:
                continue
            if a.rect.colliderect(b.rect):
                if b.level_up():
                    received_blocks.remove(a)
                    flag = True
                    break
        if flag:
            break

    for (i,j), rect in back_blocks.items():
        screen.blit(back_image, rect)

    # 绘制所有方块
    for block in active_blocks:
        screen.blit(block.image, block.rect)
    for block in received_blocks:
        screen.blit(block.image, block.rect)

    pygame.display.flip()
    delta_time = clock.tick(60)

pygame.quit()