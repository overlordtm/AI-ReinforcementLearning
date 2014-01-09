import pprint
import random
import time

from templateRL import Agent

class Model:
    def __init__(self):
        self.S = {} # known states {state: # visits}
        # self.precepts = []
        self.A = set() # known actions so far
        self.R = {} # known rewards {state: [reward history]}
        self.T = {} # transitions {(state, action, newState): transition prob}
        self.Z = {} # number of transitions by action {(state, actions, new state): # times}
        self.Q = {} # number of actions took in state {(state, action): # times}

    def addPrecept(self, precept):
        (state, action, newState, reward, terminal) = precept
        # self.precepts.append(precept)
        self.A.add(action)

        self.S[newState] = self.S.get(newState, 0) + 1
        self.Q[(state, action)] = self.Q.get((state, action), 0) + 1
        self.Z[(state, action, newState)] = self.Z.get((state, action, newState), 0) + 1

        oldRewards = self.R.get(newState) or 0
        # oldRewards.append(reward)
        self.R[newState] = (reward + oldRewards) / 2.0

        self._updateModel()

    def _updateModel(self):
        # thic can be optimized, update just for (state, action) tuple
        # start = timeit()
        for s1 in self.S.keys():
            for s2 in self.S.keys():
                for a in self.A:

                    if self.Q.get((s1, a)) is None:
                        prob = 1.0 / len(self.S)
                    else:
                        prob = float(self.Z.get((s1, a, s2), 0)) / self.Q[(s1, a)]
                    # assert prob <= 1.0 and prob >= 0.0
                    self.T[(s1, a, s2)] = prob
        # print "model updated", timeit() - start

    def getTransitions(self, s, a):
        assert s is not None and a is not None
        candidates = [(s2, prob) for (s1, action, s2), prob in self.T.iteritems() if s1 == s and action == a]
        assert abs(sum([p for _, p in candidates]) - 1) < 0.001 or len(candidates) == 0
        return candidates

    def visits(self, s):
        return self.S.get(s, 0)

    def avgReward(self, s):
        # TODO: unstable average
        return self.R.get(s)
        # if s in self.R:
        #     return sum(self.R.get(s)) / len(self.R.get(s))
        # else:
        #     return None

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


class ADPActiveAgent(Agent):
    def __init__(self, e):
        # initialization of the agent

        self.model = Model()

        self.P = None
        self.e = e
        self.gamma = 0.7
        self.lastAction = None
        self.steps = 0
        self.Rplus = 1
        self.Ne = 3


    # def printPolicy(self, P):
    #     buf = ""
    #     for j in xrange(self.e.height):
    #         for i in xrange(self.e.width):
    #             buf = buf  + str(P.get((j, i), 'x')) + "\t"
    #         buf = buf + "\n"
        
    #     print buf

    # def printUtility(self, U):
    #     buf = ""
    #     for j in xrange(self.e.height):
    #         for i in xrange(self.e.width):
    #             if (j, i) in U:
    #                 u = "%.2f" % U[(j, i)]
    #             else:
    #                 u = "x"
    #             buf = buf  + u + "\t"
    #         buf = buf + "\n"
        
    #     print buf

    # def comparePolicy(self, P1, P2):
    #     norm = 0
    #     for k in P1.keys():
    #         if P1.get(k) != P2.get(k):
    #             norm = norm + 1
    #     return norm

    def executePolicy(self):

        P = self.P

        state = self.e.getStartingState()
        terminal = False
        path = [state]

        rewardSum = 0

        count = 0
        while terminal is False:
            if count > 100:
                print "Infinite loop detected"
                break
            action = P.get(state)
            if action is None:
                print "WARNING: No action for state %s in policy" % repr(state)
                action = random.choice(self.e.getActions(state))
            assert action is not None, state
            state, reward, terminal = self.e.do(state, action)
            path.append(state)
            rewardSum = rewardSum + reward
            count = count + 1

        return rewardSum, path

    def executeRandomPolicy(self):

        state = self.e.getStartingState()
        terminal = False
        path = [state]

        rewardSum = 0

        count = 0
        while terminal is False:
            if count > 100:
                print "Infinite loop detected"
                break
            action = random.choice(self.e.getActions(state))
            state, reward, terminal = self.e.do(state, action)
            path.append(state)
            rewardSum = rewardSum + reward
            count = count + 1

        return rewardSum, path


    def train(self, k = 10):
        for i in xrange(k):
            start = int(time.time())
            print "======== TRAINING SEQUENCE %d START ========" % i
            self.start()
            print "== TRAINING SEQUENCE %d  (took %d seconds) (size: %d) ==" % (i, int(time.time())-start, len(self.model.T))

    def start(self):

        state = self.e.getStartingState()
        self.lastAction = random.choice(self.e.getActions(state))

        terminal = False
        self.gamma = 0.9
        self.steps = 0

        utilHist = {}

        while terminal is False:
            action = self.lastAction
            newState, reward, terminal = self.e.do(state, action)
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
        step = 0
        while converged is False:
            # print "Policy iteration step", step
            if step > 250:
                print "Warning: policy iteration max steps reached"
                break
            step = step + 1
            converged = True
            U = self.valueDetermination(P, U, model)
            for s in P.keys():
                a = argmax(self.e.getActions(s), lambda a: expected_utility(a, s, U, model))
                if a != P.get(s):
                    P[s] = a
                    converged = False
            # print "Policy iteration done"
        return P

    def valueDetermination(self, P, U, model, k = 10):
        R = lambda s: model.avgReward(state) or 0

        maxU = 0

        for i in xrange(k):
            for state in P.keys():
                if model.visits(state) > self.Ne:
                    assert self.gamma > 0 and self.gamma < 1
                    est = self.gamma * sum(prob * U[newState] for newState, prob in model.getTransitions(state, P.get(state)))
                else:
                    est = self.Rplus

                u = R(state) + est
                maxU = max(maxU, u)
                U[state] = u
        
        if maxU >= self.Rplus:
            self.Rplus = maxU+1

        return U

    def performanceElement(self, state):

        if random.random() > 0.9:
            action = random.choice(self.e.getActions(state))
        else:
            action = self.P.get(state) or random.choice(self.e.getActions(state))
        print action
        return action

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





