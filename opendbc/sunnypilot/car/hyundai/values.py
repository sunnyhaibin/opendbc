from enum import IntFlag


class HyundaiFlagsSP(IntFlag):
  """
    Flags for Hyundai specific quirks within sunnypilot.
  """
  ENHANCED_SCC = 1
  HAS_LFA_BUTTON = 2
  LONGITUDINAL_MAIN_CRUISE_TOGGLEABLE = 2 ** 2
