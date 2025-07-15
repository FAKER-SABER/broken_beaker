import pygame
import os
import math as m
import numpy as np
import random

class GridMap:
    def __init__(self, width, height, cell_size):
        """
        初始化网格地图
        :param width: 地图总宽度(像素)
        :param height: 地图总高度(像素)
        :param cell_size: 每个网格的大小(像素)
        """
        self.cell_size = cell_size
        self.columns = width // cell_size
        self.rows = height // cell_size
        self.grid = [[[] for _ in range(self.columns)] for _ in range(self.rows)]
        self.type = "map"

        print("GridMap created with", self.columns, "columns and", self.rows, "rows")

    def add_object(self, obj):
        """添加对象到网格"""
        if obj.type == "block"or obj.type == "air":
            x, y = obj.x, obj.y
            col, row = self._get_cell_index(x, y)

            if 0 <= row < self.rows and 0 <= col < self.columns:
                if self.grid[row][col] == []:
                    self.grid[row][col].append(obj)
                    print(obj, "added to cell", (row, col))
                else:
                    for item in self.grid[row][col]:
                        if item.type == "air"and obj.type == "block":
                            item.delete()
                            self.grid[row][col] .append(obj)
                return True
            else:
                print(obj, "out of bounds")
        else:
            print(obj, "not a block or air object")

        return False

    def get_objects_at(self, x, y):
        """获取指定位置的对象"""
        col, row = self._get_cell_index(x, y)
        if 0 <= row < self.rows and 0 <= col < self.columns:
            return self.grid[int(row)][int(col)]
        return []

    def get_nearby_objects(self, obj, radius=1):
        """获取附近网格的对象"""
        center_col, center_row = self._get_cell_index(obj.x, obj.y)
        nearby_objects = []

        for r in range(max(0, center_row - radius), min(self.rows, center_row + radius + 1)):
            for c in range(max(0, center_col - radius), min(self.columns, center_col + radius + 1)):
                # 跳过中心格子自身
                if r == center_row and c == center_col:
                    continue

                for grid_obj in self.grid[r][c]:
                    if grid_obj.type == "air":
                        nearby_objects.append(grid_obj)
        return nearby_objects


    def _get_cell_index(self, x, y):
        """将坐标转换为网格索引"""
        return x // self.cell_size, y // self.cell_size

    def clear(self):
        """清空网格"""
        self.grid = [[[] for _ in range(self.columns)] for _ in range(self.rows)]

    def create_random_air(self):
        """
        随机生成不同气体分布的Air对象
        """
        for x in range(self.columns):
            for y in range(self.rows):
                # 基础氮气浓度
                n2 = random.uniform(0.7, 0.9)
                remaining = 1.0 - n2

                # 随机分配剩余浓度给其他气体
                other_gases = [random.random() for _ in range(5)]
                total_other = sum(other_gases)
                other_gases = [g * remaining / total_other for g in other_gases]

                con = [n2] + other_gases
                air = Air(x, y, con=con)
                self.add_object(air)

class MyObject:
    def __init__(self, x=0, y=0,cell_size=50):
        """游戏对象基类

        参数:
            x (int): x坐标
            y (int): y坐标
        """
        self.cell_size = cell_size
        self.x = x*cell_size
        self.y = y*cell_size
        self.ID=[x,y]
        self.width = self.cell_size
        self.height= self.cell_size
        self.velocity = [0, 0]
        self.active = True
        self._image = None
        self.rect = pygame.Rect(x, y, 0, 0)
        self.isAir = False
        self.type = "object"
    @property
    def image(self):
        """获取对象图像"""
        return self._image

    @image.setter
    def image(self, value):
        """设置对象图像"""
        self._image = value
        if self._image is not None:
            self.rect = self._image.get_rect(topleft=(self.x, self.y))


    def draw(self, surface):
        """绘制对象"""
        if self.active and self.image is not None:
        # if self.active :
            surface.blit(self.image, self.rect)

    def set_position(self, x, y):
        """设置位置"""
        self.x = x
        self.y = y
        self.rect.topleft = (x, y)
    def isAir(self):
        return self.isAir
    def delete(self):
        del self



