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

class MoveState:
    FREE = 0  # 自由落体
    MOVE = 1  # 移动到目标位置 
    STAY = 2  # 静止

class Block:
    def __init__(self, pos, target_pos, level):
        self.level = level
        self.image = images[self.level]
        self.rect = self.image.get_rect(center=pos)
        self.speed = [0.1, -0.3]
        self.acc = [0, 0.0002]
        self.pos = list(pos)
        self.move_state = MoveState.FREE
        
        # 计算初始速度矢量
        rad = self.calc_degree(pos, target_pos)
        self.speed[0] += 0.3 * math.cos(rad)
        self.speed[1] += 0.3 * math.sin(rad)

    def update_movement(self, delta_time):
        if self.move_state == MoveState.FREE:  # 仅活动方块需要更新物理运动
            self.speed[0] += self.acc[0] * delta_time
            self.speed[1] += self.acc[1] * delta_time
            self.pos[0] += self.speed[0] * delta_time
            self.pos[1] += self.speed[1] * delta_time
            self.rect.center = self.pos
        elif self.move_state == MoveState.MOVE:
            self.pos[0] += (self.target_pos[0] - self.pos[0]) / 5
            self.pos[1] += (self.target_pos[1] - self.pos[1]) / 5
            if abs(self.target_pos[0] - self.pos[0]) < 0.01 and abs(self.target_pos[1] - self.pos[1]) < 0.01:
                self.pos = self.target_pos
                self.move_state = MoveState.STAY
            self.rect.center = self.pos
    
    def set_move_state(self, move_state, grid_pos = None):
        self.move_state = move_state
        self.grid_pos = grid_pos
        if grid_pos:
            target_x = grid_pos[0]*block_size+block_size//2 + screen_width//2
            target_y = grid_pos[1]*block_size+block_size//2
            self.target_pos = (target_x, target_y)
        

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
received_blocks = {}
back_blocks = {}
for i in range(screen_height//block_size):
    for j in range(screen_width//2//block_size):
        rect = pygame.rect.Rect(screen_width//2 + j*block_size, i*block_size, block_size, block_size)
        back_blocks[ (i,j) ] = rect
        received_blocks[ (i, j) ] = None
    
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
            block_x = (block.rect.center[0]-screen_width//2)//block_size
            block_y = block.rect.center[1]//block_size
            block.set_move_state(MoveState.MOVE, (block_x, block_y))
            to_receive.append(block)

    # 转移符合条件的方块
    for block in to_receive:
        if block in active_blocks:
            active_blocks.remove(block)
            received_blocks[ block.grid_pos ] = block
    
    for ij, block in received_blocks.items():
        if block:
            block.update_movement(delta_time)

    for (i,j), rect in back_blocks.items():
        screen.blit(back_image, rect)

    # 绘制所有方块
    for block in active_blocks:
        screen.blit(block.image, block.rect)
    for ij, block in received_blocks.items():
        if block:
            screen.blit(block.image, block.rect )

    pygame.display.flip()
    delta_time = clock.tick(60)

pygame.quit()