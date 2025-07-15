from pickle import FALSE

import myObject

class GameObjectManager:
    def __init__(self):
        self.enemys = []  # enemy objects
        self.airs = []    # air objects
        self.blocks = []  # block objects
        self.runing =True  # 游戏是否在运行


    def add(self, obj):
        """添加对象到管理器"""
        if obj.type == 'enemy':
            self.enemys.append(obj)
        elif obj.type == 'air':
            self.airs.append(obj)
        elif obj.type == 'block':
            self.blocks.append(obj)
        elif obj.type == 'hero':
            self.hero = obj  # 设定hero对象
        elif obj.type == 'map':
            self.map = obj  # 设定地图对象

        return obj  # 返回对象以便链式调用

    def update_all(self):
        """更新所有对象"""
        if self.hero.isOpen:
            # 获取英雄所在位置的空气对象
            current_cell_airs = self.map.get_objects_at(self.hero.x, self.hero.y)
            for air in current_cell_airs:
                if air.type == "air":  # 确保是空气对象
                    air.increase_con(self.hero)
                    print(f"增加气体浓度: {air.con}")

        for enemy in self.enemys:
            enemy.update(self.hero)
        for air in self.airs:
            air_set =self.map.get_nearby_objects(air)
            air.update(air_set)
        self.remove_inactive()
        return self.hero.update()


    def check_all(self):
        """检查所有对象"""
        self.hero.check_collision(self.blocks, self.enemys)
        for enemy in self.enemys:
            enemy.check_collision(self.blocks)
            enemy.check_stare(self.airs)

        # for air in self.airs:
        #     air.check_fire()

    def draw_all(self, surface):
        """绘制所有对象"""
        for block in self.blocks:
            block.draw(surface)
        self.hero.draw(surface)
        for enemy in self.enemys:
            enemy.draw(surface)
        for air in self.airs:
            air.draw(surface)




    def remove_inactive(self):
        """移除所有不活跃的对象"""
        self.enemys = [enemy for enemy in self.enemys
                        if getattr(enemy, 'active', True)]

    def clear(self):
        """清空所有对象"""
        self.enemys.clear()
        self.airs.clear()
        self.blocks.clear()
        self.hero = None
        self.map = None