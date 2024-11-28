from opendbc.car import structs
from opendbc.car.toyota.values import ToyotaFlagsSP
from opendbc.car.toyota.toyotacan import create_set_bsm_debug_mode, create_bsm_polling_status

LEFT_BLINDSPOT = b"\x41"
RIGHT_BLINDSPOT = b"\x42"


class EnhancedBSM:
  def __init__(self, CP: structs.CarParams):
    self.CP = CP
    self.left_bsm_active = False
    self.right_bsm_active = False
    self.last_bsm_frame = 0
    self._left_blindspot = False
    self._right_blindspot = False
    self._left_blindspot_d1 = 0
    self._left_blindspot_d2 = 0
    self._left_blindspot_counter = 0
    self._right_blindspot_d1 = 0
    self._right_blindspot_d2 = 0
    self._right_blindspot_counter = 0

  @property
  def enabled(self):
    """Check if Enhanced BSM is enabled based on flags."""
    return self.CP.spFlags & ToyotaFlagsSP.SP_ENHANCED_BSM

  def create_bsm_messages(self, car_state, frame, e_bsm_rate=20, always_on=True):
    """
    Generate CAN messages for Enhanced BSM.

    :param car_state: Current car state object.
    :param frame: Current frame number.
    :param e_bsm_rate: Polling rate for BSM messages.
    :param always_on: Whether to keep BSM always active or conditional.
    :return: List of CAN messages.
    """
    can_sends = []

    # Left Blind Spot Monitoring
    if not self.left_bsm_active:
      if always_on or car_state.vEgo > 6:
        can_sends.append(create_set_bsm_debug_mode(LEFT_BLINDSPOT, True))
        self.left_bsm_active = True
    else:
      if not always_on and frame - self.last_bsm_frame > 50:
        can_sends.append(create_set_bsm_debug_mode(LEFT_BLINDSPOT, False))
        self.left_bsm_active = False
      if frame % e_bsm_rate == 0:
        can_sends.append(create_bsm_polling_status(LEFT_BLINDSPOT))
        self.last_bsm_frame = frame

    # Right Blind Spot Monitoring
    if not self.right_bsm_active:
      if always_on or car_state.vEgo > 6:
        can_sends.append(create_set_bsm_debug_mode(RIGHT_BLINDSPOT, True))
        self.right_bsm_active = True
    else:
      if not always_on and frame - self.last_bsm_frame > 50:
        can_sends.append(create_set_bsm_debug_mode(RIGHT_BLINDSPOT, False))
        self.right_bsm_active = False
      if frame % e_bsm_rate == e_bsm_rate // 2:
        can_sends.append(create_bsm_polling_status(RIGHT_BLINDSPOT))
        self.last_bsm_frame = frame

    return can_sends

  def update_blindspot_state(self, cp):
    """
    Update the blind spot states based on CAN data.

    :param cp: CANParser instance with current CAN data.
    """
    distance_1 = cp.vl["DEBUG"].get("BLINDSPOTD1")
    distance_2 = cp.vl["DEBUG"].get("BLINDSPOTD2")
    side = cp.vl["DEBUG"].get("BLINDSPOTSIDE")

    if all(val is not None for val in [distance_1, distance_2, side]):
      if side == ord(LEFT_BLINDSPOT):  # Left blind spot
        if distance_1 != self._left_blindspot_d1 or distance_2 != self._left_blindspot_d2:
          self._left_blindspot_d1 = distance_1
          self._left_blindspot_d2 = distance_2
          self._left_blindspot_counter = 100
        self._left_blindspot = distance_1 > 10 or distance_2 > 10

      elif side == ord(RIGHT_BLINDSPOT):  # Right blind spot
        if distance_1 != self._right_blindspot_d1 or distance_2 != self._right_blindspot_d2:
          self._right_blindspot_d1 = distance_1
          self._right_blindspot_d2 = distance_2
          self._right_blindspot_counter = 100
        self._right_blindspot = distance_1 > 10 or distance_2 > 10

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

  def get_blindspot_warnings(self):
    """
    Get the current warnings for left and right blind spots.

    :return: Tuple of (left_warning, right_warning).
    """
    return self._left_blindspot, self._right_blindspot


class BSMCarStateBase:
  def __init__(self):
    self.left_bsm_warning = False
    self.right_bsm_warning = False


class BSMCarController:
  def __init__(self, CP: structs.CarParams):
    self.BSM = EnhancedBSM(CP)

  def update(self, car_state, cp, frame):
    """
    Update the Enhanced BSM state and generate CAN messages.

    :param car_state: Current car state.
    :param cp: CANParser instance for accessing CAN signals.
    :param frame: Current frame number.
    :return: List of CAN messages.
    """
    if self.BSM.enabled:
      self.BSM.update_blindspot_state(cp)
      car_state.left_bsm_warning, car_state.right_bsm_warning = self.BSM.get_blindspot_warnings()
      return self.BSM.create_bsm_messages(car_state, frame)
    return []
