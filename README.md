# Localization project 
Project of calculating probability distribution of robot localization having unknown robot's orientation.

1. [Robot localization](#robot-localization)
2. [Heuristics](#heuristics)

Polish language version of documentation - [README_PL.md](./README_FILES/README_PL.md)

**Environment assumptions:**
- Robot doesn't always correctly perform the maneuver of turning and driving forward. It is possible, with factor **ϵm=0.05**, that robot:
    - stay in the same place when the last action was *forward* 
    - doesn't turn if the last action was *turnleft* or *turnright*.
- Robot's sensor return list of directions relative to the robot in which obstacles have been detected e.g. ['fwd', 'right'] which means that obstacles have been detected straight ahead and to the right of the robot according to the current robot orientation. Sensors aren't perfect and can give incorrect measurement with factor **ϵs=0.1**:
  - sensor detect obstacle even though it is not there 
  - sensor doesn't detect obstacle even though it is there 
- Value *bump* in percept list of sensor can improve accuracy of localization.

**Tasks**
- Implement functions to calculate probability distribution of robot localization.
- Modification of robot motion heuristics to accelerate algorithm convergence. Robot should choose actions which give him most information.

## Robot localization
![5 first steps](./README_FILES/steps_image.png)

## Heuristics
To choose next robot's move was tested several heuristics:
- initial 
- right hand
- left hand

For each heuristics' step was calculated value of entropy what is show in grouped plot below.

![Used heuristics plots](./README_FILES/40_steps_entropy.png)