class Air(MyObject):
    def __init__(self, x=0, y=0, con=[0.9, 0.1, 0, 0, 0, 0]):
        """空气效果类（使用矩形）

        参数:
            x (int): x坐标
            y (int): y坐标

            color (tuple): RGB颜色
            alpha (int): 透明度(0-255)

        """
        super().__init__(x, y,cell_size=50)
        self.isAir = True
        self.isFire = False
        self.type = "air"
        # self.alpha = alpha
        self.con = con#气体浓度 0 N2无色   1 O2蓝色   2 H2粉色   3 CH4黄色   4 CO2黑色   5 Cl2绿色
        self.air_color()
        self._create_surface()
        self.difspeed = 0.01
        self.active = True
    def update(self,nearby_airs):
        """更新空气效果"""
        needs_update = False
        for air in nearby_airs:
            if air.type == "air" :
                air.decrease_con()
                for i in range(len(self.con)):
                    # 计算浓度差
                    diff = (self.con[i] - air.con[i]) * self.difspeed
                    if abs(diff) > 0.001:  # 只有差异明显时才扩散
                        self.con[i] -= diff
                        air.con[i] += diff
                        needs_update = True
        if needs_update:
            self.air_color()
            # print(self.color)
            self._create_surface()

    def _create_surface(self):
        """创建透明表面"""
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.image.fill((*self.color, self.alpha))

    def set_alpha(self, alpha):
        """设置透明度

        参数:
            alpha (int): 新的透明度值(0-255)
        """
        self.alpha = alpha
        self._create_surface()

    def set_color(self, color):
        """设置颜色

        参数:
            color (tuple): RGB颜色值
        """
        self.color = color
        self._create_surface()

    # def draw(self, surface):
    #     """绘制air"""
    #     pygame.draw.rect(surface, self.color, self.rect)
    def air_color(self):
        """计算空气颜色"""
        sum_con = max(0.001, sum(self.con))  # 避免除以零

        # 计算各颜色分量
        red = (0 * self.con[1] / sum_con +  # O2
               255 * self.con[2] / sum_con +  # H2
               255 * self.con[3] / sum_con +  # CH4
               0 * self.con[4] / sum_con +  # CO2
               0 * self.con[5] / sum_con)  # Cl2

        green = (0 * self.con[1] / sum_con +
                 170 * self.con[2] / sum_con +
                 255 * self.con[3] / sum_con +
                 0 * self.con[4] / sum_con +
                 255 * self.con[5] / sum_con)

        blue = (255 * self.con[1] / sum_con +
                255 * self.con[2] / sum_con +
                170 * self.con[3] / sum_con +
                0 * self.con[4] / sum_con +
                0 * self.con[5] / sum_con)

        # 限制颜色范围
        self.color = (
            max(0, min(255, int(red))),
            max(0, min(255, int(green))),
            max(0, min(255, int(blue)))
        )
        # 根据氮气浓度设置透明度
        self.alpha = int(255 * (1 - self.con[0] / sum_con)*0.5)

    def increase_con(self, hero):
        """增加气体浓度并保持总和为1"""
        if hero.typeofContent == 0:  # 无操作
            return

        # 保存原始总和用于归一化
        original_sum = sum(self.con)
        if original_sum <= 0:
            return

        # 要增加的气体索引
        gas_index = hero.typeofContent

        # 增加指定气体浓度
        increase_amount =0.8
        self.con[gas_index] += increase_amount

        # 重新归一化所有浓度，使总和保持为original_sum + increase_amount
        new_sum = original_sum + increase_amount
        self.con = [c * (original_sum / new_sum) for c in self.con]
        self.con[gas_index] = (self.con[gas_index] + increase_amount) * (original_sum / new_sum)

        # 更新颜色和表面
        self.air_color()
        self._create_surface()
    def decrease_con(self):
         """减少气体浓度并保持总和为1"""
         # 保存原始总和用于归一化
         original_sum = sum(self.con)
         if original_sum <= 0:
             return

         # 要减少的气体索引
         max_con = max(self.con)
         gas_index = self.con.index(max_con)

         # 减少指定气体浓度
         decrease_amount = 0.001
         self.con[gas_index] = max(0, self.con[gas_index]-decrease_amount)


         # 重新归一化所有浓度，使总和保持为original_sum - decrease_amount
         new_sum = original_sum - decrease_amount
         self.con = [c * (original_sum / new_sum) for c in self.con]

         # 更新颜色和表面
         self.air_color()




