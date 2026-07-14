import pathlib
import unittest

from calculation_engine import align_manpower_sales, build_channel_sales_output


class SalesManpowerGovernanceTests(unittest.TestCase):
    def _base_channel_mix(self):
        return {
            "gt": 0.40,
            "mt": 0.20,
            "qcom": 0.10,
            "ecommerce": 0.10,
            "horeca": 0.10,
            "institution": 0.07,
            "exports": 0.03,
        }

    def _explicit_workload_kwargs(self):
        return {
            "channel_mix": self._base_channel_mix(),
            "gt_target_outlets": 180,
            "gt_distributors": 4,
            "gt_outlets_per_sales_executive": 50,
            "mt_active_accounts": 3,
            "mt_accounts_per_kam": 4,
            "qcom_buying_accounts": 2,
            "qcom_buying_regions": 1,
            "qcom_accounts_per_kam": 3,
            "horeca_active_accounts": 5,
            "horeca_accounts_per_manager": 4,
            "institutional_active_tenders": 1,
            "institutional_tenders_per_manager": 4,
            "ecommerce_active_accounts": 1,
            "exports_active_markets": 0,
            "exports_active_buyers": 0,
            "exports_buyers_per_manager": 3,
            "sales_productivity_factor": 1.0,
            "digital_enablement_factor": 1.0,
            "distributor_self_service_factor": 1.0,
            "sales_automation_factor": 1.0,
        }

    def _aligned_sales_band(self, output):
        aligned = align_manpower_sales({"sales": 0, "staffing_bands": {"sales": {}}}, output)
        return aligned["staffing_bands"]["sales"]

    def test_a_revenue_4_to_7_not_linear_and_not_revenue_workload(self):
        out_4 = build_channel_sales_output(market_revenue=40000000.0, **self._explicit_workload_kwargs())
        out_7 = build_channel_sales_output(market_revenue=70000000.0, **self._explicit_workload_kwargs())

        band_4 = self._aligned_sales_band(out_4)
        band_7 = self._aligned_sales_band(out_7)

        self.assertEqual(band_4["current_workload_display"], band_7["current_workload_display"])
        self.assertEqual(band_4["recommended_hc"], band_7["recommended_hc"])
        self.assertNotIn("40,000,000", band_4["current_workload_display"])
        self.assertNotIn("70,000,000", band_7["current_workload_display"])
        self.assertEqual(band_4["workload_unit"], "coverage workload")
        self.assertEqual(band_4["current_staffing_band"], "role productivity capacity")

    def test_b_revenue_4_to_15_increases_operational_workload_and_hc(self):
        base = {
            "channel_mix": self._base_channel_mix(),
            "sales_productivity_factor": 1.0,
            "digital_enablement_factor": 1.0,
            "distributor_self_service_factor": 1.0,
            "sales_automation_factor": 1.0,
        }
        out_4 = build_channel_sales_output(market_revenue=40000000.0, **base)
        out_15 = build_channel_sales_output(market_revenue=150000000.0, **base)

        self.assertGreater(out_15["sales_operational_workload_score"], out_4["sales_operational_workload_score"])
        self.assertGreater(out_15["sales_recommended_hc"], out_4["sales_recommended_hc"])

    def test_c_explicit_workload_inputs_override_revenue_derivation(self):
        kwargs = self._explicit_workload_kwargs()
        out_4 = build_channel_sales_output(market_revenue=40000000.0, **kwargs)
        out_15 = build_channel_sales_output(market_revenue=150000000.0, **kwargs)

        self.assertEqual(out_4["sales_workload"], out_15["sales_workload"])
        self.assertEqual(out_4["sales_operational_workload_display"], out_15["sales_operational_workload_display"])
        self.assertEqual(out_4["sales_recommended_hc"], out_15["sales_recommended_hc"])

    def test_d_gt_outlets_increase_raises_gt_hc(self):
        base = self._explicit_workload_kwargs()
        out_400 = build_channel_sales_output(market_revenue=10000000.0, **base)
        out_600 = build_channel_sales_output(market_revenue=10000000.0, **{**base, "gt_target_outlets": 600})

        self.assertGreater(out_600["gt_sales_executives"], out_400["gt_sales_executives"])

    def test_e_mt_accounts_threshold_crossing_changes_mt_hc(self):
        base = self._explicit_workload_kwargs()
        out_8 = build_channel_sales_output(market_revenue=10000000.0, **base)
        out_12 = build_channel_sales_output(market_revenue=10000000.0, **{**base, "mt_active_accounts": 12})

        self.assertLessEqual(out_8["mt_kam"], 1)
        self.assertGreaterEqual(out_12["mt_kam"], out_8["mt_kam"])

    def test_f_total_commercial_hc_reconciles(self):
        out = build_channel_sales_output(market_revenue=60000000.0, **self._explicit_workload_kwargs())
        role_sum = (
            int(out.get("head_sales_hc", 0) or 0)
            + int(out.get("general_trade_hc", 0) or 0)
            + int(out.get("shared_digital_kam_hc", 0) or 0)
            + int(out.get("modern_trade_hc", 0) or 0)
            + int(out.get("quick_commerce_hc", 0) or 0)
            + int(out.get("ecommerce_hc", 0) or 0)
            + int(out.get("shared_b2b_manager_hc", 0) or 0)
            + int(out.get("horeca_hc", 0) or 0)
            + int(out.get("institutional_hc", 0) or 0)
            + int(out.get("exports_hc", 0) or 0)
            + int(out.get("sales_coordinator_mis", 0) or 0)
            + int(out.get("gt_distributor_managers", 0) or 0)
            + int(out.get("channel_leadership_hc", 0) or 0)
        )
        self.assertEqual(role_sum, int(out.get("total_commercial_hc", 0) or 0))
        self.assertEqual(out.get("sales_reconciliation_status"), "Reconciled")

    def test_g_visible_row_scenarios_2_3_15_follow_coverage_and_steps(self):
        base = {
            "channel_mix": self._base_channel_mix(),
            "sales_productivity_factor": 1.0,
            "digital_enablement_factor": 1.0,
            "distributor_self_service_factor": 1.0,
            "sales_automation_factor": 1.0,
        }
        out_2 = build_channel_sales_output(market_revenue=20000000.0, **base)
        out_3 = build_channel_sales_output(market_revenue=30000000.0, **base)
        out_15 = build_channel_sales_output(market_revenue=150000000.0, **base)

        band_2 = self._aligned_sales_band(out_2)
        band_3 = self._aligned_sales_band(out_3)
        band_15 = self._aligned_sales_band(out_15)

        self.assertNotIn("20,000,000", band_2["current_workload_display"])
        self.assertNotIn("30,000,000", band_3["current_workload_display"])
        self.assertEqual("coverage workload", band_2["workload_unit"])
        self.assertGreater(out_15["sales_operational_workload_score"], out_2["sales_operational_workload_score"])
        self.assertGreater(band_15["recommended_hc"], band_2["recommended_hc"])
        self.assertNotEqual(band_2["recommended_hc"], band_3["recommended_hc"] * (2 / 3))

    def test_h_aligned_top_level_sales_fields_match_staffing_band(self):
        out = build_channel_sales_output(market_revenue=20000000.0, **self._explicit_workload_kwargs())
        aligned = align_manpower_sales({"sales": 0, "staffing_bands": {"sales": {}}}, out)
        band = aligned["staffing_bands"]["sales"]

        self.assertEqual(aligned["sales_operational_workload_display"], band["current_workload_display"])
        self.assertEqual(aligned["sales_recommended_hc"], band["recommended_hc"])
        self.assertEqual(aligned["sales_current_hc"], band["current_hc"])
        self.assertEqual(aligned["sales_threshold_status"], band["threshold_status"])

    def test_i_no_page_level_sales_row_override(self):
        page_file = pathlib.Path(__file__).resolve().parents[1] / "pages" / "Business_Requirement_Planning.py"
        content = page_file.read_text(encoding="utf-8").lower()
        self.assertNotIn('if function_name == "sales"', content)

    def test_j_startup_1cr_uses_shared_roles_and_is_below_19(self):
        out = build_channel_sales_output(market_revenue=10000000.0, **self._explicit_workload_kwargs())

        self.assertGreaterEqual(int(out.get("shared_digital_kam_hc", 0) or 0), 1)
        self.assertGreaterEqual(int(out.get("shared_b2b_manager_hc", 0) or 0), 1)
        self.assertEqual(int(out.get("exports_hc", 0) or 0), 0)
        self.assertEqual(int(out.get("mt_kam", 0) or 0), 0)
        self.assertEqual(int(out.get("qcom_kam", 0) or 0), 0)
        self.assertEqual(int(out.get("ecommerce_hc", 0) or 0), 0)
        self.assertEqual(int(out.get("horeca_hc", 0) or 0), 0)
        self.assertEqual(int(out.get("institutional_hc", 0) or 0), 0)
        self.assertLess(int(out.get("total_commercial_hc", 0) or 0), 19)

    def test_k_revenue_steps_1cr_4cr_10cr_non_linear(self):
        base = {
            "channel_mix": self._base_channel_mix(),
            "sales_productivity_factor": 1.0,
            "digital_enablement_factor": 1.0,
            "distributor_self_service_factor": 1.0,
            "sales_automation_factor": 1.0,
        }
        out_1 = build_channel_sales_output(market_revenue=10000000.0, **base)
        out_4 = build_channel_sales_output(market_revenue=40000000.0, **base)
        out_10 = build_channel_sales_output(market_revenue=100000000.0, **base)

        self.assertGreaterEqual(int(out_4.get("total_commercial_hc", 0) or 0), int(out_1.get("total_commercial_hc", 0) or 0))
        self.assertGreaterEqual(int(out_10.get("total_commercial_hc", 0) or 0), int(out_4.get("total_commercial_hc", 0) or 0))
        self.assertTrue(
            int(out_4.get("total_commercial_hc", 0) or 0) > int(out_1.get("total_commercial_hc", 0) or 0)
            or int(out_10.get("total_commercial_hc", 0) or 0) > int(out_4.get("total_commercial_hc", 0) or 0)
        )

    def test_l_low_revenue_high_workload_increases_hc(self):
        base = self._explicit_workload_kwargs()
        startup = build_channel_sales_output(market_revenue=10000000.0, **base)
        heavy_coverage = build_channel_sales_output(
            market_revenue=10000000.0,
            **{
                **base,
                "gt_target_outlets": 700,
                "gt_distributors": 10,
                "mt_active_accounts": 12,
                "qcom_buying_accounts": 8,
                "qcom_buying_regions": 4,
                "horeca_active_accounts": 18,
                "institutional_active_tenders": 4,
            },
        )

        self.assertGreater(int(heavy_coverage.get("total_commercial_hc", 0) or 0), int(startup.get("total_commercial_hc", 0) or 0))

    def test_m_high_revenue_same_workload_keeps_hc_flat(self):
        base = self._explicit_workload_kwargs()
        out_1 = build_channel_sales_output(market_revenue=10000000.0, **base)
        out_10 = build_channel_sales_output(market_revenue=100000000.0, **base)

        self.assertEqual(int(out_1.get("sales_workload_driver_total", 0) or 0), int(out_10.get("sales_workload_driver_total", 0) or 0))
        self.assertEqual(int(out_1.get("total_commercial_hc", 0) or 0), int(out_10.get("total_commercial_hc", 0) or 0))


if __name__ == "__main__":
    unittest.main()
