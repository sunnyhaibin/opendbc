from opendbc.car import structs
from opendbc.sunnypilot import SunnypilotParamFlags


class MadsCarController:
  def __init__(self):
    super().__init__()
    self.dashed_lanes = False

  def update(self, CC: structs.CarControl) -> None:
    enable_mads = CC.sunnypilotParams & SunnypilotParamFlags.ENABLE_MADS

    if enable_mads:
      self.dashed_lanes = CC.madsEnabled and not CC.latActive
    else:
      self.dashed_lanes = CC.hudControl.lanesVisible
