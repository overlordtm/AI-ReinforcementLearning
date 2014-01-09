# Template for 2013/14 homework assignment for AI class
# by Aleksander Sadikov, December 2013
# Topic: reinforcement learning

# the environment class
class Environment:
    def __init__(self):
        # initialization of the environment
        # at least starting state probably needs to be defined
        pass

    def getStartingState(self):
        # returns starting state ID
        # internally the state can be represented as needed, externally the states are seen as their IDs
        # the agent thus distinguishes positions only by their IDs (integer; usually some sort of hash)
        return startStateID

    def do(self, state, action):
        # executes an action in a given state
        # and returns a new current state along with its reward and info on whether it's a terminal state
        return newState, reward, isTerminalState

    def getActions(self, state):
        # returns a list of possible actions in a given state
        # the notation/representation of the actions is up to the programmers
        # the agent simply uses the notation given by the environment
        # as the agent most likely stores the data about actions in a dictionary with the action notation being the key,
        # the notation should be an immutable object (e.g. integer, string, tuple, etc., but not a list)
        return listOfPossibleActions


# the agent class
class Agent:
    def __init__(self):
        # initialization of the agent
        pass
