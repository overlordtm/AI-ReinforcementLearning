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
        self.width = 8 #4
        self.height = 10#3
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

        if random.random() > 0.8:
            action = random.choice(self.getActions(state))


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

class Model:

    def __init__(self):

        self.S = {}
        self.precepts = []
        self.A = set()
        self.R = {}
        self.T = {}
        self.Z = {}
        self.Q = {}

    def addPrecept(self, precept):
        (state, action, newState, reward, terminal) = precept
        # self.precepts.append(precept)
        self.A.add(action)

        self.S[newState] = self.S.get(newState, 0) + 1
        self.Q[(state, action)] = self.Q.get((state, action), 0) + 1
        self.Z[(state, action, newState)] = self.Z.get((state, action, newState), 0) + 1

        oldRewards = self.R.get(newState) or []
        oldRewards.append(reward)
        self.R[newState] = oldRewards

        self._updateModel()

    def _updateModel(self):
        for s1 in self.S.keys():
            for s2 in self.S.keys():
                for a in self.A:

                    if self.Q.get((s1, a)) is None:
                        prob = 1.0 / len(self.S)
                    else:
                        prob = float(self.Z.get((s1, a, s2), 0)) / self.Q[(s1, a)]
                    # assert prob <= 1.0 and prob >= 0.0
                    self.T[(s1, a, s2)] = prob

    def getTransitions(self, s, a):
        # assert s is not None and a is not None

        candidates = [(s2, prob) for (s1, action, s2), prob in self.T.iteritems() if s1 == s and action == a]

        # assert abs(sum([p for _, p in candidates]) - 1) < 0.001 or len(candidates) == 0

        return candidates

    def visits(self, s):
        return self.S.get(s, 0)

    def avgReward(self, s):
        # TODO: unstable average
        if s in self.R:
            return sum(self.R.get(s)) / len(self.R.get(s))
        else:
            return None

    def knownStates(self):
        return set(self.S.keys())

    def transitionGraph(self, name = "T.png"):

        import pydot
        graph = pydot.Dot()

        nodes = {key: pydot.Node(str(key)) for key, value in self.S.iteritems()}

        for (state, action, newState), prob in self.M.iteritems():

            if state not in nodes:
                nodes[state] = pydot.Node(str(state))
            if newState not in nodes:
                nodes[newState] = pydot.Node(str(newState))

            graph.add_edge(pydot.Edge(nodes[state], nodes[newState], label= "%s:%.2f" % (action, prob)))

        graph.write_png(name)


class Agent:
    def __init__(self, e):
        # initialization of the agent

        self.model = Model()

        self.P = None
        self.e = e
        self.gamma = 0.9
        self.lastAction = None
        self.steps = 0

        for _ in xrange(10):
            print "==== Learning step %d ====" % self.steps
            self.start()

        rHist = []
        for s in xrange(1):
            r, p = self.executePolicy(self.P)
            rHist.append(r)
            # print p

        rHistR = []
        print "reward (max/min/avg): ", max(rHist), min(rHist), sum(rHist)/float(len(rHist))


    def printPolicy(self, P):
        buf = ""
        for j in xrange(self.e.height):
            for i in xrange(self.e.width):
                buf = buf  + str(P.get((j, i), 'x')) + "\t"
            buf = buf + "\n"
        
        print buf

    def printUtility(self, U):
        buf = ""
        for j in xrange(self.e.height):
            for i in xrange(self.e.width):
                if (j, i) in U:
                    u = "%.2f" % U[(j, i)]
                else:
                    u = "x"
                buf = buf  + u + "\t"
            buf = buf + "\n"
        
        print buf

    def comparePolicy(self, P1, P2):
        norm = 0
        for k in P1.keys():
            if P1.get(k) != P2.get(k):
                norm = norm + 1
        return norm

    def executePolicy(self, P):

        state = e.getStartingState()
        terminal = False
        path = [state]

        rewardSum = 0

        while terminal is False:
            state, reward, terminal = e.do(state, P.get(state))
            path.append(state)
            rewardSum = rewardSum + reward

        return rewardSum, path


    def start(self):

        state = self.e.getStartingState()
        self.lastAction = random.choice(e.getActions(state))

        terminal = False
        self.gamma = 0.6
        self.steps = 0

        utilHist = {}

        while terminal is False:

            action = self.lastAction
            newState, reward, terminal = e.do(state, action)
            percept = (state, action, newState, reward, terminal)

            # updates model
            self.model.addPrecept(percept)

            self.P = self.policyIteration(self.model)

            if terminal is True:
                return

            self.lastAction = self.performanceElement(newState)

            state = newState
            self.steps = self.steps + 1
            # self.gamma = self.gamma * self.gamma

    def policyIteration(self, model):

        U = {s: 0 for s in model.knownStates()}
        P = {s: random.choice(self.e.getActions(s)) for s in model.knownStates()}

        converged = False
        while converged is False:
            converged = True
            U = self.valueDetermination(P, U, model)
            for s in P.keys():
                a = argmax(self.e.getActions(s), lambda a: expected_utility(a, s, U, model))
                if a != P.get(s):
                    P[s] = a
                    converged = False

        print "==== Step: %d ====" % self.steps
        # self.printPolicy(P)
        # self.printUtility(U)
        return P

    def valueDetermination(self, P, U, model, k = 10):

        Ne = 2
        Rplus = 1

        R = lambda s: model.avgReward(state) or 0

        for i in xrange(k):
            for state in P.keys():
                if model.visits(state) > Ne:
                    assert self.gamma > 0 and self.gamma < 1
                    est = self.gamma * sum(prob * U[newState] for newState, prob in model.getTransitions(state, P.get(state)))
                else:
                    est = Rplus

                U[state] = R(state) + est

        return U

    def performanceElement(self, state):

        if random.random() > 0.9:
            return random.choice(e.getActions(state))
        else:
            return self.P.get(state) or random.choice(e.getActions(state))

def expected_utility(a, s, U, model):
    return sum([prob * U[newState] for newState, prob in model.getTransitions(s, a)])

def argmax(args, func):
    assert hasattr(func, '__call__')

    best = args[0]
    best_score = func(best)

    for a in args[1:]:
        score = func(a)
        if score > best_score:
            best_score = score
            best = a

    return best

def testModel():
    m = Model((0, 0))
    m.addPrecept(((0,0), 1, (0, 1), 0.04))
    m.addPrecept(((0,0), 1, (1, 0), 0.04))
    m.addPrecept(((0,0), 2, (1, 0), 0.04))
    m.addPrecept(((0,0), 2, (1, 0), 0.5))

    pprint.pprint(m.T)

    print m.getTransitions((0,0), 1)

    for s in m.S.keys():
        print s, m.avgReward(s)

if __name__ == "__main__":

    # random.seed(100)
    e = Environment()
    a = Agent(e)

    # testModel()



