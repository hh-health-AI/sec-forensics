import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import forensic_ratios as ratios


def row(start, end, val, filed="2026-02-01", **extra):
    return dict(start=start, end=end, val=val, filed=filed, form="10-K", accn=filed, **extra)


def facts(**tags):
    return {"facts": {"us-gaap": {k: {"units": {"USD": v}} for k, v in tags.items()}}}


class PeriodTests(unittest.TestCase):
    def test_quarter_and_ytd_do_not_collide(self):
        data = facts(Revenues=[row("2025-01-01", "2025-06-30", 200),
                               row("2025-04-01", "2025-06-30", 100)])
        self.assertEqual(len(ratios.series(data, ["Revenues"])), 2)

    def test_single_annual_observation_and_zero_balance(self):
        for balance, expected in [(10, 36.5), (0, 0)]:
            data = facts(Revenues=[row("2025-01-01", "2025-12-31", 100)],
                         AccountsReceivableNetCurrent=[row(None, "2025-12-31", balance)])
            self.assertEqual(ratios.analyse(data)["panel"]["dso_days_latest"], expected)

    def test_latest_filing_and_point_in_time(self):
        data = facts(Revenues=[row("2025-01-01", "2025-12-31", 100, "2026-02-01"),
                               row("2025-01-01", "2025-12-31", 120, "2026-03-01")])
        self.assertEqual(ratios.series(data, ["Revenues"])[0]["val"], 120)
        self.assertEqual(ratios.series(data, ["Revenues"], as_of="2026-02-15")[0]["val"], 100)

    def test_ytd_subtraction_and_contiguous_ttm(self):
        rs = [row("2025-01-01", end, val) for end, val in
              [("2025-03-31", 10), ("2025-06-30", 30),
               ("2025-09-30", 60), ("2025-12-31", 100)]]
        rs.append(row("2026-01-01", "2026-03-31", 25, "2026-05-01"))
        selected = ratios.series(facts(Revenues=rs), ["Revenues"])
        self.assertEqual(ratios.ttm(selected)["2026-03-31"]["val"], 115)

    def test_missing_quarter_does_not_create_ttm(self):
        rs = [row(start, end, 10) for start, end in
              [("2025-01-01", "2025-03-31"), ("2025-07-01", "2025-09-30"),
               ("2025-10-01", "2025-12-31"), ("2026-01-01", "2026-03-31")]]
        self.assertEqual(ratios.ttm(ratios.series(facts(Revenues=rs), ["Revenues"])), {})

    def test_partial_flow_and_mismatched_balance_are_null(self):
        for start, end in [("2025-10-01", "2025-12-31"), ("2024-01-01", "2024-12-31")]:
            data = facts(Revenues=[row(start, end, 100)],
                         AccountsReceivableNetCurrent=[row(None, "2025-12-31", 10)])
            self.assertIsNone(ratios.analyse(data)["panel"]["dso_days_latest"])

    def test_growth_is_fraction_not_multiple(self):
        data = facts(Revenues=[row("2024-01-01", "2024-12-31", 100),
                               row("2025-01-01", "2025-12-31", 120)])
        self.assertEqual(ratios.analyse(data)["panel"]["revenue_growth_yoy"], 0.2)

    def test_loss_making_company_has_no_cash_conversion_ratio(self):
        data = facts(NetIncomeLoss=[row("2025-01-01", "2025-12-31", -10)],
                     NetCashProvidedByUsedInOperatingActivities=[row("2025-01-01", "2025-12-31", 10)])
        self.assertIsNone(ratios.analyse(data)["panel"]["cfo_to_net_income_ttm"])

    def test_empty_input_fails(self):
        with self.assertRaises(ValueError):
            ratios.analyse({})


if __name__ == "__main__":
    unittest.main()
