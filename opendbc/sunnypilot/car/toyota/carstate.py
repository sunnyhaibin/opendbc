#!/usr/bin/env python3
# code originally by:
# arne182: https://github.com/arne182
# kumar:   https://github.com/rav4kumar

class SPCarstate:
  LEFT_SIDE = 65
  RIGHT_SIDE = 66
  BLINDSPOT_THRESHOLD = 10
  COUNTER_RESET = 100

  def __init__(self):
    self._left_blindspot = False
    self._left_blindspot_d1 = 0
    self._left_blindspot_d2 = 0
    self._left_blindspot_counter = 0

    self._right_blindspot = False
    self._right_blindspot_d1 = 0
    self._right_blindspot_d2 = 0
    self._right_blindspot_counter = 0

  def update(self, cp):
    distance_1 = cp.vl["DEBUG"].get('BLINDSPOTD1')
    distance_2 = cp.vl["DEBUG"].get('BLINDSPOTD2')
    side = cp.vl["DEBUG"].get('BLINDSPOTSIDE')

    def is_blindspot(distance_1, distance_2):
      return distance_1 > self.BLINDSPOT_THRESHOLD or distance_2 > self.BLINDSPOT_THRESHOLD

    if all(val is not None for val in [distance_1, distance_2, side]):
      if side == self.LEFT_SIDE:  # Left blind spot
        if distance_1 != self._left_blindspot_d1 or distance_2 != self._left_blindspot_d2:
          self._left_blindspot_d1 = distance_1
          self._left_blindspot_d2 = distance_2
          self._left_blindspot_counter = self.COUNTER_RESET
        self._left_blindspot = is_blindspot(distance_1, distance_2)

      elif side == self.RIGHT_SIDE:  # Right blind spot
        if distance_1 != self._right_blindspot_d1 or distance_2 != self._right_blindspot_d2:
          self._right_blindspot_d1 = distance_1
          self._right_blindspot_d2 = distance_2
          self._right_blindspot_counter = self.COUNTER_RESET
        self._right_blindspot = is_blindspot(distance_1, distance_2)

      # Update counters
      self._left_blindspot_counter = max(0, self._left_blindspot_counter - 1)
      self._right_blindspot_counter = max(0, self._right_blindspot_counter - 1)

      # Reset blind spot status if counter reaches 0
      if self._left_blindspot_counter == 0:
        self._left_blindspot = False
        self._left_blindspot_d1 = self._left_blindspot_d2 = 0

      if self._right_blindspot_counter == 0:
        self._right_blindspot = False
        self._right_blindspot_d1 = self._right_blindspot_d2 = 0

    return self._left_blindspot, self._right_blindspot


