
import pygame# 初始化pygame
import myObject as obj
import ObjectManager as mgr


# 初始化游戏窗口
cell_size= 50
width_size = 16
height_size = 16

width= cell_size * (width_size+2)
height= cell_size * (height_size+2)


pygame.init()
screen = pygame.display.set_mode((width, height))

clock = pygame.time.Clock()
FPS = 60  # 设置目标帧率
# 创建对象
hero   = obj.hero(1, 1)  # 蓝色玩家
enemy1 = obj.enemy(15, 15)  # 红色敌人
enemy2 = obj.enemy(9, 8)  # 红色敌人
block1 = obj.block(2, 2)  # 石头方块
block2 = obj.block(6, 3)  # 木头方块
block3 = obj.block(4, 8)  # 石头方块
block4 = obj.block(2, 5)  # 石头方块

#创建对象管理器
object_manager = mgr.GameObjectManager()


# object_manager.add(air1)
# object_manager.add(air2)
# object_manager.add(air3)
# object_manager.add(air4)
# object_manager.add(air5)
grid_map = obj.GridMap(width, height, cell_size)

grid_map.create_random_air()
grid_map.add_object(block1)
grid_map.add_object(block2)
grid_map.add_object(block3)
grid_map.add_object(block4)

# print(grid_map.grid)
for r in range(grid_map.rows):
    for c in range(grid_map.columns):
        for item in grid_map.grid[r][c]:
            print(item)
            object_manager.add(item)
# grid_map.add_object(air1)
# grid_map.add_object(air2)
# grid_map.add_object(air3)
# grid_map.add_object(air4)
# grid_map.add_object(air5)
object_manager.add(hero)
object_manager.add(enemy1)
object_manager.add(enemy2)
object_manager.add(block1)
object_manager.add(block2)
object_manager.add(grid_map)
#创建地图


# 游戏主循环
running = True
while running:
    # 处理事件
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    # 处理英雄输入
    hero.handle_events(events)

    # 更新游戏状态
    # hero.check_collision(blocks, enemies)
    # enemy.check_collision(blocks)
    # running=hero.update()
    # enemy.update(hero)

    object_manager.check_all()
    running = object_manager.update_all()



    # 绘制
    screen.fill((255, 255, 255))  # 清屏(黑色)
    object_manager.draw_all(screen)

    pygame.display.flip()  # 更新显示
    # print(hero.x, hero.y)

    clock.tick(60)  # 60 FPS
print("游戏结束!")
pygame.quit()