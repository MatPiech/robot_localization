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

        # previous action
        self.prev_action = None

        prob = 1.0 / (len(self.locations) * 4)
        self.P = prob * np.ones((len(self.locations), 4), dtype=np.float)


    def movementFactor(self, percept):
        movement_factors = np.zeros((len(self.locations), len(self.locations), 4), dtype=np.float)
        for i in range(len(self.locations)):
            x, y = self.locations[i]
            new_points = {'N': (x, y+1), 'E': (x+1, y), 'S': (x, y-1), 'W': (x-1, y)}

            # if self.prev_action == 'turnleft':
            #     for idx, dir in enumerate(new_points.keys()):
            #         new_point = new_points[dir]

            #         if new_point in self.locations:
            #             movement_factors[i,i, idx] = 0.05
            #             movement_factors[i,self.locations.index(new_point), idx] = 0.95
            # elif self.prev_action == 'turnright':
            #     for idx, dir in enumerate(new_points.keys()):
            #         new_point = new_points[dir]

            #         if new_point in self.locations:
            #             movement_factors[i,i, idx] = 0.05
            #             movement_factors[i,self.locations.index(new_point), idx] = 0.95
            if 'bump' in percept:
                movement_factors[i,i] = [1,1,1,1]
            elif self.prev_action == 'turnleft' or self.prev_action == 'turnright' or self.prev_action == None:
                movement_factors[i,i] = [1,1,1,1]
            elif self.prev_action == 'forward':
                for idx, new_point in enumerate(new_points.values()):

                    if new_point in self.locations:
                        movement_factors[i,i, idx] = 0.05
                        movement_factors[i,self.locations.index(new_point), idx] = 0.95
                    else:
                        movement_factors[i,i] = 1
            else:
                movement_factors[i,i] = [1,1,1,1]

        return movement_factors


    def sensorFactor(self, percept):
        sensor_factors = np.ones((len(self.locations), 4), dtype=np.float)
        sensor_available_percepts = ['fwd', 'right', 'bckwd', 'left']
        for dir in range(len(sensor_available_percepts)):
            for idx, loc in enumerate(self.locations):
                x, y = loc
                new_points = [(x, y+1), (x+1, y), (x, y-1), (x-1, y)]
                percepts_points = dict(zip(sensor_available_percepts, np.roll(new_points, -dir)))
                for point_key, point_val in percepts_points.items():
                    point_val = list(point_val)
                    if point_val in self.locations and point_key not in percept:
                        sensor_factors[idx, dir] *= 0.9
                    elif point_val not in self.locations and point_key in percept:
                        sensor_factors[idx, dir] *= 0.9
                    elif point_val in self.locations and point_key in percept:
                        sensor_factors[idx, dir] *= 0.1
                    elif point_val not in self.locations and point_key not in percept:
                        sensor_factors[idx, dir] *= 0.1

        return sensor_factors


    def __call__(self, percept):
        # update posterior
        # TODO PUT YOUR CODE HERE
        
        movement_factors = self.movementFactor(percept)
        
        sensor_factors = self.sensorFactor(percept)

        stacked_movement_factors = np.stack([np.dot(movement_factors[:,:,i].T, self.P[:,i]) for i in range(4)]).T

        #print(movement_factors.shape, sensor_factors.shape, self.P.shape, np.dot(movement_factors.T, self.P).shape)

        #self.P = np.multiply(sensor_factors, np.dot(movement_factors.T, self.P))
        self.P = np.multiply(sensor_factors, stacked_movement_factors)
        self.P = self.P / self.P.sum(keepdims=True)
        print(self.P)
        print(np.max(self.P))

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


    def getPosterior(self):
        # directions in order 'N', 'E', 'S', 'W'
        P_arr = np.zeros([self.size, self.size, 4], dtype=np.float)

        # put probabilities in the array
        # TODO PUT YOUR CODE HERE
        for dir in range(4):
            for idx, loc in enumerate(self.locations):
                P_arr[loc[0], loc[1], dir] = self.P[idx, dir]

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
