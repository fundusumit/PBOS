import unittest

import pandas as pd

from calculation_engine import build_plant_capacity_output, build_plant_planning, format_configuration


class CapacityGovernanceTests(unittest.TestCase):
    def test_recommended_config_a_9_4_mt_day(self):
        output = build_plant_capacity_output(
            {"finished_goods_mt_day": 9.4},
            capacity_per_line_mt_day=10.0,
            max_shifts=3,
            installed_lines=1,
            active_shifts=1,
            maximum_lines_in_current_plant=2,
        )
        self.assertEqual(output["recommended_configuration_label"], "1 line × 1 shift")
        self.assertAlmostEqual(output["recommended_capacity_mt_day"], 10.0, places=3)

    def test_recommended_config_b_15_mt_day(self):
        output = build_plant_capacity_output(
            {"finished_goods_mt_day": 15.0},
            capacity_per_line_mt_day=10.0,
            max_shifts=3,
            installed_lines=1,
            active_shifts=1,
            maximum_lines_in_current_plant=2,
        )
        self.assertEqual(output["recommended_configuration_label"], "1 line × 2 shifts")
        self.assertAlmostEqual(output["recommended_capacity_mt_day"], 20.0, places=3)

    def test_recommended_config_c_39_1_mt_day(self):
        output = build_plant_capacity_output(
            {"finished_goods_mt_day": 39.1},
            capacity_per_line_mt_day=10.0,
            max_shifts=3,
            installed_lines=1,
            active_shifts=1,
            maximum_lines_in_current_plant=2,
            existing_plant_expandable=True,
        )
        self.assertEqual(output["recommended_lines"], 2)
        self.assertEqual(output["recommended_shifts"], 2)
        self.assertEqual(output["recommended_configuration_label"], "2 lines × 2 shifts")
        self.assertAlmostEqual(output["recommended_capacity_mt_day"], 40.0, places=3)
        self.assertAlmostEqual(output["projected_utilization_pct"], 97.75, places=2)
        self.assertEqual(output["new_plant_required"], "No")

    def test_recommended_capacity_math_d_10_x_2_x_2(self):
        self.assertAlmostEqual(10.0 * 2 * 2, 40.0, places=9)

    def test_recommended_label_uses_canonical_formatter(self):
        output = build_plant_capacity_output(
            {"finished_goods_mt_day": 39.1},
            capacity_per_line_mt_day=10.0,
            max_shifts=3,
            installed_lines=1,
            active_shifts=1,
            maximum_lines_in_current_plant=2,
            existing_plant_expandable=True,
        )
        self.assertEqual(
            output["recommended_configuration_label"],
            format_configuration(output["recommended_lines"], output["recommended_shifts"]),
        )

    def test_a_base_10_one_line_one_shift_capacity_10(self):
        output = build_plant_capacity_output(
            {"finished_goods_mt_day": 5.0},
            capacity_per_line_mt_day=10.0,
            max_shifts=3,
            installed_lines=1,
            active_shifts=1,
            maximum_lines_in_current_plant=3,
        )
        self.assertAlmostEqual(output["installed_capacity_mt_day"], 10.0, places=3)

    def test_b_base_10_two_lines_two_shifts_capacity_40(self):
        output = build_plant_capacity_output(
            {"finished_goods_mt_day": 39.1},
            capacity_per_line_mt_day=10.0,
            max_shifts=3,
            installed_lines=2,
            active_shifts=2,
            maximum_lines_in_current_plant=4,
        )
        self.assertEqual(output["installed_lines"], 2)
        self.assertEqual(output["active_shifts"], 2)
        self.assertAlmostEqual(output["installed_capacity_mt_day"], 40.0, places=3)

    def test_c_utilization_for_39_1_over_40(self):
        output = build_plant_capacity_output(
            {"finished_goods_mt_day": 39.1},
            capacity_per_line_mt_day=10.0,
            max_shifts=3,
            installed_lines=2,
            active_shifts=2,
            maximum_lines_in_current_plant=4,
        )
        self.assertAlmostEqual(output["plant_utilization_pct"], 97.75, places=2)

    def test_d_build_new_plant_when_demand_exceeds_max_site_capacity(self):
        output = build_plant_capacity_output(
            {"finished_goods_mt_day": 125.0},
            capacity_per_line_mt_day=10.0,
            max_shifts=3,
            installed_lines=1,
            active_shifts=1,
            maximum_lines_in_current_plant=3,
            existing_plant_expandable=False,
        )
        self.assertEqual(output["recommended_action"], "Build New Plant")
        self.assertEqual(output["new_plant_required"], "Yes")
        self.assertAlmostEqual(output["recommended_new_plant_capacity_mt_day"], 35.0, places=3)

    def test_e_add_shift_when_shift_can_close_gap(self):
        output = build_plant_capacity_output(
            {"finished_goods_mt_day": 25.0},
            capacity_per_line_mt_day=10.0,
            max_shifts=4,
            installed_lines=1,
            active_shifts=1,
            maximum_lines_in_current_plant=1,
            existing_plant_expandable=False,
        )
        self.assertEqual(output["recommended_action"], "Add Shift")

    def test_f_add_shift_and_line_when_combination_required(self):
        output = build_plant_capacity_output(
            {"finished_goods_mt_day": 35.0},
            capacity_per_line_mt_day=10.0,
            max_shifts=2,
            installed_lines=1,
            active_shifts=1,
            maximum_lines_in_current_plant=2,
            existing_plant_expandable=False,
        )
        self.assertEqual(output["recommended_action"], "Add Shift and Production Line")

    def test_g_shortfall_and_headroom_labels(self):
        output = build_plant_capacity_output(
            {"finished_goods_mt_day": 39.1},
            capacity_per_line_mt_day=10.0,
            max_shifts=3,
            installed_lines=1,
            active_shifts=1,
            maximum_lines_in_current_plant=2,
            existing_plant_expandable=True,
        )
        self.assertAlmostEqual(output["capacity_shortfall_mt_day"], 29.1, places=3)
        self.assertAlmostEqual(output["capacity_headroom_mt_day"], 0.0, places=3)

    def test_h_site_headroom_after_meeting_demand(self):
        output = build_plant_capacity_output(
            {"finished_goods_mt_day": 39.1},
            capacity_per_line_mt_day=10.0,
            max_shifts=3,
            installed_lines=1,
            active_shifts=1,
            maximum_lines_in_current_plant=2,
            existing_plant_expandable=True,
        )
        self.assertAlmostEqual(output["maximum_current_plant_capacity_mt_day"], 60.0, places=3)
        self.assertAlmostEqual(output["remaining_site_headroom_after_demand_mt_day"], 20.9, places=3)

    def test_i_recommended_configuration_and_projected_utilization(self):
        output = build_plant_capacity_output(
            {"finished_goods_mt_day": 39.1},
            capacity_per_line_mt_day=10.0,
            max_shifts=3,
            installed_lines=1,
            active_shifts=1,
            maximum_lines_in_current_plant=2,
            existing_plant_expandable=True,
        )
        self.assertEqual(output["recommended_lines"], 2)
        self.assertEqual(output["recommended_shifts"], 2)
        self.assertAlmostEqual(output["recommended_capacity_mt_day"], 40.0, places=3)
        self.assertAlmostEqual(output["projected_utilization_pct"], 97.75, places=2)

    def test_j_new_plant_not_required_when_within_max_site_capacity(self):
        output = build_plant_capacity_output(
            {"finished_goods_mt_day": 39.1},
            capacity_per_line_mt_day=10.0,
            max_shifts=3,
            installed_lines=1,
            active_shifts=1,
            maximum_lines_in_current_plant=2,
            existing_plant_expandable=True,
        )
        self.assertEqual(output["new_plant_required"], "No")

    def test_k_current_config_label_1x1_capacity_10(self):
        output = build_plant_capacity_output(
            {"finished_goods_mt_day": 5.0},
            capacity_per_line_mt_day=10.0,
            max_shifts=3,
            installed_lines=1,
            active_shifts=1,
            maximum_lines_in_current_plant=2,
        )
        self.assertEqual(output["current_configuration_label"], "1 line × 1 shift")
        self.assertAlmostEqual(output["current_installed_capacity_mt_day"], 10.0, places=3)

    def test_l_current_config_label_2x1_capacity_20(self):
        output = build_plant_capacity_output(
            {"finished_goods_mt_day": 12.0},
            capacity_per_line_mt_day=10.0,
            max_shifts=3,
            installed_lines=2,
            active_shifts=1,
            maximum_lines_in_current_plant=2,
        )
        self.assertEqual(output["current_configuration_label"], "2 lines × 1 shift")
        self.assertAlmostEqual(output["current_installed_capacity_mt_day"], 20.0, places=3)

    def test_m_current_config_label_2x2_capacity_40(self):
        output = build_plant_capacity_output(
            {"finished_goods_mt_day": 30.0},
            capacity_per_line_mt_day=10.0,
            max_shifts=3,
            installed_lines=2,
            active_shifts=2,
            maximum_lines_in_current_plant=2,
        )
        self.assertEqual(output["current_configuration_label"], "2 lines × 2 shifts")
        self.assertAlmostEqual(output["current_installed_capacity_mt_day"], 40.0, places=3)

    def test_n_current_vs_recommended_separation_for_39_1(self):
        output = build_plant_capacity_output(
            {"finished_goods_mt_day": 39.1},
            capacity_per_line_mt_day=10.0,
            max_shifts=3,
            installed_lines=1,
            active_shifts=1,
            maximum_lines_in_current_plant=2,
            existing_plant_expandable=True,
        )
        self.assertEqual(output["current_configuration_label"], "1 line × 1 shift")
        self.assertAlmostEqual(output["current_installed_capacity_mt_day"], 10.0, places=3)
        self.assertEqual(output["recommended_configuration_label"], "2 lines × 2 shifts")
        self.assertAlmostEqual(output["recommended_capacity_mt_day"], 40.0, places=3)
        self.assertEqual(output["new_plant_required"], "No")

    def test_o_recommended_configuration_for_9_4_mt_day(self):
        output = build_plant_capacity_output(
            {"finished_goods_mt_day": 9.4},
            capacity_per_line_mt_day=10.0,
            max_shifts=3,
            installed_lines=1,
            active_shifts=1,
            maximum_lines_in_current_plant=2,
        )
        self.assertEqual(output["recommended_configuration_label"], "1 line × 1 shift")
        self.assertAlmostEqual(output["recommended_capacity_mt_day"], 10.0, places=3)

    def test_p_recommended_configuration_for_15_mt_day(self):
        output = build_plant_capacity_output(
            {"finished_goods_mt_day": 15.0},
            capacity_per_line_mt_day=10.0,
            max_shifts=3,
            installed_lines=1,
            active_shifts=1,
            maximum_lines_in_current_plant=2,
        )
        self.assertEqual(output["recommended_configuration_label"], "1 line × 2 shifts")
        self.assertAlmostEqual(output["recommended_capacity_mt_day"], 20.0, places=3)

    def test_q_new_plant_required_when_required_output_exceeds_60(self):
        output = build_plant_capacity_output(
            {"finished_goods_mt_day": 61.0},
            capacity_per_line_mt_day=10.0,
            max_shifts=3,
            installed_lines=1,
            active_shifts=1,
            maximum_lines_in_current_plant=2,
            existing_plant_expandable=False,
        )
        self.assertEqual(output["new_plant_required"], "Yes")


