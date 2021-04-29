import random

class Cast: 
    def __init__(self, name, hp, ap): 
        self.name = name
        self.hp = hp
        self.ap = ap

    def attack(self, object): 
        print(self.name + "は" + object.name + "を攻撃した!  " + object.name + "は" + str(self.ap) + "のダメージ!")
        object.hp -= self.ap
        self.death_judge(object)
    
    def death_judge(self, object): 
        if object.hp <= 0: 
            print(object.name + "は死亡した。")
            
            if isinstance(object, Enemy): 
                Enemy.member_list.remove(object)
                
                if Enemy.member_list == []: 
                    print("戦闘に勝利した。")
                    exit()

            if isinstance(object, Player): 
                Player.member_list.remove(object)

                if Player.member_list == []: 
                    print("戦闘に敗北した。")
                    exit()

            
    def display_hp(self): 
        print(self.name + " HP:" + str(self.hp))

class Player(Cast): 
    member_list = []
    command_list = []
    
    def __init__(self, name, hp, ap): 
        super().__init__(name, hp, ap)
        Player.member_list.append(self)

    @classmethod
    def input_command(cls): 
        cls.command_list = ["attack" for _ in range(len(cls.member_list))]
    
class Enemy(Cast): 
    member_list = []
    command_list = []
    enemy_count = 1

    def __init__(self, name, hp, ap): 
        super().__init__(name, hp, ap)
        Enemy.member_list.append(self)

    @classmethod
    def input_command(cls): 
        command_list = []
        for _ in range(len(cls.member_list)): 
            threshold = random.randint(0, 100)
            if 0 <= threshold < 50: 
                command_list.append("attack")
            else: 
                command_list.append("call")

        cls.command_list = command_list
        
    def call_other_enemy(self, name): 
        Enemy.enemy_count += 1
        print(self.name + "は仲間を呼んだ!  " + name + "が現れた")

def r(n): 
    return random.randint(0, n-1)

def main(): 
    Player("勇者", 100, 3)
    Player("戦士", 80, 5)
    Enemy("スライム1", 10, 10)
    
    while(True): 

        ## コマンドリストの更新
        Player.input_command()
        Enemy.input_command()

        ## HPの表示
        for player in Player.member_list: 
            player.display_hp()
        for enemy in Enemy.member_list: 
            enemy.display_hp()

        ## プレーヤーの行動
        for i, command in enumerate(Player.command_list): 
            player = Player.member_list[i]
            if command == "attack": 
                player.attack(Enemy.member_list[r(len(Enemy.member_list))])
            else: 
                print("command error!")

        ## エネミーの行動            
        for i, command in enumerate(Enemy.command_list): 
            try: 
                enemy = Enemy.member_list[i]
            except: 
                continue
            
            if command == "attack": 
                enemy.attack(Player.member_list[r(len(Player.member_list))])
            elif command == "call": 
                name = Enemy("スライム" + str(Enemy.enemy_count+1), 10, 10).name
                enemy.call_other_enemy(name)
            else: 
                print("command error!")
            
        print("----------------------------")

    
if __name__ == "__main__": 
    main()