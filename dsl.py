import copy
from robot import MiniGridRobot

class Done(Exception):
    pass

class Node:
    def __str__(self) -> str:
        raise NotImplementedError

# placeholders
class Stmt(Node):
    def __init__(self) -> None:
        super().__init__()

    def ground(self) -> bool:
        return False
    
    def __str__(self) -> str:
        return "s"
    
    def expand(self):
        return [Action(), While(), Semicolon(), If(), IfElse()]
    
    def exec(self, env: MiniGridRobot):
        print("Stmt not executable")
        raise NotImplementedError

class Cond(Node):
    def __init__(self) -> None:
        super().__init__()
    
    def ground(self) -> bool:
        return False

    def __str__(self) -> str:
        return "b"

    def expand(self):
        # TODO
        # return [FrontIsClear(), LeftIsClear(), RightIsClear(), MarkersPresent(), NoMarkersPresent(), Not()]
        return [FrontIsClear(), LeftIsClear(), RightIsClear(), Not()]

    def exec(self, env: MiniGridRobot):
        print("Cond not executable")
        raise NotImplementedError

class Action(Node):
    def __init__(self) -> None:
        super().__init__()

    def ground(self) -> bool:
        return False
    
    def __str__(self) -> str:
        return "a"
    
    def expand(self):
        # TODO
        # return [Move(), TurnRight(), TurnLeft(), PickMarker(), PutMarker()]
        return [Move(), TurnRight(), TurnLeft()]
    
    def exec(self, env: MiniGridRobot):
        print("Action not executable")
        raise NotImplementedError

class Prog(Node):
    def __init__(self, s=Stmt(), rules=1) -> None:
        super().__init__()
        self.s = s
        self.rules = rules
    
    def ground(self) -> bool:
        return self.s.ground()

    def __str__(self) -> str:
        return "def run() {\n" + str(self.s) + "\n}"

    def __lt__(self, other) -> bool:
        return self.rules < other.rules

    def expand(self):
        stmts = self.s.expand()
        rst = []
        for stmt in stmts:
            rst.append(Prog(s=stmt, rules=(self.rules + 1))) 
        if type(self.s) == Stmt:
            assert len(rst) == 5
        if self.ground():
            assert len(rst) == 0
        return rst
    
    def exec(self, env: MiniGridRobot):
        self.s.exec(env)

class While(Node):
    def __init__(self, b=Cond(), s=Stmt()) -> None:
        super().__init__()
        self.b = b
        self.s = s
    
    def ground(self) -> bool:
        return self.b.ground() and self.s.ground()
    
    def __str__(self) -> str:
        return "while (" + str(self.b) + ") {\n" + str(self.s) + "\n}"
    
    def expand(self):
        lst1 = self.b.expand()
        if len(lst1) == 0:
            # b is already ground
            assert self.b.ground()
            lst2 = self.s.expand()
            rst = []
            for stmt in lst2:
                rst.append(While(b=copy.deepcopy(self.b), s=stmt))
            return rst
        else:
            assert not self.b.ground()
            rst = []
            for cond in lst1:
                rst.append(While(b=cond, s=Stmt()))
            return rst
    
    def exec(self, env: MiniGridRobot):
        while self.b.exec(env) and not env.no_fuel():
            self.s.exec(env)

class Semicolon(Node):
    def __init__(self, s1=Stmt(), s2=Stmt()) -> None:
        super().__init__()
        self.s1 = s1
        self.s2 = s2
    
    def ground(self) -> bool:
        return self.s1.ground() and self.s2.ground()
    
    def __str__(self) -> str:
        return str(self.s1) + "\n" + str(self.s2)

    def expand(self):
        lst1 = self.s1.expand()
        if len(lst1) == 0:
            # r is already ground
            assert self.s1.ground()
            lst2 = self.s2.expand()
            rst = []
            for stmt in lst2:
                rst.append(Semicolon(s1=copy.deepcopy(self.s1), s2=stmt))
            return rst
        else:
            assert not self.s1.ground()
            rst = []
            for stmt in lst1:
                rst.append(Semicolon(s1=stmt, s2=Stmt()))
            return rst
    
    def exec(self, env: MiniGridRobot):
        self.s1.exec(env)
        self.s2.exec(env)
   
class If(Node):
    def __init__(self, b=Cond(), s=Stmt()) -> None:
        super().__init__()
        self.b = b
        self.s = s
    
    def ground(self) -> bool:
        return self.b.ground() and self.s.ground()
    
    def __str__(self) -> str:
        return "if (" + str(self.b) + ") {\n" + str(self.s) + "\n}"
    
    def expand(self):
        lst1 = self.b.expand()
        if len(lst1) == 0:
            # b is already ground
            assert self.b.ground()
            lst2 = self.s.expand()
            rst = []
            for stmt in lst2:
                rst.append(If(b=copy.deepcopy(self.b), s=stmt))
            return rst
        else:
            assert not self.b.ground()
            rst = []
            for cond in lst1:
                rst.append(If(b=cond, s=Stmt()))
            return rst
    
    def exec(self, env: MiniGridRobot):
        if self.b.exec(env):
            self.s.exec(env)

