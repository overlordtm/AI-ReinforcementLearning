from environment.brickBreaker import BrickBreakerEnv
from agent.ADPAgent import ADPActiveAgent
from environment.maze import MazeEnv

import pprint

if __name__ == "__main__":
	# env = MazeEnv()
	env = BrickBreakerEnv(3)
	agent = ADPActiveAgent(env, gamma=0.5, Rplus=10, Ne=5, maxPolicyIter=5000)

	agent.train(40)

	print "=== Policy ==="
	pprint.pprint(agent.P)
	print "=== Policy END ==="

	rHist = []
	for s in xrange(1000):
	    r, p = agent.executePolicy()
	    rHist.append(r)
	    # print len(p)

	rHistR = []

	for s in xrange(1000):
	    r, p = agent.executeRandomPolicy()
	    rHistR.append(r)

	print "reward (max/min/avg): ", max(rHist), min(rHist), sum(rHist)/float(len(rHist))
	print "Random reward (max/min/avg): ", max(rHistR), min(rHistR), sum(rHistR)/float(len(rHistR))

def bench():

	config = [(reps, g, Rplus, Ne) for reps in [10, 30, 50] for g in [0.1, 0.3, 0.5, 0.8, 0.9] for Rplus in [1,10] for Ne in [1,2,5,10]]

	for c in config:
		reps, gamma, Rplus, Ne = c
		env = BrickBreakerEnv(3)
		agent = ADPActiveAgent(env, gamma = gamma, Rplus = Rplus, Ne = Ne, maxPolicyIter = 2500)

		agent.train(reps)

		print "=== Policy ==="
		pprint.pprint(agent.P)
		print "=== Policy END ==="

		rHist = []
		for s in xrange(1000):
		    r, p = agent.executePolicy()
		    rHist.append(r)
		    # print p

		rHistR = []

		for s in xrange(1000):
		    r, p = agent.executeRandomPolicy()
		    rHistR.append(r)
		    # print p
		print "config", c
		print "reward (max/min/avg): ", max(rHist), min(rHist), sum(rHist)/float(len(rHist))
		print "Random reward (max/min/avg): ", max(rHistR), min(rHistR), sum(rHistR)/float(len(rHistR))
