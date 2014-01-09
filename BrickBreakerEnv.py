from templateRL import Environment

import random
import box

class BrickBreakerEnv(Environment):

    """
    Actions: +5, +2, -6,...
    """
    def __init__(self):

        self.world_width = 6
        self.world_height = 6
        self.penalty = 0
        self.brick_reward = 1
        self.pad_reward = 1
        self.win_reward = 100
        self.game_over_penalty = -100

        self.post_init()

    def post_init(self):
        if self.world_width % 2 == 0:
            self.world_width = self.world_width + 1

        self.box_model = box.BoxModel(0, self.world_width, 0, self.world_height)
        self.states = [i for i in xrange(self.world_width)]
        self.bricks_left = self.box_model.bricks.count(1)
        self.pad_pos = self.world_width/2

    def getStartingState(self):
        return self.pad_pos

    def do(self, state, action):
        newState = action
        self.box_model.movePad(newState)
        x, _, _, _ = self.box_model.bounce()
        hit_brick = self.box_model.bricks.count(1) < self.bricks_left
        if hit_brick:
            self.bricks_left = self.box_model.bricks.count(1)

        reward = self._get_reward(hit_brick)
        self.pad_pos = newState
        print "state=", state, ", newState=", newState, ", reward=", reward, ", ball=", int(x)
        return newState, reward, reward == self.win_reward or reward == self.game_over_penalty

    def _is_terminal(self, state):
        return self.left_terminal_state == state or self.right_terminal_state == state

    def _get_reward(self, hit_brick):
        reward = self.penalty
        if hit_brick:
            reward = self.brick_reward
        if self.box_model.checkPad() is False:
            reward = self.game_over_penalty
        if self.box_model.checkPad() is True:
            reward = self.pad_reward
        return reward

    def _create_bricks(self):
        self.bricks = []
        for i in xrange(self.world_width):
            brick = (i, self.world_height, 1, 1)
            self.bricks.append(brick)

    def getActions(self, state):
        return self.states

if __name__ == '__main__':
    env = BrickBreakerEnv()
    s = env.getStartingState()
    actions = env.getActions(s)
    isTerminal = False
    random.seed(100)
    a = random.choice(actions)
    for i in xrange(10):
        newState, reward, isTerminal = env.do(s, a)
        print s, '--', a, '-->', newState, reward, isTerminal
        s = newState
        x, _, _, _ = env.box_model.ball
        a = int(x)

    print "Starting state: ", s
    print "Actions: ", a