class IfElse(Node):
    def __init__(self, b=Cond(), s1=Stmt(), s2=Stmt()) -> None:
        super().__init__()
        self.b = b
        self.s1 = s1
        self.s2 = s2

    def ground(self) -> bool:
        return self.b.ground() and self.s1.ground() and self.s2.ground()
    
    def __str__(self) -> str:
        return "ifElse (" + str(self.b) + ") {\n" + str(self.s1) + "\n} else {\n" + str(self.s2) + "\n}"
    
    def expand(self):
        lst1 = self.b.expand()
        if len(lst1) == 0:
            # b is already ground
            assert self.b.ground()
            lst2 = self.s1.expand()
            if len(lst2) == 0:
                # s1 is already ground 
                assert self.s1.ground()
                lst3 = self.s2.expand()
                rst = []
                for stmt in lst3:
                    rst.append(IfElse(b=copy.deepcopy(self.b), s1=Stmt(), s2=stmt))
                return rst
            else:
                assert not self.s1.ground()
                rst = []
                for stmt in lst2:
                    rst.append(IfElse(b=copy.deepcopy(self.b), s1=stmt, s2=Stmt()))
                return rst
        else:
            assert not self.b.ground()
            rst = []
            for cond in lst1:
                rst.append(IfElse(b=cond, s1=Stmt(), s2=Stmt()))
            return rst
    
    def exec(self, env: MiniGridRobot):
        if self.b.exec(env):
            self.s1.exec(env)
        else:
            self.s2.exec(env)

class FrontIsClear(Node):
    def __init__(self) -> None:
        super().__init__()

    def ground(self) -> bool:
        return True
    
    def __str__(self) -> str:
        return "front_is_clear()"

    def expand(self):
        return []
    
    def exec(self, env: MiniGridRobot):
        env.make_step()
        return env.env.front_is_clear()

class LeftIsClear(Node):
    def __init__(self) -> None:
        super().__init__()

    def ground(self) -> bool:
        return True
    
    def __str__(self) -> str:
        return "left_is_clear()"

    def expand(self):
        return []
    
    def exec(self, env: MiniGridRobot):
        env.make_step()
        return env.env.left_is_clear()
        
class RightIsClear(Node):
    def __init__(self) -> None:
        super().__init__()

    def ground(self) -> bool:
        return True
    
    def __str__(self) -> str:
        return "right_is_clear()"

    def expand(self):
        return []
    
    def exec(self, env: MiniGridRobot):
        env.make_step()
        return env.env.right_is_clear()

class MarkersPresent(Node):
    def __init__(self) -> None:
        super().__init__()

    def ground(self) -> bool:
        return True
    
    def __str__(self) -> str:
        return "markers_present()"
  
    def expand(self):
        return []
    
    def exec(self, env: MiniGridRobot):
        # TODO
        env.make_step()
        return env.karel.markers_present()

class NoMarkersPresent(Node):
    def __init__(self) -> None:
        super().__init__()

    def ground(self) -> bool:
        return True
    
    def __str__(self) -> str:
        return "no_markers_present()"
  

    def expand(self):
        return []
    
    def exec(self, env: MiniGridRobot):
        # TODO
        env.make_step()
        return env.karel.no_markers_present()

class Not(Node):
    def __init__(self, b=Cond()) -> None:
        super().__init__()
        self.b = b

    def ground(self) -> bool:
        return self.b.ground()
    
    def __str__(self) -> str:
        return "not " + str(self.b)

    def expand(self):
        lst = self.b.expand()
        if len(lst) == 0:
            # b is already ground
            assert self.b.ground()
            return []
        else:
            rst = []
            for cond in lst:
                rst.append(Not(b=cond))
            return rst
    
    def exec(self, env: MiniGridRobot):
        return not self.b.exec(env)

class Move(Node):
    def __init__(self) -> None:
        super().__init__()

    def ground(self) -> bool:
        return True
    
    def __str__(self) -> str:
        return "move()"

    def expand(self):
        return []
    
    def exec(self, env: MiniGridRobot):
        _, reward, done, _ = env.env.step(env.env.actions.forward)
        env.make_step()
        env.update_reward(reward)
        # env.env.render()
        if done:
            raise Done()

class TurnRight(Node):
    def __init__(self) -> None:
        super().__init__()

    def ground(self) -> bool:
        return True
    
    def __str__(self) -> str:
        return "turn_right()"

    def expand(self):
        return []
    
    def exec(self, env: MiniGridRobot):
        _, reward, done, _ = env.env.step(env.env.actions.right)
        env.make_step()
        env.update_reward(reward)
        # env.env.render()
        if done:
            raise Done()

class TurnLeft(Node):
    def __init__(self) -> None:
        super().__init__()

    def ground(self) -> bool:
        return True
    
    def __str__(self) -> str:
        return "turn_left()"

    def expand(self):
        return []
    
    def exec(self, env: MiniGridRobot):
        _, reward, done, _ = env.env.step(env.env.actions.left)
        env.make_step()
        env.update_reward(reward)
        # env.env.render()
        if done:
            raise Done()

class PickMarker(Node):
    def __init__(self) -> None:
        super().__init__()

    def ground(self) -> bool:
        return True
    
    def __str__(self) -> str:
        return "pick_marker()"

    def expand(self):
        return []
    
    def exec(self, env: MiniGridRobot):
        _, reward, done, _ = env.env.step(env.env.actions.pickup)
        env.make_step()
        env.update_reward(reward)
        if done:
            raise Done()

class PutMarker(Node):
    def __init__(self) -> None:
        super().__init__()

    def ground(self) -> bool:
        return True
    
    def __str__(self) -> str:
        return "put_marker()"

    def expand(self):
        return []
    
    def exec(self, env: MiniGridRobot):
        _, reward, done, _ = env.env.step(env.env.actions.drop)
        env.make_step()
        env.update_reward(reward)
        if done:
            raise Done()

