import unittest

from calculation_engine import align_manpower_sales, build_channel_sales_output


class SalesManpowerGovernanceTests(unittest.TestCase):
    def _base_kwargs(self):
        return {
            "channel_mix": {
                "gt": 0.40,
                "mt": 0.20,
                "qcom": 0.10,
                "ecommerce": 0.10,
                "horeca": 0.10,
                "institution": 0.07,
                "exports": 0.03,
            },
            "gt_target_outlets": 400,
            "gt_distributors": 8,
            "gt_outlets_per_sales_executive": 50,
            "mt_active_accounts": 8,
            "mt_accounts_per_kam": 4,
            "qcom_buying_accounts": 3,
            "qcom_buying_regions": 2,
            "qcom_accounts_per_kam": 3,
            "horeca_active_accounts": 10,
            "horeca_accounts_per_manager": 4,
            "institutional_active_tenders": 4,
            "institutional_tenders_per_manager": 4,
            "ecommerce_active_accounts": 0,
            "ecommerce_accounts_per_manager": 4,
            "exports_active_markets": 0,
            "exports_active_buyers": 0,
            "sales_productivity_factor": 1.0,
            "digital_enablement_factor": 1.0,
            "distributor_self_service_factor": 1.0,
            "sales_automation_factor": 1.0,
        }

    def test_a_revenue_increase_without_workload_increase(self):
        base = self._base_kwargs()
        out_6 = build_channel_sales_output(market_revenue=60000000.0, **base)
        out_12 = build_channel_sales_output(market_revenue=120000000.0, **base)

        self.assertEqual(out_6["gt_sales_executives"], out_12["gt_sales_executives"])
        self.assertEqual(out_6["mt_kam"], out_12["mt_kam"])
        self.assertEqual(out_6["qcom_kam"], out_12["qcom_kam"])

    def test_b_outlet_increase_changes_gt_hc(self):
        base = self._base_kwargs()
        out_400 = build_channel_sales_output(market_revenue=10000000.0, **base)
        out_600 = build_channel_sales_output(market_revenue=10000000.0, **{**base, "gt_target_outlets": 600})

        self.assertEqual(out_400["gt_sales_executives"], 8)
        self.assertEqual(out_600["gt_sales_executives"], 12)

    def test_c_mt_revenue_increase_accounts_unchanged(self):
        base = self._base_kwargs()
        out_6 = build_channel_sales_output(market_revenue=60000000.0, **base)
        out_25 = build_channel_sales_output(market_revenue=250000000.0, **base)

        self.assertEqual(out_6["modern_trade"]["accounts"], 8)
        self.assertEqual(out_25["modern_trade"]["accounts"], 8)
        self.assertEqual(out_6["mt_kam"], out_25["mt_kam"])

    def test_d_productivity_improvement_reduces_gt_hc(self):
        base = self._base_kwargs()
        out_base = build_channel_sales_output(market_revenue=10000000.0, **base)
        out_productive = build_channel_sales_output(
            market_revenue=10000000.0,
            **{**base, "sales_productivity_factor": 1.2},
        )

        self.assertLess(out_productive["gt_sales_executives"], out_base["gt_sales_executives"])

    def test_e_total_commercial_hc_reconciles(self):
        out = build_channel_sales_output(market_revenue=60000000.0, **self._base_kwargs())
        role_sum = (
            int(out.get("head_sales_hc", 0) or 0)
            + int(out.get("general_trade_hc", 0) or 0)
            + int(out.get("modern_trade_hc", 0) or 0)
            + int(out.get("quick_commerce_hc", 0) or 0)
            + int(out.get("ecommerce_hc", 0) or 0)
            + int(out.get("horeca_hc", 0) or 0)
            + int(out.get("institutional_hc", 0) or 0)
            + int(out.get("exports_hc", 0) or 0)
            + int(out.get("sales_coordinator_mis", 0) or 0)
            + int(out.get("channel_leadership_hc", 0) or 0)
        )
        self.assertEqual(role_sum, int(out.get("total_commercial_hc", 0) or 0))
        self.assertTrue(out.get("commercial_hc_reconciled", False))

    def test_f_inactive_channels_have_zero_hc(self):
        out = build_channel_sales_output(
            market_revenue=60000000.0,
            **self._base_kwargs(),
        )
        self.assertEqual(int(out.get("ecommerce_hc", 0) or 0), 0)
        self.assertEqual(int(out.get("exports_hc", 0) or 0), 0)

    def test_g_revenue_change_does_not_change_operational_sales_workload(self):
        base = self._base_kwargs()
        out_4 = build_channel_sales_output(market_revenue=40000000.0, **base)
        out_7 = build_channel_sales_output(market_revenue=70000000.0, **base)

        self.assertEqual(out_4["gt_sales_executives"], out_7["gt_sales_executives"])
        self.assertEqual(out_4["mt_kam"], out_7["mt_kam"])
        self.assertEqual(out_4["qcom_kam"], out_7["qcom_kam"])
        self.assertEqual(out_4["total_sales_hc"], out_7["total_sales_hc"])

        aligned_4 = align_manpower_sales({"sales": 0, "staffing_bands": {"sales": {}}}, out_4)
        aligned_7 = align_manpower_sales({"sales": 0, "staffing_bands": {"sales": {}}}, out_7)

        band_4 = aligned_4["staffing_bands"]["sales"]
        band_7 = aligned_7["staffing_bands"]["sales"]

        self.assertEqual(band_4["current_workload"], band_7["current_workload"])
        self.assertEqual(band_4["current_workload_numeric"], band_7["current_workload_numeric"])
        self.assertEqual(band_4["recommended_hc"], band_7["recommended_hc"])
        self.assertEqual(band_4["current_workload_display"], band_7["current_workload_display"])
        self.assertEqual(band_4["workload_unit"], "coverage workload")
        self.assertEqual(band_4["current_staffing_band"], "role productivity capacity")
        self.assertEqual(band_4["lower_threshold_display"], "Role-specific")
        self.assertEqual(band_4["upper_threshold_display"], "Role-specific")
        self.assertIn("400 outlets", band_4["current_workload_display"])
        self.assertIn("8 distributors", band_4["current_workload_display"])
        self.assertIn("8 MT accounts", band_4["current_workload_display"])
        self.assertIn("3 QCom accounts", band_4["current_workload_display"])
        self.assertIn("10 HoReCa accounts", band_4["current_workload_display"])
        self.assertIn("4 institutional tenders", band_4["current_workload_display"])
        self.assertNotIn("40,000,000", band_4["current_workload_display"])
        self.assertNotIn("70,000,000", band_4["current_workload_display"])

    def test_h_default_operational_workload_stays_stable_when_revenue_changes(self):
        base = {
            "channel_mix": {
                "gt": 0.40,
                "mt": 0.20,
                "qcom": 0.10,
                "ecommerce": 0.10,
                "horeca": 0.10,
                "institution": 0.07,
                "exports": 0.03,
            },
            "horeca_active_accounts": 10,
            "sales_productivity_factor": 1.0,
            "digital_enablement_factor": 1.0,
            "distributor_self_service_factor": 1.0,
            "sales_automation_factor": 1.0,
        }
        out_4 = build_channel_sales_output(market_revenue=40000000.0, **base)
        out_7 = build_channel_sales_output(market_revenue=70000000.0, **base)

        self.assertEqual(out_4["general_trade"]["target_outlets"], out_7["general_trade"]["target_outlets"])
        self.assertEqual(out_4["general_trade"]["active_distributors"], out_7["general_trade"]["active_distributors"])
        self.assertEqual(out_4["modern_trade"]["accounts"], out_7["modern_trade"]["accounts"])
        self.assertEqual(out_4["quick_commerce"]["buying_accounts"], out_7["quick_commerce"]["buying_accounts"])
        self.assertEqual(out_4["sales_operational_workload_display"], out_7["sales_operational_workload_display"])
        self.assertEqual(out_4["total_sales_hc"], out_7["total_sales_hc"])


if __name__ == "__main__":
    unittest.main()
