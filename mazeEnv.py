import numpy
import random

from templateRL import Environment

class MazeEnv(Environment):
    def __init__(self):
        # initialization of the environment
        # at least starting state probably needs to be defined
        # self.world = [[0 for x in xrange(4)] for x in xrange(3)]

        self.obstacles = [(1,1)]
        self.terminalStates = [(0, 3), (1, 3)]
        self.width = 4
        self.height = 3
        self.world = numpy.zeros(self.width * self.height).reshape((self.height, self.width))

        for j in range(self.height):
            for i in range(self.width):
                self.world[j][i] = -0.04

        for (j, i) in self.obstacles:
            self.world[j][i] = None

        self.world[0][3] = 1
        self.world[1][3] = -1
        pass

    def getStartingState(self):
        # returns starting state ID
        # internally the state can be represented as needed, externally the states are seen as their IDs
        # the agent thus distinguishes positions only by their IDs (integer; usually some sort of hash)
        return (2,0)

    def do(self, state, action):
        # executes an action in a given state
        # and returns a new current state along with its reward and info on whether it's a terminal state

        if random.random() > 0.9:
            action = random.choice(self.getActions(state))
        # r = random.random()
        # if r < 0.1:
        #     action = 'L'
        # elif r < 0.2:
        #     action = 'R'
        # else:
        #     action = 'U'

        j, i = state
        # if action not in self.getActions(state):
        #     return state, self.world[j][i], False

        if action == 'U':
            j = j - 1
        if action == 'D':
            j = j + 1
        if action == 'L':
            i = i - 1
        if action == 'R':
            i = i + 1

        newState = (j, i)
        isTerminal = newState in self.terminalStates
        reward = self.world[j][i]

        return newState, reward, isTerminal

    def getActions(self, state):
        # returns a list of possible actions in a given state
        # the notation/representation of the actions is up to the programmers
        # the agent simply uses the notation given by the environment
        # as the agent most likely stores the data about actions in a dictionary with the action notation being the key,
        # the notation should be an immutable object (e.g. integer, string, tuple, etc., but not a list)

        if state in self.obstacles:
            raise Exception("Kak si pa ti sem prisel")

        # if state in self.terminalStates:
        #     return []

        allActions = {'U': True, 'D': True, 'L': True, 'R': True}

        j, i = state

        if j == 0:
            allActions['U'] = False
        if j == self.height - 1:
            allActions['D'] = False
        if i == 0:
            allActions['L'] = False
        if i == self.width - 1:
            allActions['R'] = False

        if (j+1, i) in self.obstacles:
            allActions['D'] = False
        if (j-1, i) in self.obstacles:
            allActions['U'] = False
        if (j, i-1) in self.obstacles:
            allActions['L'] = False
        if (j, i+1) in self.obstacles:
            allActions['R'] = False

        return [key for key, value in allActions.iteritems() if value is True]