class block(MyObject):
    def __init__(self, x=0, y=0,material=None, scale=1.0, alpha=255):
        super().__init__(x, y)
        print(material)

        self.isAir = False
        self.material = material
        self.active = True
        self.type = "block"
        self.alpha = alpha
        if self.material :
            image_path = "./images/"+ self.material+".png"
            if image_path and os.path.exists(image_path):
                self.load_image(image_path, scale, alpha)
        else:
            print("没有材质")
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self.image.fill((100,100,0))





    def load_image(self, image_path, scale=1.0, alpha=255):
        """加载图片并设置透明度

        参数:
            image_path (str): 图片路径
            scale (float): 缩放比例
            alpha (int): 透明度(0-255)
        """
        try:
            # 加载图片并启用透明度
            img = pygame.image.load(image_path).convert_alpha()

            # 缩放
            if scale != 1.0:
                new_size = (
                    int(img.get_width() * scale),
                    int(img.get_height() * scale)
                )
                img = pygame.transform.scale(img, new_size)

            # 设置透明度
            if alpha < 255:
                img = self._set_image_alpha(img, alpha)

            self.image = img
        except Exception as e:
            print(f"加载图片失败: {e}")
            # 创建默认图像
            self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
            self.image.fill((255, 0, 0, alpha))

    def _set_image_alpha(self, image, alpha):
        """设置图片整体透明度"""
        img_copy = image.copy()
        img_copy.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
        return img_copy



class role(MyObject):
    def __init__(self, x=0, y=0, image_path=None, scale=1.0, alpha=255):
        """角色类（使用图片）

        参数:
            x (int): x坐标
            y (int): y坐标
            image_path (str): 图片路径
            scale (float): 缩放比例
            alpha (int): 透明度(0-255)
        """
        super().__init__(x, y)
        self.isAir = False
        if image_path and os.path.exists(image_path):
            self.load_image(image_path, scale, alpha)
        else:
            # 默认红色矩形（带透明度）
            self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
            self.image.fill((255, 0, 0, alpha))


    def load_image(self, image_path, scale=1.0, alpha=255):
        """加载图片并设置透明度

        参数:
            image_path (str): 图片路径
            scale (float): 缩放比例
            alpha (int): 透明度(0-255)
        """
        try:
            # 加载图片并启用透明度
            img = pygame.image.load(image_path).convert_alpha()

            # 缩放
            if scale != 1.0:
                new_size = (
                    int(img.get_width() * scale),
                    int(img.get_height() * scale)
                )
                img = pygame.transform.scale(img, new_size)

            # 设置透明度
            if alpha < 255:
                img = self._set_image_alpha(img, alpha)

            self.image = img
        except Exception as e:
            print(f"加载图片失败: {e}")
            # 创建默认图像
            self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
            self.image.fill((255, 0, 0, alpha))

    def _set_image_alpha(self, image, alpha):
        """设置图片整体透明度"""
        img_copy = image.copy()
        img_copy.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
        return img_copy

    def update(self):
        """更新对象位置"""
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        if self.x < 0:
            self.x = 0
        if self.x > 800:
            self.x = 800
        if self.y < 0:
            self.y = 0
        if self.y > 800:
            self.y = 800
        self.rect.topleft = (self.x, self.y)
        # print(self.x, self.y)