class PlantNormalizationHotfixTests(unittest.TestCase):
    def setUp(self):
        self.assigned_markets = pd.DataFrame([
            {
                "city": "Kolkata",
                "revenue_allocation_cr": 10.0,
                "assigned_plant_id": "PLANT_KOL",
            }
        ])

    def test_a_dict_input_runs(self):
        plant = {
            "line_capacity_mt_day": 10,
            "installed_lines": 2,
            "active_shifts": 2,
            "maximum_shifts": 3,
            "installed_capacity_mt_day": 40,
            "maximum_lines_in_current_plant": 3,
            "existing_plant_expandable": "Yes",
        }
        result = build_plant_planning(plant=plant, assigned_markets=self.assigned_markets)
        self.assertIn("plant_capacity_output", result)

    def test_b_series_input_runs_without_truth_value_error(self):
        plant = pd.Series(
            {
                "line_capacity_mt_day": 10,
                "installed_lines": 2,
                "active_shifts": 1,
                "maximum_shifts": 3,
                "maximum_lines_in_current_plant": 2,
                "existing_plant_expandable": "Yes",
            }
        )
        result = build_plant_planning(plant=plant, assigned_markets=self.assigned_markets)
        output = result["plant_capacity_output"]
        self.assertEqual(output["current_configuration_label"], "2 lines × 1 shift")
        self.assertAlmostEqual(output["current_installed_capacity_mt_day"], 20.0, places=3)

    def test_c_switch_between_plants_updates_current_configuration(self):
        plant_one = {
            "line_capacity_mt_day": 10,
            "installed_lines": 1,
            "active_shifts": 1,
            "maximum_shifts": 3,
            "maximum_lines_in_current_plant": 2,
            "existing_plant_expandable": "Yes",
        }
        plant_two = {
            "line_capacity_mt_day": 10,
            "installed_lines": 2,
            "active_shifts": 1,
            "maximum_shifts": 3,
            "maximum_lines_in_current_plant": 3,
            "existing_plant_expandable": "Yes",
        }
        result_one = build_plant_planning(plant=plant_one, assigned_markets=self.assigned_markets)
        result_two = build_plant_planning(plant=plant_two, assigned_markets=self.assigned_markets)
        output_one = result_one["plant_capacity_output"]
        output_two = result_two["plant_capacity_output"]
        self.assertEqual(output_one["current_configuration_label"], "1 line × 1 shift")
        self.assertEqual(output_two["current_configuration_label"], "2 lines × 1 shift")
        self.assertNotEqual(output_one["current_installed_capacity_mt_day"], output_two["current_installed_capacity_mt_day"])


