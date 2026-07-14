import unittest

from calculation_engine import build_plant_capacity_output


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


if __name__ == "__main__":
    unittest.main()
