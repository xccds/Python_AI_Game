import numpy as np
import copy
from operator import itemgetter
from tqdm import tqdm, trange


class TreeNode:
    
    def __init__(self, parent):
        self._parent = parent
        self._children = {}  # a map from action to TreeNode
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
        # update visit count
        self._Q += 1.0*(leaf_value - self._Q) / self._n_visits
        # update Q, a running average of values for all visits.
        # there is just: (v-Q)/(n+1)+Q = (v-Q+(n+1)*Q)/(n+1)=(v+n*Q)/(n+1)

    def update_recursive(self, leaf_value):
  
        # If it is not root, this node's parent should be updated first.
        if self._parent:
            self._parent.update_recursive(-leaf_value)
            # every step for revursive update,
            # we should change the perspective by the way of taking the negative
        self.update(leaf_value)

    def get_value(self, c_puct):

        self._u = (c_puct * np.sqrt(self._parent._n_visits) / (1 + self._n_visits))
        return self._Q + self._u

    def is_leaf(self):

        return self._children == {}


class MCTS:

    def __init__(self, c_puct=5, n_playout=400):

        self._root = TreeNode(parent=None)
        # root node do not have parent ,and sure with prior probability 1
        self._c_puct = c_puct
        self._n_playout = n_playout # times of tree search

    def _playout(self, state):

        node = self._root
        while(1):
            # select action in tree
            if node.is_leaf():
                # break if the node is leaf node

                break
            # Greedily select next move.
            action, node = node.select(self._c_puct)
            state.do_move(action)

        # Check for end of game
        end, winner = state.game_end()
        if not end:
            # expand the node
            node.expand(state.availables)
        # Evaluate the leaf node by random rollout
        leaf_value = self._evaluate_rollout(state)
        # Update value and visit count of nodes in this traversal.
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
            # If no break from the loop, issue a warning.
            print("WARNING: rollout reached move limit")

        if winner == -1:  # tie
            return 0
        else:
            return 1 if winner == player else -1

    def get_move(self, state):

        for n in trange(self._n_playout):
            state_copy = copy.deepcopy(state)
            self._playout(state_copy)
            # use deepcopy and playout on the copy state

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
            # reuse the tree
            # retain the tree that can continue to use
            # so update the tree with opponent's move and do mcts from the current node

        if len(sensible_moves) > 0:
            move = self.mcts.get_move(board)
            self.mcts.update_with_move(move)
            # every time when get a move, update the tree
        else:
            print("WARNING: the board is full")

        return move, None

    def __str__(self):
        return "MCTS {}".format(self.player)