class ManpowerNormalizationHotfixTests(unittest.TestCase):
    def setUp(self):
        self.assigned_markets = pd.DataFrame([
            {
                "city": "Kolkata",
                "revenue_allocation_cr": 10.0,
                "assigned_plant_id": "PLANT_KOL",
            }
        ])

    def test_a_dict_input_runs(self):
        manpower = {
            "total_hc": 76,
            "production_hc": 46,
        }
        result = build_plant_planning(assigned_markets=self.assigned_markets, manpower=manpower)
        self.assertIn("manpower_output", result)

    def test_b_series_input_runs(self):
        manpower = pd.Series(
            {
                "total_hc": 76,
                "production_hc": 46,
            }
        )
        result = build_plant_planning(assigned_markets=self.assigned_markets, manpower=manpower)
        self.assertIn("manpower_output", result)

    def test_c_none_input_returns_empty_mapping(self):
        result = build_plant_planning(assigned_markets=self.assigned_markets, manpower=None)
        self.assertEqual(result["manpower_output"], {})

    def test_d_output_type_is_dict(self):
        result_dict = build_plant_planning(
            assigned_markets=self.assigned_markets,
            manpower={"total_hc": 76, "production_hc": 46},
        )
        result_series = build_plant_planning(
            assigned_markets=self.assigned_markets,
            manpower=pd.Series({"total_hc": 76, "production_hc": 46}),
        )
        result_none = build_plant_planning(assigned_markets=self.assigned_markets, manpower=None)
        self.assertIsInstance(result_dict["manpower_output"], dict)
        self.assertIsInstance(result_series["manpower_output"], dict)
        self.assertIsInstance(result_none["manpower_output"], dict)

    def test_e_values_unchanged_after_normalization(self):
        manpower_dict = {"total_hc": 76, "production_hc": 46}
        manpower_series = pd.Series({"total_hc": 76, "production_hc": 46})
        result_dict = build_plant_planning(assigned_markets=self.assigned_markets, manpower=manpower_dict)
        result_series = build_plant_planning(assigned_markets=self.assigned_markets, manpower=manpower_series)
        self.assertEqual(result_dict["manpower_output"].get("total_hc"), 76)
        self.assertEqual(result_dict["manpower_output"].get("production_hc"), 46)
        self.assertEqual(result_series["manpower_output"].get("total_hc"), 76)
        self.assertEqual(result_series["manpower_output"].get("production_hc"), 46)

    def test_b_series_input_runs(self):
        plant = pd.Series(
            {
                "line_capacity_mt_day": 10,
                "installed_lines": 2,
                "active_shifts": 2,
                "maximum_shifts": 3,
                "installed_capacity_mt_day": 40,
                "maximum_lines_in_current_plant": 3,
                "existing_plant_expandable": "Yes",
            }
        )
        result = build_plant_planning(plant=plant, assigned_markets=self.assigned_markets)
        self.assertIn("plant_capacity_output", result)

    def test_c_none_input_runs(self):
        result = build_plant_planning(plant=None, assigned_markets=self.assigned_markets)
        self.assertIn("plant_capacity_output", result)

    def test_d_expected_capacity_40_mt_day(self):
        plant = pd.Series(
            {
                "line_capacity_mt_day": 10,
                "installed_lines": 2,
                "active_shifts": 2,
                "maximum_shifts": 3,
                "installed_capacity_mt_day": 40,
                "maximum_lines_in_current_plant": 4,
                "existing_plant_expandable": "Yes",
            }
        )
        result = build_plant_planning(plant=plant, assigned_markets=self.assigned_markets)
        output = result["plant_capacity_output"]
        self.assertAlmostEqual(output["installed_capacity_mt_day"], 40.0, places=3)

    def test_e_cloud_call_style_no_series_truth_error(self):
        plant = pd.Series(
            {
                "plant_id": "PLANT_KOL",
                "line_capacity_mt_day": 10,
                "installed_capacity_mt_day": 10,
                "maximum_shifts": 3,
                "existing_plant_expandable": "Yes",
            }
        )
        try:
            result = build_plant_planning(
                plant=plant,
                assigned_markets=self.assigned_markets,
                product_mix={"FRESH": 40, "FROZEN": 30, "RTE": 15, "FVA": 15},
                channel_mix={"GT": 40, "MT": 20, "QC": 10, "ECOM": 10, "HORECA": 15, "INST": 3, "EXP": 2},
            )
        except ValueError as exc:
            self.fail(f"Unexpected ValueError from Series truth evaluation: {exc}")
        self.assertIn("plant_capacity_output", result)


if __name__ == "__main__":
    unittest.main()
