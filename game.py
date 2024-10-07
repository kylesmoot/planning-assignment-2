import numpy as np
import copy

class BoardState:
    """
    Represents a state in the game
    """

    def __init__(self):
        """
        Initializes a fresh game state
        """
        self.N_ROWS = 8
        self.N_COLS = 7

        self.state = np.array([1,2,3,4,5,3,50,51,52,53,54,52])
        self.decode_state = [self.decode_single_pos(d) for d in self.state]

    def update(self, idx, val):
        """
        Updates both the encoded and decoded states
        """
        self.state[idx] = val
        self.decode_state[idx] = self.decode_single_pos(self.state[idx])

    def make_state(self):
        """
        Creates a new decoded state list from the existing state array
        """
        return [self.decode_single_pos(d) for d in self.state]

    def encode_single_pos(self, cr: tuple):
        """
        Encodes a single coordinate (col, row) -> Z

        Input: a tuple (col, row)
        Output: an integer in the interval [0, 55] inclusive

        """
        return cr[0] + self.N_COLS * cr[1]

    def decode_single_pos(self, n: int):
        """
        Decodes a single integer into a coordinate on the board: Z -> (col, row)

        Input: an integer in the interval [0, 55] inclusive
        Output: a tuple (col, row)

        """
        col = n % self.N_COLS
        row = n // self.N_COLS
        return (col, row)

    def is_termination_state(self):
        """
        Checks if the current state is a termination state. Termination occurs when
        one of the player's move their ball to the opposite side of the board.

        You can assume that `self.state` contains the current state of the board, so
        check whether self.state represents a termainal board state, and return True or False.
        
        """
        
        if (self.is_valid()):
            white = self.get_white()
            white_ball = self.get_white_ball()
            black = self.get_black()
            black_ball = self.get_black_ball()
            white_goal = np.any([x < 56 and x >= 49 and x == white_ball for x in white])
            black_goal = np.any([x < 7 and x >= 0 and x == black_ball for x in black])
            return white_goal or black_goal
        else:
            return False

    def is_valid(self):
        """
        Checks if a board configuration is valid. This function checks whether the current
        value self.state represents a valid board configuration or not. This encodes and checks
        the various constrainsts that must always be satisfied in any valid board state during a game.

        If we give you a self.state array of 12 arbitrary integers, this function should indicate whether
        it represents a valid board configuration.

        Output: return True (if valid) or False (if not valid)
        
        """
        white = self.get_white()
        white_ball = self.get_white_ball()
        black = self.get_black()
        black_ball = self.get_black_ball()

        max_val = self.N_ROWS * self.N_COLS

        white_valid = np.all([x < max_val and x >= 0 for x in white])
        black_valid = np.all([x < max_val and x >= 0 for x in black])

        white_ball_valid = white_ball in white and white_ball < max_val and white_ball >= 0
        black_ball_valid = black_ball in black and white_ball < max_val and white_ball >= 0

        # test for overlap
        overlap = np.concatenate((white, black))
        u, c = np.unique(overlap, return_counts=True)
        overlap_valid = np.all([x == 1 for x in c])

        return white_valid and white_ball_valid and black_valid and black_ball_valid and overlap_valid
    
    def get_white(self):
        return self.state[0:5]
    
    def get_white_ball(self):
        return self.state[5]
    
    def get_black(self):
        return self.state[6:11]
    
    def get_black_ball(self):
        return self.state[11]

