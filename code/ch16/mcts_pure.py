import numpy as np
import copy
from operator import itemgetter
from tqdm import tqdm, trange


class TreeNode:
    
    def __init__(self, parent):
        self._parent = parent
        self._children = {}  
        self._n_visits = 0
        self._Q = 0
        self._u = 0

    def expand(self, actions):

        for action in actions:
            if action not in self._children:
                self._children[action] = TreeNode(self)

    def select(self, c_puct):

        return max(self._children.items(),
                   key=lambda act_node: act_node[1].get_value(c_puct))

    def update(self, leaf_value):
 
        self._n_visits += 1
        self._Q += 1.0*(leaf_value - self._Q) / self._n_visits

    def update_recursive(self, leaf_value):
        if self._parent:
            self._parent.update_recursive(-leaf_value)
        self.update(leaf_value)

    def get_value(self, c_puct):

        self._u = (c_puct * np.sqrt(self._parent._n_visits) / (1 + self._n_visits))
        return self._Q + self._u

    def is_leaf(self):

        return self._children == {}


class MCTS:

    def __init__(self, c_puct=5, n_playout=400):

        self._root = TreeNode(parent=None)
        self._c_puct = c_puct
        self._n_playout = n_playout 

    def _playout(self, state):

        node = self._root
        while(True):
            if node.is_leaf():
                break
            action, node = node.select(self._c_puct)
            state.do_move(action)

        end, winner = state.game_end()
        if not end:
            node.expand(state.availables)
        leaf_value = self._evaluate_rollout(state)
        node.update_recursive(-leaf_value)

    @staticmethod
    def rollout_policy_fn(state):
        action_probs = np.random.rand(len(state.availables)) # rollout randomly
        return zip(state.availables, action_probs)

    def _evaluate_rollout(self, state, limit=5000):

        player = state.current_player
        for i in range(limit):
            end, winner = state.game_end()
            if end:
                break
            action_probs = self.rollout_policy_fn(state)
            max_action = max(action_probs, key=itemgetter(1))[0]
            state.do_move(max_action)
        else:
            print("WARNING: rollout reached move limit")

        if winner == -1:  # tie
            return 0
        else:
            return 1 if winner == player else -1

    def get_move(self, state):

        for n in trange(self._n_playout):
            state_copy = copy.deepcopy(state)
            self._playout(state_copy)

        return max(self._root._children.items(),
                   key=lambda act_node: act_node[1]._n_visits)[0]

    def update_with_move(self, last_move):

        if last_move in self._root._children:
            self._root = self._root._children[last_move]
            self._root._parent = None
        else:
            self._root = TreeNode(None)

    def __str__(self):
        return "MCTS"

class MCTSPlayer:

    def __init__(self, c_puct=5, n_playout=400):
        self.mcts = MCTS(c_puct, n_playout)

    def reset_player(self):
        self.mcts.update_with_move(-1) # reset the node

    def get_action(self, board,is_selfplay=False,print_probs_value=0):

        sensible_moves = board.availables
        if board.last_move != -1:
            self.mcts.update_with_move(last_move=board.last_move)

        if len(sensible_moves) > 0:
            move = self.mcts.get_move(board)
            self.mcts.update_with_move(move)

        else:
            print("WARNING: the board is full")

        return move, None

    def __str__(self):
        return "MCTS {}".format(self.player)








