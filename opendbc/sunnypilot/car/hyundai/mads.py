from abc import ABC
from collections import namedtuple

from opendbc.car import DT_CTRL, structs

MadsDataSP = namedtuple("MadsDataSP",
                        ["enable_mads", "lat_active", "disengaging", "paused"])


class MadsCarController(ABC):
  def __init__(self):
    self.lat_disengage_blink = 0
    self.lat_disengage_init = False
    self.prev_lat_active = False

  # display LFA "white_wheel" and LKAS "White car + lanes" when not CC.latActive
  def mads_status_update(self, CC: structs.CarControl, frame: int) -> MadsDataSP:
    if CC.latActive:
      self.lat_disengage_init = False
    elif self.prev_lat_active:
      self.lat_disengage_init = True

    if not self.lat_disengage_init:
      self.lat_disengage_blink = frame

    paused = CC.madsActive and not CC.latActive
    disengaging = (frame - self.lat_disengage_blink) * DT_CTRL < 1.0 if self.lat_disengage_init else False

    self.prev_lat_active = CC.latActive

    return MadsDataSP(CC.sunnyLiveParams.enableMads, CC.latActive, disengaging, paused)

  def update(self, CC: structs.CarControl, frame: int) -> MadsDataSP:
    mads = self.mads_status_update(CC, frame)
    return mads
