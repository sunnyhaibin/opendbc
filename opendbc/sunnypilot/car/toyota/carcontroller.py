#!/usr/bin/env python3
# credits:
# arne182: https://github.com/arne182
# kumar:   https://github.com/rav4kumar

from opendbc.car.toyota import toyotacan
from opendbc.car.toyota.values import ToyotaFlagsSP
from opendbc.car.common.numpy_fast import clip

LEFT_BLINDSPOT = b"\x41"
RIGHT_BLINDSPOT = b"\x42"

class SPController:
  def __init__(self):
    self.CP = CP
    self.left_blindspot_debug_enabled = False
    self.right_blindspot_debug_enabled = False
    self.last_blindspot_frame = 0
    if CP.spFlags & ToyotaFlagsSP.SP_AUTO_BRAKE_HOLD:
      self.brake_hold_active: bool = False
      self._brake_hold_counter: int = 0
      self._brake_hold_reset: bool = False
      self._prev_brake_pressed: bool = False

  def create_enhanced_bsm_messages(self, CS, frame, e_bsm_rate=20, always_on=True):
    can_sends = []

    # Left BSM
    if not self.left_blindspot_debug_enabled:
      if always_on or CS.out.vEgo > 6:
        can_sends.append(toyotacan.create_set_bsm_debug_mode(LEFT_BLINDSPOT, True))
        self.left_blindspot_debug_enabled = True
    else:
      if not always_on and frame - self.last_blindspot_frame > 50:
        can_sends.append(toyotacan.create_set_bsm_debug_mode(LEFT_BLINDSPOT, False))
        self.left_blindspot_debug_enabled = False
      if frame % e_bsm_rate == 0:
        can_sends.append(toyotacan.create_bsm_polling_status(LEFT_BLINDSPOT))
        self.last_blindspot_frame = frame

    # Right BSM
    if not self.right_blindspot_debug_enabled:
      if always_on or CS.out.vEgo > 6:
        can_sends.append(toyotacan.create_set_bsm_debug_mode(RIGHT_BLINDSPOT, True))
        self.right_blindspot_debug_enabled = True
    else:
      if not always_on and frame - self.last_blindspot_frame > 50:
        can_sends.append(toyotacan.create_set_bsm_debug_mode(RIGHT_BLINDSPOT, False))
        self.right_blindspot_debug_enabled = False
      if frame % e_bsm_rate == 0:
        can_sends.append(toyotacan.create_bsm_polling_status(RIGHT_BLINDSPOT))
        self.last_blindspot_frame = frame

    return can_sends

  def create_auto_brake_hold_messages(self, CS):
    can_sends = []

    # Auto brake hold logic
    brake_pressed = CS.out.brakePressed
    self._brake_hold_reset = False

    # Enable auto brake hold when the vehicle is stationary, and the driver holds the brake
    if CS.out.standstill and not self.brake_hold_active and brake_pressed and not self._prev_brake_pressed:
      self._brake_hold_counter += 1
      if self._brake_hold_counter > 50:  # arbitrary delay for activation
        self.brake_hold_active = True
        self._brake_hold_counter = 0
        # Send the activation message
        can_sends.append(toyotacan.create_brake_hold_activate())

    # Handle release conditions
    elif self.brake_hold_active and not brake_pressed:
      self.brake_hold_active = False
      self._brake_hold_reset = True
      # Send the deactivation message
      can_sends.append(toyotacan.create_brake_hold_deactivate())

    self._prev_brake_pressed = brake_pressed
    return can_sends