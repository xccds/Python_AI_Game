class Board:

    def __init__(self, width, height, n_in_row):
        self.width = int(width)
        self.height = int(height)
        self.n_in_row = int(n_in_row)

    def reset_board(self, start_player=1):
        self.current_player = start_player 
        self.availables = list(range(self.width * self.height))
        self.states = {}
        self.last_move = -1

    def do_move(self, move):
        self.states[move] = self.current_player
        self.availables.remove(move)
        self.current_player = self.current_player % 2 + 1
        self.last_move = move

    def has_a_winner(self):
        width = self.width
        height = self.height
        states = self.states
        n = self.n_in_row
        moved = list(states.keys())
        if len(moved) < self.n_in_row + 2:
            return False, -1

        for m in moved:
            h = m // width
            w = m % width
            player = states[m]

            if (w in range(width - n + 1) and
                    len(set(states.get(i, -1) for i in range(m, m + n))) == 1):
                return True, player

            if (h in range(height - n + 1) and
                    len(set(states.get(i, -1) for i in range(m, m + n * width, width))) == 1):
                return True, player

            if (w in range(width - n + 1) and h in range(height - n + 1) and
                    len(set(states.get(i, -1) for i in range(m, m + n * (width + 1), width + 1))) == 1):
                return True, player

            if (w in range(n - 1, width) and h in range(height - n + 1) and
                    len(set(states.get(i, -1) for i in range(m, m + n * (width - 1), width - 1))) == 1):
                return True, player

        return False, -1

    def game_end(self):
        end, winner = self.has_a_winner()
        if end:
            return True, winner
        elif not len(self.availables):
            return True, -1
        return False, -1
