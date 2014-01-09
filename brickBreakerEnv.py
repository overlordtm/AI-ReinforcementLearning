from templateRL import Environment
from box import BoxModel

import random
import math

class BrickBreakerEnv(Environment):

    """
    Actions: +5, +2, -6,...
    """
    def __init__(self, bricks = 5, lives = 3):
        self.origLives = lives
        self.lives = lives
        self.maxSteps = 1000000
        self.steps = 0
        minx = 0
        maxx = bricks
        miny = 0
        maxy = bricks
        self.box = BoxModel(minx, maxx, miny, maxy)

        # self.actions = [(i, d/10.0) for i in xrange(int(minx), int(maxx)) for d in xrange(-5, 5+1)]
        self.actions = [(i, d) for i in xrange(int(minx), int(maxx)) for d in ['<<', '<', '.', '>', '>>']]

        print self.actions

    def reset(self):
        self.lives = self.origLives
        self.steps = self.maxSteps
        self.box.reset()

    def getStartingState(self):

        _, _, vx, vy = self.box.ball

        return (self.box.pad, round(float(vy)/vx, 1), tuple(self.box.bricks))

    def do(self, state, action):

        self.steps = self.steps + 1
        x, y, vx, vy = self.box.ball

        pad, corr = action

        if corr == '<<':
            vx = vx - 1.5

        if corr == '<':
            vx = vx - 0.5

        if corr == '>':
            vx = vx + 0.5

        if corr == '>>':
            vx = vx + 1.5

        # delta = math.atan(action - self.box.pad) + (random.random() - 0.5)
        # if random.random() > 0.8:
        #     vx = vx + (random.random() - 0.5)

        self.box.ball = (x, y, vx, vy)
        self.box.pad = pad
        hit = self.box.bounce()

        self.printStatus()
        isTerminal = False
        reward = -0.1
        if hit is True:
            print "Brick hit", self.box.bricks
            reward = 1

        if sum(self.box.bricks) == 0:
            print "You won", self.box.bricks
            isTerminal = True
            self.reset()
            reward = 10

        if self.box.checkPad() is False:
            print "Ball missed (lives left: %d)" % self.lives
            # then you missed the ball
            self.lives = self.lives - 1
            reward = -1
            isTerminal = False

        if self.lives < 1:
            print "You died"
            reward = -10
            isTerminal = True
            self.reset()

        # if self.steps > self.maxSteps:
        #     print "Out of time"
        #     reward = -1
        #     isTerminal = True
        #     self.reset()

        
        _, _, vx, vy = self.box.ball

        newState = (self.box.pad, round(float(vy)/vx, 1), tuple(self.box.bricks))
        return newState, reward, isTerminal

    def getActions(self, state):
        return self.actions

    def printStatus(self):
        bricks = ['=' for _ in self.box.bricks]
        ball = [' ' for _ in self.box.bricks]
        pad = [' ' for _ in self.box.bricks]

        x, _, _, _ = self.box.ball
        assert 0 <= int(x) < len(ball), x
        ball[int(x)] = '*'
        pad[int(self.box.pad)] = '_'

        for i in range(len(self.box.bricks)):
            if self.box.bricks[i] == 0:
                bricks[i] = ' '

        print "".join(bricks)
        for i in range(len(self.box.bricks) - 2):
            print
        print "".join(ball)
        print "".join(pad)




if __name__ == '__main__':
    env = BrickBreakerEnv()
    s = env.getStartingState()
    actions = env.getActions(s)
    isTerminal = False
    random.seed(100)
    for i in xrange(10):
        a = random.choice(actions)
        if i == 5:
            print ""
        newState, reward, isTerminal = env.do(s, a)
        print s, '--', a, '-->', newState, reward, isTerminal
        s = newState

    print "Starting state: ", s
    print "Actions: ", a