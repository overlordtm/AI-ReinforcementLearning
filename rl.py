from brickBreakerEnv import BrickBreakerEnv
from ADPActiveAgent import ADPActiveAgent
from mazeEnv import MazeEnv

import pprint

if __name__ == "__main__":
	# env = MazeEnv()
	env = BrickBreakerEnv(3)
	agent = ADPActiveAgent(env)


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
	    # print p
	print "reward (max/min/avg): ", max(rHist), min(rHist), sum(rHist)/float(len(rHist))
	print "Random reward (max/min/avg): ", max(rHistR), min(rHistR), sum(rHistR)/float(len(rHistR))
	print "ohai!"