from templateRL import Environment

import random
import math


class BoxModel:
    def __init__(self, box_min_x, box_max_x, box_min_y, box_max_y):

        self.box = (box_min_x, box_max_x, box_min_y, box_max_y)

        self.reset()
        print "==== BoxModel ====="
        print "Box:", self.box
        print "Ball:", self.ball
        print "Pad:", self.pad
        print "Bricks", self.bricks
        print "==== BoxMode END ====="

    def reset(self):
        (box_min_x, box_max_x, box_min_y, box_max_y) = self.box
        self.pad = int(box_max_x - box_min_x)/2
        self.ball = (self.pad + 0.5, 0.0, 1, 1.0)
        self.bricks = [1 for _ in xrange(box_min_x, box_max_x)]

    def _normalizeVelocity(self):
        x, y, _vx, _vy = self.ball
        # print "normalizing", _vx, _vy
        # nromalize
        vx = _vx/max(abs(_vx), abs(_vy))
        vy = _vy/max(abs(_vx), abs(_vy))
        # ensure normalized speed
        assert -1 <= vx <= 1, self.ball
        assert -1 <= vy <= 1, self.ball
        self.ball = (x, y, vx, vy)

    def bounce(self):
        box_min_x, box_max_x, box_min_y, box_max_y = self.box
        self._normalizeVelocity()
        x, y, vx, vy = self.ball
        
        brickHit = False
        # ensure up direction
        assert vy > 0
        # ensure ball starts at bottom
        assert y == 0

        ball = self.ball

        count = 0

        while True:
            x, y, vx, vy = ball
            count = count + 1
            assert count < 30, ball
            assert box_min_x <= x <= box_max_x, ball
            assert box_min_y <= y <= box_max_y, ball

            if vx < 0:
                newy = vy/vx * (box_min_x - x) + y
                # assert (box_min_x - x) != 0
                if box_min_y <= newy <= box_max_y:
                    ball = (box_min_x+0.01, newy, -vx, vy)
                    # print "hit left", ball
                elif newy > box_max_y:
                    k = vy/vx
                    x = (box_max_y - y) / k + x
                    ball = (x+0.01, box_max_y, vx, -vy)
                    # print "hit top", ball
                    brickHit, self.checkBrickHit(ball)
                elif newy < box_min_y:
                    k = vy/vx
                    x = (box_min_y - y) / k + x
                    ball = (x+0.01, box_min_y, vx, -vy)
                    # print "hit bottom", ball
                    break
                else:
                    assert False, "kaj naj naredim?"

            if vx > 0:
                newy = vy/vx * (box_max_x - x) + y
                # assert (box_max_x - x) != 0
                if box_min_y <= newy <= box_max_y:
                    ball = (box_max_x-0.01, newy, -vx, vy)
                    # print "hit right", ball
                elif newy > box_max_y:
                    k = vy/vx
                    x = (box_max_y - y) / k + x
                    ball = (x-0.01, box_max_y, vx, -vy)
                    # print "hit top", ball
                    brickHit = self.checkBrickHit(ball)
                elif newy < box_min_y:
                    k = vy/vx
                    x = (box_min_y - y) / k + x
                    ball = (x-0.01, box_min_y, vx, -vy)
                    # print "hit bottom", ball
                    break
                else:
                    assert False, "kaj naj naredim?"

            if vx == 0:
                brickHit = self.checkBrickHit(ball)
                ball = (x, y, vx, vy)
                break

        # set ball position
        self.ball = ball
        self._normalizeVelocity()

        x, y, vx, vy = self.ball
        # ensure we ended up at bottom
        assert y == box_min_y, y
        return brickHit

    def checkBrickHit(self, ball):
        box_min_x, box_max_x, box_min_y, box_max_y = self.box
        x, y, _, _ = ball

        assert y == box_max_y or y == box_min_x

        idx = int(x - box_min_x)
        idx = min(idx, len(self.bricks)-1)

        assert -1 < idx < len(self.bricks), ball

        if self.bricks[idx] == 1:
            # print "Hit brick", idx
            self.bricks[idx] = 0
            return True
        else:
            return False

    def checkPad(self):
        box_min_x, box_max_x, box_min_y, box_max_y = self.box
        x, y, _, _ = self.ball

        assert y == box_min_y
        return self.pad <= x <= self.pad + 1

    def movePad(self, newX):
        box_min_x, box_max_x, box_min_y, box_max_y = self.box
        x, y, vx, vy = self.ball

        c = math.atan(newX - self.pad)

        self.pad = newX
        self.ball = (x, y, vx + c, vy)

class BrickBreakerEnv(Environment):

    """
    Actions: +5, +2, -6,...
    """
    def __init__(self, bricks = 5, lives = 3):
        self.origLives = lives
        self.lives = lives
        self.maxSteps = 1000
        self.steps = 0
        minx = 0
        maxx = bricks
        miny = 0
        maxy = bricks
        self.box = BoxModel(minx, maxx, miny, maxy)

        # self.actions = [(i, d/10.0) for i in xrange(int(minx), int(maxx)) for d in xrange(-5, 5+1)]
        actions = ['<', '.', '>']
        self.actions = [(i, d) for i in xrange(int(minx), int(maxx)) for d in actions]

        print self.actions

    def reset(self):
        self.lives = self.origLives
        self.steps = self.maxSteps
        self.box.reset()

    def getStartingState(self):

        _, _, vx, vy = self.box.ball

        if vx != 0:
            k = round(float(vy)/vx, 1)
        else:
            k = None

        return (self.box.pad, k)

    def do(self, state, action):

        self.steps = self.steps + 1
        x, y, vx, vy = self.box.ball

        pad, corr = action

        if corr == '<<':
            vx = vx - 0.3

        if corr == '<':
            vx = vx - 0.1

        if corr == '>':
            vx = vx + 0.1

        if corr == '>>':
            vx = vx + 0.3

        # delta = math.atan(action - self.box.pad) + (random.random() - 0.5)
        # if random.random() > 0.8:
        #     vx = vx + (random.random() - 0.5)

        self.box.ball = (x, y, vx, vy)
        self.box.pad = pad
        hit = self.box.bounce()

        # self.printStatus()
        isTerminal = False
        reward = 0
        if hit is True:
            # print "Brick hit", self.box.bricks
            reward = 3

        if sum(self.box.bricks) == 0:
            # print "You won", self.box.bricks
            isTerminal = True
            self.reset()
            reward = 10

        if self.box.checkPad() is False:
            # print "Ball missed (lives left: %d)" % self.lives
            # then you missed the ball
            self.lives = self.lives - 1
            reward = -1
            isTerminal = False

        if self.lives < 1:
            # print "You died"
            reward = -10
            isTerminal = True
            self.reset()

        # if self.steps > self.maxSteps:
        #     print "Out of time"
        #     reward = -1
        #     isTerminal = True
        #     self.reset()

        
        _, _, vx, vy = self.box.ball

        if vx != 0:
            k = round(float(vy)/vx, 1)
        else:
            k = None

        newState = (self.box.pad, k)
        return newState, reward, isTerminal

    def getActions(self, state):
        return self.actions

    def printStatus(self):
        bricks = ['=' for _ in self.box.bricks]
        ball = [' ' for _ in self.box.bricks]
        pad = [' ' for _ in self.box.bricks]

        x, _, _, _ = self.box.ball
        assert 0 <= int(x) <= len(ball), x
        ball[min(int(x), len(ball)-1)] = '*'
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
