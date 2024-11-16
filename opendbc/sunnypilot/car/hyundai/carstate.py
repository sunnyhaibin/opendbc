from abc import ABC


class CarStateSP(ABC):
  def __init__(self):
    self.alt_button = 0
    self.main_cruise_enabled: bool = False
