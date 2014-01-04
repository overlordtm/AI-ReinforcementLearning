# Template for 2013/14 homework assignment for AI class
# by Aleksander Sadikov, December 2013
# Topic: reinforcement learning

import pprint
import numpy
import random

# the environment class
class Environment:
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

        if random.random > 0.8:
            action = random.choice(self.getActions(state))

        j, i = state
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

        if state in self.terminalStates:
            return None

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


# the agent class
class Agent:
    def __init__(self, e):
        # initialization of the agent

        state = e.getStartingState()

        self.P = None
        self.U = None
        self.M = {}
        self.R = {}
        self.e = e
        self.gamma = 0.9
        self.precepts = []
        self.lastAction = None
        self.steps = 0

        for _ in xrange(20):
            print "============= START ===================="
            self.start()
            # print "Transitions"
            # pprint.pprint(self.M)
            # print "Probs"
            # pprint.pprint(self.M)
            print "Policy"
            self.printPolicy(self.P)
            # pprint.pprint(self.P)

    def printPolicy(self, P):
        x = [[x for x in xrange(4)] for x in xrange(3)]

        buf = ""
        # x = numpy.zeros(self.e.width * self.e.height).reshape((self.e.height, self.e.width))
        for j in xrange(self.e.height):
            for i in xrange(self.e.width):
                buf = buf  + str(P.get((j, i), 'x')) + "\t"
            buf = buf + "\n"
        
        print buf

    def start(self):
        state = e.getStartingState()
        self.lastAction = random.choice(e.getActions(state))

        terminal = False

        while terminal is False:
            print "I am in state ", state
            # print "State:", state
            # percept = (state, action, newState, reward)
            action = self.lastAction

            newState, reward, terminal = e.do(state, action)
            percept = (state, action, newState, reward)
            self.precepts.append(percept)

            self.R[newState] = reward

            self.M = self.updateActiveModel(self.M, self.precepts, self.lastAction)
            self.P = self.policyIteration(self.M, self.R)

            if terminal is True:
                self.steps = 0
                print "Finished in", newState
                # self.precepts = []
                return

            self.lastAction = self.performanceElement(newState)

            # print newState
            state = newState
            # self.gamma = self.gamma * self.gamma
            self.steps = self.steps + 1


    def updateActiveModel(self, M, precepts, lastAction):
        seen = {}
        transitions = {}

        newM = {}

        for state, action, newState, _ in precepts:
            key = (state, action)
            seen[key] = seen.get(key, 0) + 1

        for (state, action, newState, _) in precepts:
            transitions[(state, action, newState)] = transitions.get((state, action, newState), 0) + 1

        # print "======================="
        # pprint.pprint(precepts)
        # pprint.pprint(seen)
        # pprint.pprint(transitions)

        for key, value in transitions.iteritems():
            state, action, newState = key

            if seen.get((state, action)) is not None:
                newM[key] = float(value)/seen[(state, action)]

        # pprint.pprint(newM)
        # print "======================="

        return newM


    def policyIteration(self, M, R):

        states = set()
        for state, _, _ in M.keys():
            states.add(state)

        # print "All known states", len(states)

        U = {s: 0.0 for s in states}

        P = {s: random.choice(self.e.getActions(s)) for s in states}

        while True:
            U = self.valueDetermination(P, U, M, R)
            unchanged = True
            for s in states:
                a = argmax(self.e.getActions(s), lambda a: self._expected_utility(a, s, U, M))

                if a != P.get(s):
                    # print "Best move in ", s ," is ", a
                    P[s] = a
                    unchanged = False

                if unchanged is True:
                    return P


    def valueDetermination(self, P, U, M, R, k = 20):

        def getPossibleOutcomes(s, a):
            return [(action, newState, prob) for (state, action, newState), prob in M.iteritems() if state == s and action == a]

        Ui = U.copy()

        for i in range(k):
            for state in P.keys():
                Ui[state] = R.get(state, 0) + self.gamma * sum(prob * U.get(newState, 0) for action, newState, prob in getPossibleOutcomes(state, P.get(state)))
                # print "U[", state, "] = ", Ui[state]

        for k, v in Ui.iteritems():
            print k, v, self.gamma

        return Ui

    def _expected_utility(self, a, s, U, M):

        return sum([prob * U.get(newState, 1) for (state, action, newState), prob in M.iteritems() if state == s and action == a])


    def performanceElement(self, state):
        if random.random() > 1 - (1.0 / (self.steps + 1)) or self.P.get(state) is None:
            return random.choice(e.getActions(state))
        else:
            return self.P[state]

def argmax(args, func):

    best = args[0]
    best_score = func(best)

    for a in args:
        score = func(a)
        if score > best_score:
            best_score = score
            best = a

    return best

if __name__ == "__main__":

    random.seed(100)
    e = Environment()

    a = Agent(e)
    # pprint.pprint(e.world)

