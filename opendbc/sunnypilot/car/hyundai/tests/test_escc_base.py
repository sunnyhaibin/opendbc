import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from opendbc.sunnypilot.car.hyundai.escc import EnhancedSmartCruiseControl, ESCC_MSG
from opendbc.car.hyundai.carstate import CarState
from opendbc.car import structs
from opendbc.sunnypilot.car.hyundai.values import HyundaiFlagsSP


@pytest.fixture
def CP():
  params = structs.CarParams()
  params.carFingerprint = "HYUNDAI_SONATA"
  params.sunnypilotCarParams.flags = HyundaiFlagsSP.ENHANCED_SCC.value
  return params


@pytest.fixture
def escc(CP):
  return EnhancedSmartCruiseControl(CP)


class TestEscc:
  def test_escc_msg_id(self, escc):
    assert escc.trigger_msg == ESCC_MSG

  @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
  @given(st.integers(min_value=0, max_value=255))
  def test_enabled_flag(self, CP, value):
    CP.sunnypilotCarParams.flags = value
    escc = EnhancedSmartCruiseControl(CP)
    assert escc.enabled == (value & HyundaiFlagsSP.ENHANCED_SCC)

  def test_refresh_car_state(self, escc, CP):
    CS = CarState(CP)
    CS.escc_cmd_act = 1
    CS.escc_aeb_warning = 1
    CS.escc_aeb_dec_cmd_act = 1
    CS.escc_aeb_dec_cmd = 1
    escc.refresh_car_state(CS)
    assert escc.CS == CS

  def test_update_scc12_message(self, escc, CP):
    car_state = CarState(CP)
    car_state.escc_cmd_act = 1
    car_state.escc_aeb_warning = 1
    car_state.escc_aeb_dec_cmd_act = 1
    car_state.escc_aeb_dec_cmd = 1
    escc.refresh_car_state(car_state)
    scc12_message = {}
    escc.update_scc12_message(scc12_message)
    assert scc12_message["AEB_CmdAct"] == 1
    assert scc12_message["CF_VSM_Warn"] == 1
    assert scc12_message["CF_VSM_DecCmdAct"] == 1
    assert scc12_message["CR_VSM_DecCmd"] == 1
    assert scc12_message["AEB_Status"] == 2

  def test_get_radar_escc_parser(self, escc):
    parser = escc.get_radar_parser_escc()
    assert parser is not None
    assert parser.dbc_name == b"hyundai_kia_generic"
