from templateRL import Environment

import random

class BrickBreakerEnv(Environment):

    """
    Actions: +5, +2, -6,...
    """
    def __init__(self):
        self.move_step = 1
        self.pad_pos = 0
        self.ball_pos = [0, 0]
        self.ball.left = 0
        self.ball.top = 0
        self.world_width = 12
        self.world_height = 12
        self.penalty = -0.04
        self.brick_reward = 1
        self.win_reward = 2
        self._create_bricks()
        self.bricks_left = self.world_width
        self.states = [i for i in xrange(-(self.world_width/2), (self.world_width/2) + 1)]
        self.left_terminal_state = self.states[0]
        self.right_terminal_state = self.states[-1]

    def getStartingState(self):
        return self.pad_pos

    def do(self, state, action):
        newState = self._get_new_state(action, state)
        isTerminal = self._is_terminal(newState)
        hit_brick = self._simulate_ball(action, state, newState, isTerminal)
        reward = self._get_reward(isTerminal, hit_brick)
        self.pad_pos = newState
        return newState, reward, isTerminal

    def _is_terminal(self, state):
        return self.left_terminal_state == state or self.right_terminal_state == state

    def _get_reward(self, is_terminal, hit_brick):
        reward = self.penalty
        if hit_brick:
            reward = self.brick_reward
        if is_terminal:
            reward = self.win_reward
        return reward

    def _get_new_state(self, steps, state):
        new_pos = self.pad_pos + steps

        if new_pos in self.states:
            return new_pos

        if new_pos > self.right_terminal_state:
            return self.right_terminal_state

        if new_pos < self.left_terminal_state:
            return self.left_terminal_state

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
    for i in xrange(10):
        a = random.choice(actions)
        if i == 5:
            print ""
        newState, reward, isTerminal = env.do(s, a)
        print s, '--', a, '-->', newState, reward, isTerminal
        s = newState

    print "Starting state: ", s
    print "Actions: ", a