class hero(role):
    def __init__(self, x=0, y=0, image_path=None, scale=1.0, alpha=255):
        super().__init__(x, y, image_path, scale, alpha)
        if image_path is None:
            self.color = (0, 0, 0)
        self.isAir = False
        self.health = 100
        self.Cspeed = self.cell_size / 20
        self.speed = self.cell_size/20
        self.typeofContent = 0#0为无，1为O2，2为N2，3为H2，4为CO2，5为CH4
        self.isOpen = False
        self.isFire = False

        self.active = True
        self.type = "hero"
    def update(self):

        if self.typeofContent == 0:
            self.color = (100, 200, 150)
        elif self.typeofContent == 1:
            self.color = (0, 0, 255)
        elif self.typeofContent == 2:
            self.color = (255, 170, 0)
        elif self.typeofContent == 3:
            self.color = (255, 255, 170)
        elif self.typeofContent == 4:
            self.color = (0, 0, 0)
        elif self.typeofContent == 5:
            self.color = (0, 255, 0)
        super().update()
        if self.health <= 0:
            self.active = False
            return False
        if self.isFire:
            self.health -= 10
            self.isFire = False
        if self.isOpen:
           if self.typeofContent == 0:
               self.speed=self.Cspeed
           elif self.typeofContent == 1:
               self.speed = self.Cspeed*0.8
               self.health += 2
           elif self.typeofContent == 2:
                self.speed = self.Cspeed
           elif self.typeofContent == 3:
               self.speed = self.Cspeed*1.2
               self.health -= 0.2
           elif self.typeofContent == 4:
               self.speed = self.Cspeed*1.1





        print(self.typeofContent)
        # print(self.color)
        # print(self.isOpen)
        return True

    def handle_events(self, events):
        """处理键盘输入事件"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.velocity[1] = -self.speed
                elif event.key == pygame.K_s:
                    self.velocity[1] = self.speed
                elif event.key == pygame.K_a:
                    self.velocity[0] = -self.speed
                elif event.key == pygame.K_d:
                    self.velocity[0] = self.speed
                elif event.key == pygame.K_SPACE:
                    self.isOpen = True
                elif event.key == pygame.K_j:
                    self.typeofContent = 0
                elif event.key == pygame.K_k:
                    self.typeofContent = 1
                elif event.key == pygame.K_l:
                    self.typeofContent = 2
                elif event.key == pygame.K_u:
                    self.typeofContent = 3
                elif event.key == pygame.K_i:
                    self.typeofContent = 4
                elif event.key == pygame.K_o:
                    self.typeofContent = 5


            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w or event.key == pygame.K_s:
                    self.velocity[1] = 0
                elif event.key == pygame.K_a or event.key == pygame.K_d:
                    self.velocity[0] = 0
                elif event.key == pygame.K_SPACE:
                    self.isOpen = False
                elif event.key == pygame.K_j:
                    self.typeofContent = 0
                elif event.key == pygame.K_k:
                    self.typeofContent = 1
                elif event.key == pygame.K_l:
                    self.typeofContent = 2
                elif event.key == pygame.K_u:
                    self.typeofContent = 3
                elif event.key == pygame.K_i:
                    self.typeofContent = 4
                elif event.key == pygame.K_o:
                    self.typeofContent = 5


                    # self.isFire = False

    def check_collision(self, blocks, enemies):
        """检查与障碍物和敌人的碰撞"""
        # 保存原始位置用于碰撞回退
        original_x, original_y = self.x, self.y

        # 更新临时位置
        temp_rect = self.rect.copy()
        temp_rect.x = self.x + self.velocity[0]
        temp_rect.y = self.y + self.velocity[1]

        # 检查与障碍物的碰撞
        for block in blocks:
            if temp_rect.colliderect(block.rect):
                # 水平碰撞
                if self.velocity[0] != 0:
                #     if self.velocity[0] > 0:  # 向右移动
                #         self.x = block.rect.left - self.width
                #     else:  # 向左移动
                #         self.x = block.rect.right
                    self.velocity[0] = 0
                    self.x = original_x

                # 垂直碰撞
                if self.velocity[1] != 0:
                    # if self.velocity[1] > 0:  # 向下移动
                    #     self.y = block.rect.top - self.height
                    # else:  # 向上移动
                    #     self.y = block.rect.bottom
                    self.velocity[1] = 0
                    self.y = original_y

                temp_rect.topleft = (self.x, self.y)

        # 检查与敌人的碰撞
        for enemy in enemies:
            if temp_rect.colliderect(enemy.rect):
                self.health -= 10
                print(f"英雄受到伤害! 剩余生命: {self.health}")
                # 碰撞后弹开
                push_back = 5
                if self.x < enemy.x:
                    self.x -= push_back
                else:
                    self.x += push_back
                if self.y < enemy.y:
                    self.y -= push_back
                else:
                    self.y += push_back

                # 确保不会超出屏幕
                self.x = max(0, min(self.x, 800 - self.width))
                self.y = max(0, min(self.y, 600 - self.height))

                temp_rect.topleft = (self.x, self.y)

        # 更新最终位置
        self.rect.topleft = (self.x, self.y)
    def draw(self, surface):
            """绘制英雄"""
            pygame.draw.rect(surface, self.color, self.rect)
            # 绘制生命条
            health_bar_width = 50
            health_ratio = self.health / 100
            pygame.draw.rect(surface, (255, 0, 0), (self.x, self.y - 10, health_bar_width, 5))
            pygame.draw.rect(surface, (0, 255, 0), (self.x, self.y - 10, health_bar_width * health_ratio, 5))



class enemy(role):
    def __init__(self, x=0, y=0, image_path=None, scale=1.0, alpha=255):
        super().__init__(x, y, image_path, scale, alpha)
        if image_path is None:
            self.color = (0, 0, 255)
        self.isAir = False
        self.health = 100
        self.speed = self.cell_size/25
        self.isFire = False
        self.active = True
        self.type = "enemy"
    def update(self,hero):

        super().update()
        self.velocity[0] = (hero.x - self.x)/m.sqrt(m.pow((hero.x - self.x),2)+m.pow((hero.y - self.y),2))*self.speed
        self.velocity[1] = (hero.y - self.y)/m.sqrt(m.pow((hero.x - self.x),2)+m.pow((hero.y - self.y),2))*self.speed
        if self.health <= 0:
            self.active = False
            self.delete()
        if self.isFire:
            self.health -= 10
            self.isFire = False
    def check_collision(self, blocks):
        """检查与障碍物和敌人的碰撞"""
        # 保存原始位置用于碰撞回退
        original_x, original_y = self.x, self.y

        # 更新临时位置
        temp_rect = self.rect.copy()
        temp_rect.x = self.x + self.velocity[0]
        for block in blocks:
            if temp_rect.colliderect(block.rect):
                # 水平碰撞
                if self.velocity[0] != 0:
                    # if self.velocity[0] > 0:  # 向右移动
                    #     self.x = block.rect.left - self.width
                    # else:  # 向左移动
                    # self.x = block.rect.right
                    self.velocity[0] = 0
                    self.x = original_x
                    self.velocity[1] = np.sign(self.velocity[1])*self.speed
        temp_rect.x = original_x
        temp_rect.y = self.y + self.velocity[1]

        for block in blocks:
            if temp_rect.colliderect(block.rect):
        # 检查与障碍物的碰撞
        # for block in blocks:
        #     if temp_rect.colliderect(block.rect):
        #         # 水平碰撞
        #         if self.velocity[0] != 0:
        #             # if self.velocity[0] > 0:  # 向右移动
        #             #     self.x = block.rect.left - self.width
        #             # else:  # 向左移动
        #                 # self.x = block.rect.right
        #             self.velocity[0] = 0
        #             self.x = original_x

                # 垂直碰撞
                if self.velocity[1] != 0:
                    # if self.velocity[1] > 0:  # 向下移动
                    #     self.y = block.rect.top - self.height
                    # else:  # 向上移动
                    #     self.y = block.rect.bottom
                    self.velocity[1] = 0
                    self.y = original_y
                    self.velocity[0] = np.sign(self.velocity[0]) * self.speed
                temp_rect.topleft = (self.x, self.y)



        # 更新最终位置
        self.rect.topleft = (self.x, self.y)

    def check_stare(self,airs):
        for air in airs:
            if self.rect.colliderect(air.rect):
                if air.con[5]>0.5:
                    self.health -= 0.5
                    print(f"敌人受到伤害! 剩余生命: {self.health}")


    def draw(self, surface):
        """绘制英雄"""
        pygame.draw.rect(surface, self.color, self.rect)
        # 绘制生命条
        health_bar_width = 50
        health_ratio = self.health / 100
        pygame.draw.rect(surface, (255, 0, 0), (self.x, self.y - 10, health_bar_width, 5))
        pygame.draw.rect(surface, (0, 255, 0), (self.x, self.y - 10, health_bar_width * health_ratio, 5))



