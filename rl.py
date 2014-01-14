from environment.brickBreaker import BrickBreakerEnv
from agent.ADPAgent import ADPActiveAgent
from environment.maze import MazeEnv

import pprint

if __name__ == "__main__":
	# env = MazeEnv()
	env = BrickBreakerEnv(3)
	agent = ADPActiveAgent(env, gamma=0.3, Rplus=1, Ne=2, maxPolicyIter=5000)

	agent.train(30)

	print "=== Policy ==="
	# pprint.pprint(agent.UHist)

	s = set()

	for U in agent.UHist:
		for k in U.keys():
			s.add(k)

	f = list(s)

	print "\t".join(map(repr,f))

	print "\t".join(str(U.get(f, 0)) for f in U for U in agent.UHist)


	print "=== Policy END ==="

	rHist = []
	for s in xrange(1000):
	    r, p = agent.executePolicy()
	    rHist.append(r)

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

		rHist = []
		for s in xrange(1000):
		    r, p = agent.executePolicy()
		    rHist.append(r)

		data = [reps, gamma, Rplus, Ne, max(rHist), min(rHist), sum(rHist)/float(len(rHist))]
		print "\t".join(map(str,data))
