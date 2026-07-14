import unittest

import pandas as pd

from calculation_engine import build_plant_capacity_output, build_plant_planning


class CapacityGovernanceTests(unittest.TestCase):
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

    def test_e_add_shift_when_shift_headroom_exists(self):
        output = build_plant_capacity_output(
            {"finished_goods_mt_day": 39.1},
            capacity_per_line_mt_day=10.0,
            max_shifts=3,
            installed_lines=2,
            active_shifts=2,
            maximum_lines_in_current_plant=2,
            existing_plant_expandable=False,
        )
        self.assertEqual(output["recommended_action"], "Add Shift")

    def test_f_add_line_when_no_shift_headroom_and_line_space_exists(self):
        output = build_plant_capacity_output(
            {"finished_goods_mt_day": 39.1},
            capacity_per_line_mt_day=10.0,
            max_shifts=2,
            installed_lines=2,
            active_shifts=2,
            maximum_lines_in_current_plant=3,
            existing_plant_expandable=False,
        )
        self.assertEqual(output["recommended_action"], "Add Production Line")


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
