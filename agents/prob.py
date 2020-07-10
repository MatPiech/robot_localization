# prob.py
# This is

import random
import numpy as np

from gridutil import *

best_turn = {('N', 'E'): 'turnright',
             ('N', 'S'): 'turnright',
             ('N', 'W'): 'turnleft',
             ('E', 'S'): 'turnright',
             ('E', 'W'): 'turnright',
             ('E', 'N'): 'turnleft',
             ('S', 'W'): 'turnright',
             ('S', 'N'): 'turnright',
             ('S', 'E'): 'turnleft',
             ('W', 'N'): 'turnright',
             ('W', 'E'): 'turnright',
             ('W', 'S'): 'turnleft'}


class LocAgent:

    def __init__(self, size, walls, eps_perc, eps_move):
        self.size = size
        self.walls = walls
        # list of valid locations
        self.locations = list({*locations(self.size)}.difference(self.walls))
        # dictionary from location to its index in the list
        self.loc_to_idx = {loc: idx for idx, loc in enumerate(self.locations)}
        self.eps_perc = eps_perc
        self.eps_move = eps_move

        self.dirs = ['N', 'E', 'S', 'W']

        self.dirs_len = len(self.dirs)
        self.loc_len = len(self.locations)

        # previous action
        self.prev_action = None

        prob = 1.0 / (self.loc_len * self.dirs_len)
        self.P = prob * np.ones((self.loc_len * self.dirs_len), dtype=np.float)


    def __call__(self, percept):
        # update posterior
        # TODO PUT YOUR CODE HERE

        sensor_factors = self.sensor_factor(percept)
        movement_factors = self.movement_factor(percept)

        self.P = np.multiply(sensor_factors, np.dot(movement_factors, self.P))
        self.P = self.P / self.P.sum(keepdims=1)

        # -----------------------

        action = 'forward'
        # TODO CHANGE THIS HEURISTICS TO SPEED UP CONVERGENCE
        # if there is a wall ahead then lets turn
        if 'fwd' in percept:
            # higher chance of turning left to avoid getting stuck in one location
            action = np.random.choice(['turnleft', 'turnright'], 1, p=[0.8, 0.2])
        else:
            # prefer moving forward to explore
            action = np.random.choice(['forward', 'turnleft', 'turnright'], 1, p=[0.8, 0.1, 0.1])

        self.prev_action = action

        return action


    def sensor_factor(self, percept: list) -> np.ndarray:
        """Method to calculate robot sensor factor.

        Parameters
        ----------
        percept : list
            Robot sensor measurements.

        Returns
        -------
        np.ndarray
            Sensor factor.
        """
        sensor_factors = np.ones((self.loc_len * self.dirs_len))
        available_percepts = ['fwd', 'right', 'bckwd', 'left']

        for idx, loc in enumerate(self.locations):
            x, y = loc
            new_locs = {'N': (x, y+1), 'E': (x+1, y), 'S': (x, y-1), 'W': (x-1, y)}

            for dir_idx in range(self.dirs_len): 
                new_orientations = np.roll(list(new_locs.keys()), -dir_idx)
                percept_dirs = [new_orientations[available_percepts.index(p)] for p in percept]

                for dir in self.dirs:
                    new_loc = new_locs[dir]

                    if dir in percept_dirs:
                        if new_loc in self.locations:
                            sensor_factors[idx * self.dirs_len + dir_idx] *= 0.1
                        else:
                            sensor_factors[idx * self.dirs_len + dir_idx] *= 0.9
                    else:
                        if new_loc in self.locations:
                            sensor_factors[idx * self.dirs_len + dir_idx] *= 0.9
                        else:
                            sensor_factors[idx * self.dirs_len + dir_idx] *= 0.1

        return sensor_factors


    def movement_factor(self, percept: list) -> np.ndarray:
        """Method to calculate robot movement factor.

        Parameters
        ----------
        percept : list
            Robot sensor measurements.

        Returns
        -------
        np.ndarray
            Movement factor.
        """
        movement_factors = np.zeros((self.loc_len * self.dirs_len, self.loc_len * self.dirs_len))

        for idx, loc in enumerate(self.locations):
            x, y = loc
            new_locs = {'N': (x, y+1), 'E': (x+1, y), 'S': (x, y-1), 'W': (x-1, y)}

            for dir_idx, dir in enumerate(self.dirs):
                if 'bump' in percept or self.prev_action == None:
                    movement_factors[idx * self.dirs_len + dir_idx, idx * self.dirs_len + dir_idx] = 1.0
                if self.prev_action == 'forward':
                    new_loc = new_locs[dir]
                    if new_loc in self.locations:
                        new_idx = self.loc_to_idx[new_loc]
                        movement_factors[idx * self.dirs_len + dir_idx, idx * self.dirs_len + dir_idx] = 0.05
                        movement_factors[new_idx * self.dirs_len + dir_idx, idx * self.dirs_len + dir_idx] = 0.95
                    else:
                        movement_factors[idx * self.dirs_len + dir_idx, idx * self.dirs_len + dir_idx] = 1.0                        
                elif self.prev_action == 'turnleft':
                    _, left_dir = self.turnleft(loc, dir)
                    left_dir = self.dirs.index(left_dir)
                    movement_factors[idx * self.dirs_len + dir_idx, idx * self.dirs_len + dir_idx] = 0.05
                    movement_factors[idx * self.dirs_len + left_dir, idx * self.dirs_len + dir_idx] = 0.95
                elif self.prev_action == 'turnright':
                    _, right_dir = self.turnright(loc, dir)
                    right_dir = self.dirs.index(right_dir)
                    movement_factors[idx * self.dirs_len + dir_idx, idx * self.dirs_len + dir_idx] = 0.05
                    movement_factors[idx * self.dirs_len + right_dir, idx * self.dirs_len + dir_idx] = 0.95

        return movement_factors


    def getPosterior(self):
        # directions in order 'N', 'E', 'S', 'W'
        P_arr = np.zeros([self.size, self.size, 4], dtype=np.float)

        # put probabilities in the array
        # TODO PUT YOUR CODE HERE
        for dir in range(self.dirs_len):
            for idx, loc in enumerate(self.locations):
                P_arr[loc[0], loc[1], dir] = self.P[idx * self.dirs_len + dir]

        # -----------------------

        return P_arr

    def forward(self, cur_loc, cur_dir):
        if cur_dir == 'N':
            ret_loc = (cur_loc[0], cur_loc[1] + 1)
        elif cur_dir == 'E':
            ret_loc = (cur_loc[0] + 1, cur_loc[1])
        elif cur_dir == 'W':
            ret_loc = (cur_loc[0] - 1, cur_loc[1])
        elif cur_dir == 'S':
            ret_loc = (cur_loc[0], cur_loc[1] - 1)
        ret_loc = (min(max(ret_loc[0], 0), self.size - 1), min(max(ret_loc[1], 0), self.size - 1))
        return ret_loc, cur_dir

    def backward(self, cur_loc, cur_dir):
        if cur_dir == 'N':
            ret_loc = (cur_loc[0], cur_loc[1] - 1)
        elif cur_dir == 'E':
            ret_loc = (cur_loc[0] - 1, cur_loc[1])
        elif cur_dir == 'W':
            ret_loc = (cur_loc[0] + 1, cur_loc[1])
        elif cur_dir == 'S':
            ret_loc = (cur_loc[0], cur_loc[1] + 1)
        ret_loc = (min(max(ret_loc[0], 0), self.size - 1), min(max(ret_loc[1], 0), self.size - 1))
        return ret_loc, cur_dir

    @staticmethod
    def turnright(cur_loc, cur_dir):
        dir_to_idx = {'N': 0, 'E': 1, 'S': 2, 'W': 3}
        dirs = ['N', 'E', 'S', 'W']
        idx = (dir_to_idx[cur_dir] + 1) % 4
        return cur_loc, dirs[idx]

    @staticmethod
    def turnleft(cur_loc, cur_dir):
        dir_to_idx = {'N': 0, 'E': 1, 'S': 2, 'W': 3}
        dirs = ['N', 'E', 'S', 'W']
        idx = (dir_to_idx[cur_dir] + 4 - 1) % 4
        return cur_loc, dirs[idx]
