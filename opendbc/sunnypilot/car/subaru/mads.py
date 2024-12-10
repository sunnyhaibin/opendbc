"""
The MIT License

Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Last updated: July 29, 2024
"""

from opendbc.car import structs

from opendbc.sunnypilot.mads_base import MadsCarStateBase

ButtonType = structs.CarState.ButtonEvent.Type


class MadsCarState(MadsCarStateBase):
  def __init__(self):
    super().__init__()

  @staticmethod
  def create_lkas_button_events(cur_btn: int, prev_btn: int,
                                buttons_dict: dict[int, structs.CarState.ButtonEvent.Type]) -> list[structs.CarState.ButtonEvent]:
    events: list[structs.CarState.ButtonEvent] = []

    if cur_btn == prev_btn:
      return events

    state_changes = [
      {"pressed": prev_btn != cur_btn and cur_btn != 2 and not (prev_btn == 2 and cur_btn == 1)},
      {"pressed": prev_btn != cur_btn and cur_btn == 2 and cur_btn != 1},
    ]

    for change in state_changes:
      if change["pressed"]:
        events.append(structs.CarState.ButtonEvent(pressed=change["pressed"],
                                                   type=buttons_dict.get(cur_btn, ButtonType.unknown)))
    return events
