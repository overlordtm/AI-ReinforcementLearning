from environment.brickBreaker import BrickBreakerEnv
from agent.ADPAgent import ADPActiveAgent
from mazeEnv import MazeEnv

import pprint

if __name__ == "__main__":
	#env = MazeEnv()
	env = BrickBreakerEnv(3)
	agent = ADPActiveAgent(env, maxPolicyIter=1000)


	agent.train(10)

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

	print "reward (max/min/avg): ", max(rHist), min(rHist), sum(rHist)/float(len(rHist))
	print "Random reward (max/min/avg): ", max(rHistR), min(rHistR), sum(rHistR)/float(len(rHistR))

def bench():

	config = [(t, g/10.0, Rplus, Ne, maxPolicyIter) for t in xrange(10, 101, 10) for g in xrange(7,10) for Rplus in [1,2,5,10] for Ne in [1,2,3, 10] for maxPolicyIter in [250, 1000, 10000]]

	for reps, gamma, Rplus, Ne, maxPolicyIter in config:
		env = BrickBreakerEnv(5)
		agent = ADPActiveAgent(env, gamma = gamma, Rplus = Rplus, Ne = Ne, maxPolicyIter = maxPolicyIter)
		
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
		print "reward (max/min/avg): ", max(rHist), min(rHist), sum(rHist)/float(len(rHist))
		print "Random reward (max/min/avg): ", max(rHistR), min(rHistR), sum(rHistR)/float(len(rHistR))