class Rules:

    @staticmethod
    def single_piece_actions(board_state: BoardState, piece_idx):
        """
        Returns the set of possible actions for the given piece, assumed to be a valid piece located
        at piece_idx in the board_state.state.

        Inputs:
            - board_state, assumed to be a BoardState
            - piece_idx, assumed to be an index into board_state, identfying which piece we wish to
              enumerate the actions for.

        Output: an iterable (set or list or tuple) of integers which indicate the encoded positions
            that piece_idx can move to during this turn.
        
        """

        actions = []

        if (board_state.is_valid()):
            white = board_state.get_white()
            white_ball = board_state.get_white_ball()
            black = board_state.get_black()
            black_ball = board_state.get_black_ball()
            piece = board_state.state[piece_idx]
            pos = board_state.decode_single_pos(piece)

            locs = [
                (pos[0] + 1, pos[1] - 2),
                (pos[0] - 1, pos[1] - 2),
                (pos[0] + 2, pos[1] - 1),
                (pos[0] - 2, pos[1] - 1),
                (pos[0] + 2, pos[1] + 1),
                (pos[0] - 2, pos[1] + 1),
                (pos[0] + 1, pos[1] + 2),
                (pos[0] - 1, pos[1] + 2),
            ]

            print(locs)

            for l in locs:
                enc_loc = board_state.encode_single_pos(l)
                if (piece != white_ball and
                    piece != black_ball and
                    l[0] >= 0 and l[0] < board_state.N_COLS and
                    l[1] >= 0 and l[1] < board_state.N_ROWS and
                    enc_loc not in white and
                    enc_loc not in black):
                        actions.append(enc_loc)

        return actions

    @staticmethod
    def single_ball_actions(board_state: BoardState, player_idx):
        """
        Returns the set of possible actions for moving the specified ball, assumed to be the
        valid ball for plater_idx  in the board_state

        Inputs:
            - board_state, assumed to be a BoardState
            - player_idx, either 0 or 1, to indicate which player's ball we are enumerating over
        
        Output: an iterable (set or list or tuple) of integers which indicate the encoded positions
            that player_idx's ball can move to during this turn.
        """

        white = board_state.get_white()
        black = board_state.get_black()

        if player_idx == 0:
            # white ball
            pieces = white
            ball = board_state.get_white_ball()
            pieces_opp = black
        else:
            # black ball
            pieces = black
            ball = board_state.get_black_ball()
            pieces_opp = white

        actions = []

        ball_pos = board_state.decode_single_pos(ball)

        for piece in pieces:
            if piece != ball:
                pos = board_state.decode_single_pos(piece)

                is_same_col = pos[0] == ball_pos[0]
                is_same_row = pos[1] == ball_pos[1]

                # diagonal pieces will have a slope of 1 or -1
                slope = (ball_pos[1] - pos[1]) / (ball_pos[0] - pos[0])
                is_diagonal = (slope == 1) or (slope == -1)

                if (is_same_col or is_same_row or is_diagonal):
                    # check to see if there are any opposing pieces in the way
                    for opp in pieces_opp:
                        pos_opp = board_state.decode_single_pos(opp)
                        opp_same_col = pos_opp[0] == ball_pos[0]
                        opp_same_row = pos_opp[1] == ball_pos[1]

                        opp_slope = (ball_pos[1] - pos_opp[1]) / (ball_pos[0] - pos_opp[0])
                        opp_diagonal = (opp_slope == 1) or (opp_slope == -1)

                        if (not opp_same_col and
                            not opp_same_row and
                            not opp_diagonal):
                                actions.append(piece)

        return actions

class GameSimulator:
    """
    Responsible for handling the game simulation
    """

    def __init__(self, players):
        self.game_state = BoardState()
        self.current_round = -1 ## The game starts on round 0; white's move on EVEN rounds; black's move on ODD rounds
        self.players = players

    def run(self):
        """
        Runs a game simulation
        """
        while not self.game_state.is_termination_state():
            ## Determine the round number, and the player who needs to move
            self.current_round += 1
            player_idx = self.current_round % 2
            ## For the player who needs to move, provide them with the current game state
            ## and then ask them to choose an action according to their policy
            action, value = self.players[player_idx].policy( self.game_state.make_state() )
            print(f"Round: {self.current_round} Player: {player_idx} State: {tuple(self.game_state.state)} Action: {action} Value: {value}")

            if not self.validate_action(action, player_idx):
                ## If an invalid action is provided, then the other player will be declared the winner
                if player_idx == 0:
                    return self.current_round, "BLACK", "White provided an invalid action"
                else:
                    return self.current_round, "WHITE", "Black probided an invalid action"

            ## Updates the game state
            self.update(action, player_idx)

        ## Player who moved last is the winner
        if player_idx == 0:
            return self.current_round, "WHITE", "No issues"
        else:
            return self.current_round, "BLACK", "No issues"

    def generate_valid_actions(self, player_idx: int):
        """
        Given a valid state, and a player's turn, generate the set of possible actions that player can take

        player_idx is either 0 or 1

        Input:
            - player_idx, which indicates the player that is moving this turn. This will help index into the
              current BoardState which is self.game_state
        Outputs:
            - a set of tuples (relative_idx, encoded position), each of which encodes an action. The set should include
              all possible actions that the player can take during this turn. relative_idx must be an
              integer on the interval [0, 5] inclusive. Given relative_idx and player_idx, the index for any
              piece in the boardstate can be obtained, so relative_idx is the index relative to current player's
              pieces. Pieces with relative index 0,1,2,3,4 are block pieces that like knights in chess, and
              relative index 5 is the player's ball piece.
        """
        actions = []
        r = range(5) if player_idx == 0 else range(6, 11)
        offset = 0 if player_idx == 0 else 6

        for i in r:
            moves = Rules.single_piece_actions(self.game_state, i)
            print(moves)
            for m in moves:
                actions.append((i - offset, m)) # since this is a relative index, for player 2
                                                # we need to subtract 6
        moves = Rules.single_ball_actions(self.game_state, player_idx)
        for m in moves:
            actions.append((5, m))

        return actions

    def validate_action(self, action: tuple, player_idx: int):
        """
        Checks whether or not the specified action can be taken from this state by the specified player

        Inputs:
            - action is a tuple (relative_idx, encoded position)
            - player_idx is an integer 0 or 1 representing the player that is moving this turn
            - self.game_state represents the current BoardState

        Output:
            - if the action is valid, return True
            - if the action is not valid, raise ValueError
        """

        valid_actions = self.generate_valid_actions(player_idx)

        for a in valid_actions:
            if (action == a):
                return True

        raise ValueError('not allowed')
    
    def update(self, action: tuple, player_idx: int):
        """
        Uses a validated action and updates the game board state
        """
        offset_idx = player_idx * 6 ## Either 0 or 6
        idx, pos = action
        self.game_state.update(offset_idx + idx, pos)
