import math

import pandas as pd


_UNSET = object()


def load_registry(path):
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def _to_float(value, default=0.0):
    try:
        if value is None or pd.isna(value):
            return default
        if isinstance(value, str):
            value = value.replace(",", "").replace("%", "").replace("₹", "").strip()
            if value == "":
                return default
        return float(value)
    except Exception:
        return default


def _normalize_mapping(value):
    if value is None:
        return {}
    if isinstance(value, pd.Series):
        return value.to_dict()
    if isinstance(value, dict):
        return value
    if hasattr(value, "to_dict"):
        converted = value.to_dict()
        return converted if isinstance(converted, dict) else {}
    return {}


def _coerce_percent(value):
    value = _to_float(value, 0.0)
    return value / 100.0 if value > 1 else value


def _value_from_cost_registry(cost_registry, cost_key, default):
    if cost_registry is None or getattr(cost_registry, "empty", True):
        return default
    for key_col in ("cost_key", "key", "name", "driver"):
        if key_col in cost_registry.columns:
            rows = cost_registry[cost_registry[key_col].astype(str) == str(cost_key)]
            if not rows.empty:
                for value_col in ("value", "cost", "amount", "rate"):
                    if value_col in rows.columns:
                        return _to_float(rows.iloc[0].get(value_col), default)
    return default


def _clamp(value, lower, upper):
    return max(lower, min(upper, value))


def _live_bird_rate(value):
    return _clamp(_to_float(value, 120.0), 104.0, 180.0)


def _nonnegative(value, default=0.0):
    return max(0.0, _to_float(value, default))


def _procurement_driver_value(procurement_drivers, key, fallback):
    if isinstance(procurement_drivers, dict) and key in procurement_drivers:
        return procurement_drivers.get(key)
    return fallback


def _procurement_route_shares(operating_model=None):
    model = str(operating_model or "").strip().lower()
    if "fully" in model:
        return 0.20, 0.80, "Fully Integrated procurement assumption: 20% trader sourced and 80% direct or contract farm sourced."
    if "partial" in model:
        return 0.60, 0.40, "Partial Integration procurement assumption: 60% trader sourced and 40% direct or contract farm sourced."
    return 0.70, 0.30, "Asset Light procurement assumption: 70% trader sourced and 30% direct or contract farm sourced."


def build_procurement_cost_waterfall(
    live_bird_rate_per_kg=120.0,
    yield_pct=72.0,
    mortality_pct=2.0,
    processing_loss_pct=3.0,
    gt_distributor_margin_pct=None,
    packaging_cost_per_kg=18.0,
    transport_cost_per_kg=12.0,
    processing_cost_per_kg=12.0,
    factory_overhead_per_kg=5.0,
    target_margin_pct=18.0,
    operating_model=None,
    # Deprecated compatibility parameters: accepted but ignored for procurement costing.
    trader_margin_pct=None,
    farm_margin_pct=None,
):
    rate = _nonnegative(live_bird_rate_per_kg, 120.0)
    dressed_yield_pct = _to_float(yield_pct, 72.0)
    mortality_pct = _to_float(mortality_pct, 2.0)
    processing_loss_pct = _to_float(processing_loss_pct, 3.0)
    if not (0 < dressed_yield_pct <= 100):
        raise ValueError("Yield % must be greater than 0 and less than or equal to 100.")
    if not (0 <= mortality_pct < 100):
        raise ValueError("Mortality % must be greater than or equal to 0 and less than 100.")
    if not (0 <= processing_loss_pct < 100):
        raise ValueError("Processing Loss % must be greater than or equal to 0 and less than 100.")
    if gt_distributor_margin_pct is None:
        gt_distributor_margin_pct = trader_margin_pct
    gt_distributor_margin_pct = _nonnegative(gt_distributor_margin_pct, 6.0)
    packaging_cost_per_kg = _nonnegative(packaging_cost_per_kg, 18.0)
    transport_cost_per_kg = _nonnegative(transport_cost_per_kg, 12.0)
    processing_cost_per_kg = _nonnegative(processing_cost_per_kg, 12.0)
    factory_overhead_per_kg = _nonnegative(factory_overhead_per_kg, 5.0)
    target_margin_pct = _nonnegative(target_margin_pct, 18.0)

    _, _, sourcing_assumption = _procurement_route_shares(operating_model)
    dressed_yield_rate = dressed_yield_pct / 100.0
    processing_retention_rate = 1.0 - processing_loss_pct / 100.0
    survival_rate = 1.0 - mortality_pct / 100.0
    effective_yield_rate = dressed_yield_rate * processing_retention_rate
    # Live bird rate is the final all-inclusive lifting rate and must be used directly.
    raw_material_cost_per_finished_kg = rate / max(0.0001, effective_yield_rate * survival_rate)
    total_ex_factory_cost_per_kg = raw_material_cost_per_finished_kg + processing_cost_per_kg + packaging_cost_per_kg + factory_overhead_per_kg
    total_delivered_cost_per_kg = total_ex_factory_cost_per_kg + transport_cost_per_kg
    margin_denominator = max(0.01, 1.0 - target_margin_pct / 100.0)
    return {
        "live_bird_base_rate_per_kg": rate,
        "live_bird_rate_per_kg": rate,
        "sourcing_assumption": sourcing_assumption,
        "gt_distributor_margin_pct": gt_distributor_margin_pct,
        "dressed_yield_pct": dressed_yield_pct,
        "processing_loss_pct": processing_loss_pct,
        "processing_retention_pct": processing_retention_rate * 100.0,
        "effective_finished_goods_yield_pct": effective_yield_rate * 100.0,
        "mortality_pct": mortality_pct,
        "survival_rate_pct": survival_rate * 100.0,
        "raw_material_cost_per_finished_kg": raw_material_cost_per_finished_kg,
        "processing_cost_per_kg": processing_cost_per_kg,
        "packaging_cost_per_kg": packaging_cost_per_kg,
        "transport_cost_per_kg": transport_cost_per_kg,
        "factory_overhead_per_kg": factory_overhead_per_kg,
        "total_ex_factory_cost_per_kg": total_ex_factory_cost_per_kg,
        "total_delivered_cost_per_kg": total_delivered_cost_per_kg,
        "target_margin_pct": target_margin_pct,
        "recommended_ex_factory_price_per_kg": total_ex_factory_cost_per_kg / margin_denominator,
        "recommended_delivered_price_per_kg": total_delivered_cost_per_kg / margin_denominator,
    }


PROCUREMENT_DRIVER_IMPACT_MAP = {
    "Live Bird Rate": ["Raw Material Cost/kg", "Live Bird Procurement Spend", "Total Cost/kg", "Gross Contribution", "EBITDA", "PAT", "Recommended Selling Price"],
    "Yield %": ["Effective Finished-Goods Yield", "Live Weight Required", "Birds/day", "Procurement Spend", "Gross Contribution"],
    "Mortality %": ["Gross Birds Required", "Live Weight Required", "Procurement Spend", "Farms Required", "Gross Contribution"],
    "Processing Loss %": ["Effective Finished-Goods Yield", "Raw Material Cost/kg", "Birds/day", "Procurement Spend", "Gross Contribution"],
    "GT Distributor Margin %": ["GT Company Net Realization", "GT Contribution", "Consolidated Gross Contribution", "EBITDA", "PAT"],
    "Packaging Cost": ["Packaging Spend", "Total Cost/kg", "Gross Contribution", "EBITDA", "PAT", "Recommended Selling Price"],
    "Transport Cost": ["Transport Spend", "Delivered Cost/kg", "Gross Contribution", "EBITDA", "PAT", "Recommended Selling Price"],
}


def _mix_value(mix, key, default=0.0):
    aliases = {
        "gt": "GT",
        "mt": "MT",
        "qcom": "QC",
        "ecommerce": "ECOM",
        "horeca": "HORECA",
        "institution": "INST",
        "exports": "EXP",
        "fresh": "FRESH",
        "frozen": "FROZEN",
        "rte": "RTE",
        "fva": "FVA",
    }
    if isinstance(mix, dict):
        candidates = [key, str(key).upper(), str(key).lower(), aliases.get(str(key).lower(), key)]
        for candidate in candidates:
            if candidate in mix:
                return _to_float(mix.get(candidate, default), default)
        return default
    if mix is not None and hasattr(mix, "get"):
        try:
            return _to_float(mix.get(key, default), default)
        except Exception:
            return default
    return default


def _mix_share(mix, key, default=0.0):
    value = _mix_value(mix, key, default)
    return value / 100.0 if value > 1 else value


def _price_lookup(pricing_registry, product_id, channel_id, default_price):
    if pricing_registry is not None and not getattr(pricing_registry, "empty", True):
        cols = pricing_registry.columns
        if {"product_id", "channel_id", "selling_price_per_kg"}.issubset(set(cols)):
            rows = pricing_registry[
                (pricing_registry["product_id"].astype(str).str.upper() == str(product_id).upper())
                & (pricing_registry["channel_id"].astype(str).str.upper() == str(channel_id).upper())
            ]
            if not rows.empty:
                return max(1.0, _to_float(rows.iloc[0].get("selling_price_per_kg"), default_price))
    return max(1.0, _to_float(default_price, 240.0))


def _product_registry_defaults(product_registry):
    defaults = {}
    if product_registry is not None and not getattr(product_registry, "empty", True):
        for _, row in product_registry.iterrows():
            product_id = str(row.get("product_id", "")).upper()
            if product_id:
                defaults[product_id] = {
                    "price": _to_float(row.get("selling_price_per_kg"), 240.0),
                    "yield_pct": _to_float(row.get("bird_yield_percent"), 72.0),
                }
    for product_id, price, yield_pct in [
        ("FRESH", 240.0, 72.0),
        ("FROZEN", 210.0, 68.0),
        ("RTE", 300.0, 70.0),
        ("FVA", 330.0, 66.0),
    ]:
        defaults.setdefault(product_id, {"price": price, "yield_pct": yield_pct})
    return defaults


def build_channel_product_volume_output(
    revenue_rupees,
    product_mix=None,
    channel_mix=None,
    product_registry=None,
    pricing_registry=None,
    working_days=25,
):
    revenue = max(0.0, _to_float(revenue_rupees, 0.0))
    wd = max(1.0, _to_float(working_days, 25))
    product_defaults = _product_registry_defaults(product_registry)
    product_ids = ["FRESH", "FROZEN", "RTE", "FVA"]
    channel_ids = [
        ("general_trade", "GT", "gt_revenue"),
        ("modern_trade", "MT", "mt_revenue"),
        ("quick_commerce", "QC", "qcom_revenue"),
        ("ecommerce", "ECOM", "ecommerce_revenue"),
        ("horeca", "HORECA", "horeca_revenue"),
        ("institution", "INST", "institutional_government_revenue"),
        ("exports", "EXP", "exports_revenue"),
    ]
    channel_shares = {channel_id: _mix_share(channel_mix, channel_id, 0.0) for _, channel_id, _ in channel_ids}
    if sum(channel_shares.values()) <= 0:
        channel_shares = {"GT": 0.40, "MT": 0.20, "QC": 0.10, "ECOM": 0.10, "HORECA": 0.15, "INST": 0.03, "EXP": 0.02}
    channel_total = sum(channel_shares.values()) or 1.0
    channel_shares = {key: value / channel_total for key, value in channel_shares.items()}
    product_shares = {product_id: _mix_share(product_mix, product_id, 0.0) for product_id in product_ids}
    if sum(product_shares.values()) <= 0:
        product_shares = {"FRESH": 0.40, "FROZEN": 0.30, "RTE": 0.15, "FVA": 0.15}
    product_total = sum(product_shares.values()) or 1.0
    product_shares = {key: value / product_total for key, value in product_shares.items()}

    output = {}
    channel_revenues = {}
    total_kg_month = 0.0
    weighted_price_numerator = 0.0
    weighted_yield_numerator = 0.0
    for output_key, channel_id, revenue_key in channel_ids:
        channel_revenue = revenue * channel_shares[channel_id]
        channel_revenues[revenue_key] = channel_revenue
        channel_output = {"revenue": channel_revenue, "total_kg_month": 0.0}
        for product_id in product_ids:
            product_revenue = channel_revenue * product_shares[product_id]
            price = _price_lookup(pricing_registry, product_id, channel_id, product_defaults[product_id]["price"])
            volume_kg = product_revenue / price if price > 0 else 0.0
            prefix = "fva" if product_id == "FVA" else product_id.lower()
            channel_output[f"{prefix}_revenue"] = product_revenue
            channel_output[f"{prefix}_kg_month"] = volume_kg
            channel_output[f"{prefix}_selling_price_per_kg"] = price
            channel_output["total_kg_month"] += volume_kg
            total_kg_month += volume_kg
            weighted_price_numerator += price * volume_kg
            weighted_yield_numerator += product_defaults[product_id]["yield_pct"] * volume_kg
        channel_output["total_mt_month"] = channel_output["total_kg_month"] / 1000.0
        channel_output["total_kg_day"] = channel_output["total_kg_month"] / wd
        channel_output["total_mt_day"] = channel_output["total_kg_day"] / 1000.0
        output[output_key] = channel_output
    return {
        "channels": output,
        "channel_revenues": channel_revenues,
        "total_planned_finished_goods_kg_month": total_kg_month,
        "total_planned_finished_goods_mt_month": total_kg_month / 1000.0,
        "total_planned_finished_goods_kg_day": total_kg_month / wd,
        "total_planned_finished_goods_mt_day": total_kg_month / wd / 1000.0,
        "weighted_selling_price": weighted_price_numerator / total_kg_month if total_kg_month > 0 else 240.0,
        "weighted_yield_pct": weighted_yield_numerator / total_kg_month if total_kg_month > 0 else 72.0,
    }


def build_plant_capacity_output(
    raw_material_output,
    capacity_per_line_mt_day=10.0,
    working_hours_per_shift=8.0,
    max_shifts=3,
    cold_storage_buffer_days=3,
    utilization_threshold_pct=85.0,
    installed_lines=None,
    active_shifts=None,
    maximum_lines_in_current_plant=None,
    safe_utilization_pct=85.0,
    review_utilization_pct=90.0,
    critical_utilization_pct=95.0,
    existing_plant_expandable=True,
    expansion_line_increment=1,
):
    required_capacity_mt_day = max(0.0, _to_float(raw_material_output.get("finished_goods_mt_day", 0.0), 0.0))
    plant_base_capacity_mt_day = max(0.1, _to_float(capacity_per_line_mt_day, 10.0))
    maximum_shifts_per_line = max(1, int(round(_to_float(max_shifts, 3.0))))
    safe_utilization_pct = _to_float(safe_utilization_pct, 85.0)
    review_utilization_pct = _to_float(review_utilization_pct, 90.0)
    critical_utilization_pct = _to_float(critical_utilization_pct, 95.0)

    installed_lines_provided = installed_lines is not None and _to_float(installed_lines, 0.0) > 0
    active_shifts_provided = active_shifts is not None and _to_float(active_shifts, 0.0) > 0

    if not installed_lines_provided:
        installed_lines_candidate = 1
    else:
        installed_lines_candidate = max(1, int(round(_to_float(installed_lines, 1.0))))

    if not active_shifts_provided:
        active_shifts_candidate = 1
    else:
        active_shifts_candidate = max(1, int(round(_to_float(active_shifts, 1.0))))
    active_shifts_candidate = min(active_shifts_candidate, maximum_shifts_per_line)

    if maximum_lines_in_current_plant is None or _to_float(maximum_lines_in_current_plant, 0.0) <= 0:
        default_max_lines = max(installed_lines_candidate + 1, 2)
        maximum_lines_in_current_plant = default_max_lines
    maximum_lines_in_current_plant = max(installed_lines_candidate, int(round(_to_float(maximum_lines_in_current_plant, installed_lines_candidate))))

    best_lines = installed_lines_candidate
    best_shifts = active_shifts_candidate
    best_capacity = plant_base_capacity_mt_day * best_lines * best_shifts
    if required_capacity_mt_day > 0 and not (installed_lines_provided and active_shifts_provided):
        best_pair = None
        for lines in range(1, maximum_lines_in_current_plant + 1):
            for shifts in range(1, maximum_shifts_per_line + 1):
                candidate_capacity = plant_base_capacity_mt_day * lines * shifts
                if candidate_capacity + 1e-9 < required_capacity_mt_day:
                    continue
                candidate = (candidate_capacity, lines, shifts)
                if best_pair is None or candidate < best_pair:
                    best_pair = candidate
        if best_pair is not None:
            best_capacity, best_lines, best_shifts = best_pair

    current_installed_capacity_mt_day = plant_base_capacity_mt_day * best_lines * best_shifts
    installed_capacity_mt_day = current_installed_capacity_mt_day
    maximum_current_plant_capacity_mt_day = plant_base_capacity_mt_day * maximum_lines_in_current_plant * maximum_shifts_per_line
    capacity_gap_mt_day = required_capacity_mt_day - installed_capacity_mt_day
    capacity_shortfall_mt_day = max(0.0, required_capacity_mt_day - installed_capacity_mt_day)
    capacity_headroom_mt_day = max(0.0, installed_capacity_mt_day - required_capacity_mt_day)
    remaining_current_site_capacity_mt_day = max(0.0, maximum_current_plant_capacity_mt_day - installed_capacity_mt_day)
    remaining_site_headroom_after_demand_mt_day = max(0.0, maximum_current_plant_capacity_mt_day - required_capacity_mt_day)
    current_load_ratio_pct = required_capacity_mt_day / installed_capacity_mt_day * 100.0 if installed_capacity_mt_day > 0 else 0.0
    utilization = current_load_ratio_pct

    can_add_shift = best_shifts < maximum_shifts_per_line
    can_add_line = best_lines < maximum_lines_in_current_plant
    shift_only_capacity_mt_day = plant_base_capacity_mt_day * best_lines * maximum_shifts_per_line
    line_only_capacity_mt_day = plant_base_capacity_mt_day * maximum_lines_in_current_plant * best_shifts
    shift_can_close_gap = can_add_shift and required_capacity_mt_day <= shift_only_capacity_mt_day
    line_can_close_gap = can_add_line and required_capacity_mt_day <= line_only_capacity_mt_day
    combined_can_close_gap = required_capacity_mt_day <= maximum_current_plant_capacity_mt_day and (can_add_shift or can_add_line)

    recommended_lines = best_lines
    recommended_shifts = best_shifts
    if required_capacity_mt_day > 0:
        recommended_pair = None
        for lines in range(best_lines, maximum_lines_in_current_plant + 1):
            for shifts in range(best_shifts, maximum_shifts_per_line + 1):
                candidate_capacity = plant_base_capacity_mt_day * lines * shifts
                if candidate_capacity + 1e-9 < required_capacity_mt_day:
                    continue
                candidate = (candidate_capacity, lines, shifts)
                if recommended_pair is None or candidate < recommended_pair:
                    recommended_pair = candidate
        if recommended_pair is not None:
            _, recommended_lines, recommended_shifts = recommended_pair
    recommended_capacity_mt_day = plant_base_capacity_mt_day * recommended_lines * recommended_shifts
    projected_utilization_pct = required_capacity_mt_day / recommended_capacity_mt_day * 100.0 if recommended_capacity_mt_day > 0 else 0.0
    remaining_shift_capacity_mt_day = max(0.0, shift_only_capacity_mt_day - installed_capacity_mt_day)
    remaining_line_capacity_mt_day = max(0.0, line_only_capacity_mt_day - installed_capacity_mt_day)
    expandable = bool(existing_plant_expandable)
    expanded_max_lines = maximum_lines_in_current_plant + max(0, int(round(_to_float(expansion_line_increment, 1.0)))) if expandable else maximum_lines_in_current_plant
    expanded_site_capacity_mt_day = plant_base_capacity_mt_day * expanded_max_lines * maximum_shifts_per_line

    expansion_stage = "A. Existing capacity sufficient"
    recommended_action = "Continue Current Configuration"
    supporting_actions = []
    decision_reason = "Current installed capacity is sufficient for required output."
    if required_capacity_mt_day <= installed_capacity_mt_day:
        if current_load_ratio_pct <= review_utilization_pct and current_load_ratio_pct > safe_utilization_pct:
            expansion_stage = "B. Optimize existing capacity"
            recommended_action = "Optimize Existing Capacity"
            decision_reason = "Current installed capacity meets demand but operating load is high enough to warrant optimization."
        else:
            expansion_stage = "A. Existing capacity sufficient"
            recommended_action = "Continue Current Configuration"
            decision_reason = "Current installed capacity meets required output."
    elif shift_can_close_gap:
        expansion_stage = "C. Add shift"
        recommended_action = "Add Shift"
        decision_reason = "Additional shift capacity within current lines can close the current shortfall."
    elif line_can_close_gap:
        expansion_stage = "D. Add production line"
        recommended_action = "Add Production Line"
        decision_reason = "Additional line capacity with current shifts can close the current shortfall."
    elif combined_can_close_gap:
        expansion_stage = "E. Expand existing plant"
        recommended_action = "Add Shift and Production Line"
        supporting_actions = ["Add Shift", "Add Production Line"]
        decision_reason = "Demand exceeds shift-only and line-only limits, but a combined shift and line expansion within current-site limits can close the shortfall."
    elif expandable and required_capacity_mt_day <= expanded_site_capacity_mt_day:
        expansion_stage = "E. Expand existing plant"
        recommended_action = "Expand Existing Plant"
        decision_reason = "Current-site configured limits are insufficient, but site expansion can still support required output."
    else:
        expansion_stage = "F. Build new plant"
        recommended_action = "Build New Plant"
        decision_reason = "Required output exceeds maximum current-site capacity and expandable options are exhausted."

    new_plant_required = recommended_action == "Build New Plant" and required_capacity_mt_day > maximum_current_plant_capacity_mt_day
    recommended_new_plant_capacity_mt_day = max(0.0, required_capacity_mt_day - maximum_current_plant_capacity_mt_day) if new_plant_required else 0.0

    expansion_required = "Yes" if utilization > _to_float(utilization_threshold_pct, 85.0) else "No"
    return {
        "finished_goods_mt_day": required_capacity_mt_day,
        "plant_capacity_mt_day": plant_base_capacity_mt_day,
        "capacity_per_line_mt_day": plant_base_capacity_mt_day,
        "plant_base_capacity_mt_day": plant_base_capacity_mt_day,
        "installed_lines": best_lines,
        "active_shifts": best_shifts,
        "maximum_shifts_per_line": maximum_shifts_per_line,
        "maximum_lines_in_current_plant": maximum_lines_in_current_plant,
        "current_installed_capacity_mt_day": current_installed_capacity_mt_day,
        "installed_capacity_mt_day": installed_capacity_mt_day,
        "maximum_current_plant_capacity_mt_day": maximum_current_plant_capacity_mt_day,
        "required_capacity_mt_day": required_capacity_mt_day,
        "capacity_gap_mt_day": capacity_gap_mt_day,
        "capacity_shortfall_mt_day": capacity_shortfall_mt_day,
        "capacity_headroom_mt_day": capacity_headroom_mt_day,
        "production_lines_required": best_lines,
        "plant_utilization_pct": utilization,
        "production_utilization_pct": utilization,
        "current_load_ratio_pct": current_load_ratio_pct,
        "recommended_lines": recommended_lines,
        "recommended_shifts": recommended_shifts,
        "recommended_capacity_mt_day": recommended_capacity_mt_day,
        "projected_utilization_pct": projected_utilization_pct,
        "shifts_required": best_shifts,
        "working_hours_per_shift": _to_float(working_hours_per_shift, 8.0),
        "max_shifts": float(maximum_shifts_per_line),
        "cold_storage_buffer_days": _to_float(cold_storage_buffer_days, 3.0),
        "cold_storage_required_mt": required_capacity_mt_day * _to_float(cold_storage_buffer_days, 3.0),
        "utilization_threshold_pct": _to_float(utilization_threshold_pct, 85.0),
        "safe_utilization_pct": safe_utilization_pct,
        "review_utilization_pct": review_utilization_pct,
        "critical_utilization_pct": critical_utilization_pct,
        "unused_capacity_mt_day": max(0.0, installed_capacity_mt_day - required_capacity_mt_day),
        "remaining_shift_capacity_mt_day": remaining_shift_capacity_mt_day,
        "remaining_line_capacity_mt_day": remaining_line_capacity_mt_day,
        "remaining_current_site_capacity_mt_day": remaining_current_site_capacity_mt_day,
        "remaining_site_headroom_after_demand_mt_day": remaining_site_headroom_after_demand_mt_day,
        "shift_only_capacity_mt_day": shift_only_capacity_mt_day,
        "line_only_capacity_mt_day": line_only_capacity_mt_day,
        "decision_reason": decision_reason,
        "supporting_actions": supporting_actions,
        "expansion_stage": expansion_stage,
        "recommended_action": recommended_action,
        "new_plant_required": "Yes" if new_plant_required else "No",
        "recommended_new_plant_capacity_mt_day": recommended_new_plant_capacity_mt_day,
        "existing_plant_expandable": "Yes" if expandable else "No",
        "can_add_shift": "Yes" if can_add_shift else "No",
        "can_add_line": "Yes" if can_add_line else "No",
        "expansion_required": expansion_required,
    }


def build_manpower_output(raw_material_output, plant_capacity_output, channel_mix=None, operating_model=None, business_stage=None, stage_profile=None, revenue_rupees=0.0):
    finished_goods_mt_day = _to_float(raw_material_output.get("finished_goods_mt_day", 0.0), 0.0)
    lines = int(plant_capacity_output.get("production_lines_required", 1) or 1)
    shifts = int(plant_capacity_output.get("shifts_required", 1) or 1)
    birds_day = _to_float(raw_material_output.get("birds_per_day", 0.0), 0.0)
    traders_managed = int(raw_material_output.get("traders_required", 1) or 1)
    farms_managed = int(raw_material_output.get("farms_required", 1) or 1)

    def governed_band(workload, bands, current_hc, reason, unit_label):
        selected = bands[-1]
        for band in bands:
            if workload <= band["upper"]:
                selected = band
                break
        if workload < selected["lower"]:
            status = "Persistent Underutilization Review"
            recommended = current_hc
        elif workload > selected["upper"]:
            status = "Additional HC Required"
            recommended = selected["hc"]
        else:
            status = "Within Current Staffing Band"
            recommended = current_hc if current_hc >= selected["hc"] else selected["hc"]
        if selected.get("temporary_support") and workload > selected["support_trigger"]:
            status = "Temporary Capacity Support"
        return {
            "current_workload": workload,
            "workload_unit": unit_label,
            "current_staffing_band": selected["label"],
            "lower_threshold": selected["lower"],
            "upper_threshold": selected["upper"],
            "current_hc": current_hc,
            "recommended_hc": recommended,
            "threshold_status": status,
            "business_reason": reason,
        }

    production_band = governed_band(
        finished_goods_mt_day,
        [
            {"label": "0-10 MT/day, 1 line, up to 1 shift", "lower": 4.0, "upper": 10.0, "hc": 46},
            {"label": "10-18 MT/day, 2 lines or extended shift", "lower": 10.0, "upper": 18.0, "hc": 54, "temporary_support": True, "support_trigger": 10.0},
            {"label": "18-28 MT/day, multi-line/multi-shift", "lower": 18.0, "upper": 28.0, "hc": 62, "temporary_support": True, "support_trigger": 18.0},
        ],
        46,
        "Production staffing is governed by MT/day, active lines, active shifts, automation level, sanitation coverage and supervision.",
        "MT/day",
    )
    warehouse_band = governed_band(
        finished_goods_mt_day,
        [
            {"label": "0-10 MT/day throughput, single dispatch rhythm", "lower": 3.0, "upper": 10.0, "hc": 6},
            {"label": "10-18 MT/day throughput or additional dispatch wave", "lower": 10.0, "upper": 18.0, "hc": 8, "temporary_support": True, "support_trigger": 10.0},
            {"label": "18-28 MT/day throughput, multi-zone cold room", "lower": 18.0, "upper": 28.0, "hc": 10, "temporary_support": True, "support_trigger": 18.0},
        ],
        6,
        "Warehouse and cold-room staffing is governed by throughput, dispatch count, FEFO control, cold-storage zones and shift coverage.",
        "MT/day",
    )
    production = int(production_band["recommended_hc"])
    warehouse = int(warehouse_band["recommended_hc"])
    sales = 9
    marketing = 2
    finance = 3
    hr = 2
    admin = 2
    qa_food_safety = 3
    procurement = 2
    total = production + warehouse + sales + marketing + finance + hr + admin + qa_food_safety + procurement
    qa_band = governed_band(
        shifts,
        [
            {"label": "1-2 active shifts / standard product coverage", "lower": 1.0, "upper": 2.0, "hc": 3},
            {"label": "3 active shifts or expanded product groups", "lower": 2.0, "upper": 3.0, "hc": 4, "temporary_support": True, "support_trigger": 2.0},
        ],
        qa_food_safety,
        "QA / Food Safety staffing is governed by active shifts, production lines, product groups, process checks and compliance coverage.",
        "active shifts",
    )
    procurement_band = governed_band(
        birds_day,
        [
            {"label": "0-25,000 birds/day, local trader/farm network", "lower": 0.0, "upper": 25000.0, "hc": 2},
            {"label": "25,000-50,000 birds/day or multi-region sourcing", "lower": 25000.0, "upper": 50000.0, "hc": 3, "temporary_support": True, "support_trigger": 25000.0},
        ],
        procurement,
        f"Procurement staffing is governed by birds/day, farms/traders managed ({farms_managed} farms, {traders_managed} traders) and sourcing regions.",
        "birds/day",
    )
    finance_band = governed_band(
        revenue_rupees,
        [
            {"label": "up to Rs 10 Cr/month transaction complexity", "lower": 0.0, "upper": 100000000.0, "hc": 3},
            {"label": "Rs 10-20 Cr/month, higher AR/AP and MIS load", "lower": 100000000.0, "upper": 200000000.0, "hc": 4},
        ],
        finance,
        "Finance staffing is governed by transaction volume, collections, vendor payments, GST, MIS and banking complexity.",
        "Rs/month",
    )
    marketing_band = governed_band(
        revenue_rupees,
        [
            {"label": "startup activation band up to Rs 10 Cr/month", "lower": 0.0, "upper": 100000000.0, "hc": 2},
            {"label": "regional activation band above Rs 10 Cr/month", "lower": 100000000.0, "upper": 200000000.0, "hc": 3},
        ],
        marketing,
        "Marketing staffing is governed by brand activation, trade promotions, POSM, digital campaigns and product launches.",
        "Rs/month",
    )
    hr_band = governed_band(
        total,
        [
            {"label": "up to 100 employees / one site", "lower": 0.0, "upper": 100.0, "hc": 2},
            {"label": "100-200 employees or multi-shift hiring load", "lower": 100.0, "upper": 200.0, "hc": 3},
        ],
        hr,
        "HR staffing is governed by total employee bands, plant attendance, payroll, compliance, recruitment and contractor coordination.",
        "employees",
    )
    admin_band = governed_band(
        total,
        [
            {"label": "up to 100 employees / one plant office", "lower": 0.0, "upper": 100.0, "hc": 2},
            {"label": "100-200 employees or higher site complexity", "lower": 100.0, "upper": 200.0, "hc": 3},
        ],
        admin,
        "Admin staffing is governed by site complexity, utilities, security, housekeeping, AMC/vendor coordination and office support.",
        "employees",
    )
    staffing_bands = {
        "production": production_band,
        "warehouse": warehouse_band,
        "qa_food_safety": qa_band,
        "procurement": procurement_band,
        "sales": {"current_workload": revenue_rupees, "workload_unit": "channel workload", "current_staffing_band": "channel coverage threshold", "lower_threshold": 0.0, "upper_threshold": revenue_rupees, "current_hc": sales, "recommended_hc": sales, "threshold_status": "Within Current Staffing Band", "business_reason": "Sales staffing is governed by channel workload and coverage thresholds, not linear revenue or tonnage."},
        "marketing": marketing_band,
        "finance": finance_band,
        "hr": hr_band,
        "admin": admin_band,
    }
    production = int(production_band["recommended_hc"])
    warehouse = int(warehouse_band["recommended_hc"])
    qa_food_safety = int(qa_band["recommended_hc"])
    procurement = int(procurement_band["recommended_hc"])
    marketing = int(marketing_band["recommended_hc"])
    finance = int(finance_band["recommended_hc"])
    hr = int(hr_band["recommended_hc"])
    admin = int(admin_band["recommended_hc"])
    total = production + warehouse + sales + marketing + finance + hr + admin + qa_food_safety + procurement
    return {
        "production": production,
        "warehouse": warehouse,
        "sales": sales,
        "marketing": marketing,
        "finance": finance,
        "hr": hr,
        "admin": admin,
        "qa_food_safety": qa_food_safety,
        "procurement": procurement,
        "total_employees": total,
        "finished_goods_mt_day": finished_goods_mt_day,
        "production_lines": lines,
        "business_stage": business_stage or "Startup",
        "operating_model": operating_model or "Asset Light / Semi Automatic",
        "production_mt_per_person_day": finished_goods_mt_day / max(1, production),
        "staffing_bands": staffing_bands,
    }


def align_manpower_sales(manpower_output, channel_sales_output):
    aligned = _normalize_mapping(manpower_output)
    channel_data = _normalize_mapping(channel_sales_output)
    sales_hc = int(channel_data.get("total_sales_hc", channel_data.get("total_commercial_hc", aligned.get("sales", 0))) or 0)
    aligned["sales"] = sales_hc
    staffing_bands = dict(aligned.get("staffing_bands", {}) or {})
    sales_band = dict(staffing_bands.get("sales", {}) or {})
    sales_band.update({
        "current_workload": _to_float(channel_data.get("selected_market_revenue", sales_band.get("current_workload", 0.0)), 0.0),
        "current_staffing_band": "channel coverage threshold",
        "current_hc": sales_hc,
        "recommended_hc": sales_hc,
        "threshold_status": "Within Current Staffing Band",
        "business_reason": "Sales staffing is governed by final channel workload, coverage thresholds, account ownership and sales coordination requirements.",
    })
    staffing_bands["sales"] = sales_band
    aligned["staffing_bands"] = staffing_bands
    total_keys = ["production", "warehouse", "sales", "marketing", "finance", "hr", "admin", "qa_food_safety", "procurement"]
    aligned["total_employees"] = sum(int(aligned.get(key, 0) or 0) for key in total_keys)
    return aligned


def _cold_chain_required(product_mix):
    return bool(_mix_share(product_mix, "frozen", 0.0) or _mix_share(product_mix, "rte", 0.0))


def build_logistics_output(
    plant_raw_material_output=None,
    market_raw_material_output=None,
    product_mix=None,
    market_distance_km=0.0,
    avg_bird_weight=1.8,
    working_days=25,
    primary_vehicle_capacity_kg=4000.0,
    primary_trips_per_vehicle_per_day=2,
    average_primary_distance_km=100.0,
    primary_cost_per_km=28.0,
    primary_fixed_cost_per_trip=1500.0,
    secondary_vehicle_capacity_mt=2.0,
    secondary_trips_per_vehicle_per_day=2,
    secondary_cost_per_km=32.0,
    secondary_fixed_cost_per_trip=2000.0,
    cold_chain_cost_multiplier=1.20,
    plant_id=None,
    raw_material_output=None,
    selected_market_finished_goods_mt_day=None,
    cold_chain_required=True,
    **kwargs,
):
    plant_raw = plant_raw_material_output or raw_material_output or {}
    market_raw = market_raw_material_output or raw_material_output or {}
    wd = max(1, int(_to_float(working_days, 25)))
    live_weight_kg_day = _to_float(plant_raw.get("live_weight_kg_day", plant_raw.get("live_bird_kg", 0.0) / wd), 0.0)
    finished_goods_mt_day = _to_float(selected_market_finished_goods_mt_day, _to_float(market_raw.get("finished_goods_mt_day", 0.0), 0.0))
    primary_trips = math.ceil(live_weight_kg_day / max(1.0, _to_float(primary_vehicle_capacity_kg, 4000.0))) if live_weight_kg_day > 0 else 0
    primary_vehicles = math.ceil(primary_trips / max(1.0, _to_float(primary_trips_per_vehicle_per_day, 2)))
    primary_cost_day = primary_trips * (_to_float(average_primary_distance_km, 100.0) * _to_float(primary_cost_per_km, 28.0) + _to_float(primary_fixed_cost_per_trip, 1500.0))
    secondary_trips = math.ceil(finished_goods_mt_day / max(0.1, _to_float(secondary_vehicle_capacity_mt, 2.0))) if finished_goods_mt_day > 0 else 0
    secondary_vehicles = math.ceil(secondary_trips / max(1.0, _to_float(secondary_trips_per_vehicle_per_day, 2)))
    cold_chain = bool(cold_chain_required if cold_chain_required is not None else _cold_chain_required(product_mix))
    multiplier = _to_float(cold_chain_cost_multiplier, 1.2) if cold_chain else 1.0
    secondary_cost_day = secondary_trips * (_to_float(market_distance_km, 0.0) * _to_float(secondary_cost_per_km, 32.0) + _to_float(secondary_fixed_cost_per_trip, 2000.0)) * multiplier
    return {
        "primary": {
            "live_weight_kg_day": live_weight_kg_day,
            "birds_per_day": _to_float(plant_raw.get("birds_per_day", 0.0), 0.0),
            "average_bird_weight": _to_float(avg_bird_weight, 1.8),
            "trips_day": primary_trips,
            "vehicles_required": primary_vehicles,
            "cost_day": primary_cost_day,
            "cost_month": primary_cost_day * wd,
            "average_distance_km": _to_float(average_primary_distance_km, 100.0),
            "vehicle_capacity_kg": _to_float(primary_vehicle_capacity_kg, 4000.0),
        },
        "secondary": {
            "finished_goods_mt_day": finished_goods_mt_day,
            "trips_day": secondary_trips,
            "vehicles_required": secondary_vehicles,
            "cost_day": secondary_cost_day,
            "cost_month": secondary_cost_day * wd,
            "market_distance_km": _to_float(market_distance_km, 0.0),
            "vehicle_capacity_mt": _to_float(secondary_vehicle_capacity_mt, 2.0),
            "cold_chain_required": "Yes" if cold_chain else "No",
        },
        "total_logistics_cost_month": primary_cost_day * wd + secondary_cost_day * wd,
    }


def build_actual_order_output(order_registry=None, plant_id=None, planning_date=None, operating_mode="PLANNING", planned_channel_volume_kg=None):
    planned_channel_volume_kg = planned_channel_volume_kg or {}
    if operating_mode == "PLANNING":
        total = sum(_to_float(v, 0.0) for v in planned_channel_volume_kg.values())
        return {
            "actual_order_demand_kg": total,
            "actual_order_demand_mt": total / 1000.0,
            "orders_count": 0,
            "demand_by_channel": dict(planned_channel_volume_kg),
            "demand_by_product_group": {},
            "demand_by_delivery_date": {},
            "demand_by_market": {},
            "source": "PLANNING",
        }
    return {
        "actual_order_demand_kg": 0.0,
        "actual_order_demand_mt": 0.0,
        "orders_count": 0,
        "demand_by_channel": {},
        "demand_by_product_group": {},
        "demand_by_delivery_date": {},
        "demand_by_market": {},
        "source": "ORDER_REGISTRY",
    }


def build_order_capacity_intelligence(
    raw_material_output,
    plant_capacity_output,
    channel_sales_output,
    order_registry=None,
    plant_id=None,
    operating_mode="PLANNING",
    available_finished_goods_inventory_kg=0.0,
    committed_production_kg=0.0,
    minimum_line_utilization_pct=60.0,
    underutilization_observation_days=5,
    capacity_breach_observation_days=5,
    persistence_days=1,
    average_bird_weight_kg=None,
    scenario_mode="No Scenario",
    channel_achievement_pct=None,
    manual_order_volume_kg=None,
    releasable_cold_inventory_mt=0.0,
    committed_capacity_mt_day=0.0,
    current_marketing_spend=0.0,
    gross_contribution_pct=0.0,
):
    working_days = max(1.0, _to_float(raw_material_output.get("working_days", 25), 25))
    selected_revenue = max(0.0, _to_float(channel_sales_output.get("selected_market_revenue", raw_material_output.get("revenue_rupees", 0.0)), 0.0))
    planned_month_kg = max(0.0, _to_float(raw_material_output.get("finished_goods_kg", 0.0), 0.0))
    installed_capacity_mt_day = max(0.0, _to_float(plant_capacity_output.get("installed_capacity_mt_day", plant_capacity_output.get("plant_capacity_mt_day", 0.0)), 0.0))
    committed_mt_day = max(0.0, _to_float(committed_capacity_mt_day, 0.0))
    if committed_mt_day <= 0 and committed_production_kg:
        committed_mt_day = max(0.0, _to_float(committed_production_kg, 0.0)) / 1000.0
    net_capacity_mt_day = max(0.0, installed_capacity_mt_day - committed_mt_day)
    channel_revenue_keys = {
        "GT": "gt_revenue",
        "MT": "mt_revenue",
        "QCom": "qcom_revenue",
        "E-commerce": "ecommerce_revenue",
        "HoReCa": "horeca_revenue",
        "Institutional / Government": "institutional_government_revenue",
        "Exports": "exports_revenue",
    }
    planned_kg_day = {}
    volume_channels = (raw_material_output.get("channel_product_volume_output", {}) or {}).get("channels", {})
    volume_key_map = {
        "GT": "general_trade",
        "MT": "modern_trade",
        "QCom": "quick_commerce",
        "E-commerce": "ecommerce",
        "HoReCa": "horeca",
        "Institutional / Government": "institution",
        "Exports": "exports",
    }
    for channel, key in channel_revenue_keys.items():
        volume_key = volume_key_map[channel]
        if volume_key in volume_channels:
            planned_kg_day[channel] = _to_float(volume_channels[volume_key].get("total_kg_day"), 0.0)
        else:
            revenue = max(0.0, _to_float(channel_sales_output.get(key, 0.0), 0.0))
            planned_kg_day[channel] = (planned_month_kg * revenue / selected_revenue / working_days) if selected_revenue > 0 else 0.0
    scenario_mode = str(scenario_mode or "No Scenario")
    scenario_key = scenario_mode.upper().replace(" ", "_")
    if scenario_key == "CHANNEL_ACHIEVEMENT_%":
        scenario_active, order_source = True, "SCENARIO_PERCENT"
    elif scenario_key == "MANUAL_ORDER_VOLUME":
        scenario_active, order_source = True, "SCENARIO_MANUAL"
    else:
        scenario_active, order_source, scenario_mode = False, "NONE", "No Scenario"

    def zero_output():
        return {
            "scenario_active": False,
            "scenario_mode": "No Scenario",
            "order_source": "NONE",
            "is_baseline_simulation": False,
            "scenario_horizon": "DAY",
            "planned_demand_kg": 0.0,
            "planned_demand_mt_day": 0.0,
            "scenario_order_demand_kg": 0.0,
            "scenario_order_demand_mt_day": 0.0,
            "demand_variance_kg_day": 0.0,
            "demand_variance_mt_day": 0.0,
            "demand_variance_pct": 0.0,
            "demand_variance_status": "Not Simulated",
            "demand_variance_explanation": "No order scenario has been activated.",
            "scenario_variance_explanation": "No order scenario has been activated.",
            "actual_order_demand_kg": 0.0,
            "actual_order_demand_mt": 0.0,
            "overall_achievement_pct": 0.0,
            "achievement_pct": 0.0,
            "available_inventory_kg": 0.0,
            "available_inventory_mt": 0.0,
            "available_production_capacity_kg": 0.0,
            "available_plant_capacity_mt_day": 0.0,
            "total_available_supply_kg": 0.0,
            "total_fulfilment_capability_mt": 0.0,
            "production_required_mt_day": 0.0,
            "capacity_gap_kg": 0.0,
            "capacity_gap_mt": 0.0,
            "shortage_kg": 0.0,
            "shortage_mt": 0.0,
            "additional_capacity_required_mt_day": 0.0,
            "plant_utilization_pct": 0.0,
            "line_utilization_pct": 0.0,
            "scenario_plant_utilization_pct": 0.0,
            "scenario_line_utilization_pct": 0.0,
            "capacity_status": "NOT_SIMULATED",
            "plant_supply_available_kg": 0.0,
            "inventory_build_risk_kg": 0.0,
            "stockout_risk": "No",
            "fixed_cost_absorption_risk": "No",
            "status": "NOT_SIMULATED",
            "warning_type": "Not Simulated",
            "recommended_actions": [],
            "capacity_recommendations": [],
            "marketing_warnings": [],
            "marketing_recommendations": [],
            "procurement_recommendations": [],
            "logistics_recommendations": [],
            "manpower_recommendations": [],
            "business_impact": "No order scenario has been activated. Order and capacity signals will remain zero until a scenario is selected.",
            "ceo_summary": "No order scenario has been activated. Select a scenario to compare channel demand, releasable inventory and plant capacity.",
            "persistence_days": persistence_days,
            "persistence_status": "Not Simulated",
            "observation_status": "Not simulated - no scenario order assumptions are active.",
            "actual_order_output": build_actual_order_output(operating_mode="EMPTY"),
            "channel_planned_vs_actual": {},
            "channel_results": {},
            "inventory_impact": {"inventory_build_risk_kg": 0.0, "days_of_inventory": 0.0, "fresh_expiry_risk": "No", "frozen_storage_impact": 0.0, "inventory_depletion_days": None, "stockout_risk": "No"},
            "affected_orders": 0,
            "affected_markets": [],
            "affected_channels": [],
            "required_extra_shift": "No",
            "required_extra_line": "No",
            "required_outsourcing_mt": 0.0,
            "additional_birds_required": 0.0,
            "cold_storage_impact": "Not simulated.",
            "logistics_impact": "Not simulated.",
            "minimum_line_utilization_pct": minimum_line_utilization_pct,
            "underutilization_observation_days": underutilization_observation_days,
            "capacity_breach_observation_days": capacity_breach_observation_days,
        }

    if not scenario_active:
        return zero_output()

    channel_achievement_pct = channel_achievement_pct or {}
    manual_order_volume_kg = manual_order_volume_kg or {}
    scenario_kg_day = {}
    for channel, planned in planned_kg_day.items():
        if order_source == "SCENARIO_PERCENT":
            scenario_kg_day[channel] = planned * max(0.0, _to_float(channel_achievement_pct.get(channel, 100.0), 100.0)) / 100.0
        else:
            scenario_kg_day[channel] = max(0.0, _to_float(manual_order_volume_kg.get(channel, planned), planned))

    planned_demand_kg_day = sum(planned_kg_day.values())
    scenario_order_kg_day = sum(scenario_kg_day.values())
    planned_demand_mt_day = planned_demand_kg_day / 1000.0
    scenario_order_mt_day = scenario_order_kg_day / 1000.0
    demand_variance_kg_day = scenario_order_kg_day - planned_demand_kg_day
    demand_variance_mt_day = scenario_order_mt_day - planned_demand_mt_day
    demand_variance_pct = (demand_variance_mt_day / planned_demand_mt_day * 100.0) if planned_demand_mt_day > 0 else 0.0
    tolerance_mt_day = 0.0005
    if demand_variance_mt_day > tolerance_mt_day:
        demand_variance_status = "Above Plan"
    elif demand_variance_mt_day < -tolerance_mt_day:
        demand_variance_status = "Below Plan"
    else:
        demand_variance_status = "On Plan"
    available_inventory_mt = max(0.0, _to_float(releasable_cold_inventory_mt, 0.0))
    if available_inventory_mt <= 0 and available_finished_goods_inventory_kg:
        available_inventory_mt = max(0.0, _to_float(available_finished_goods_inventory_kg, 0.0)) / 1000.0
    total_capability_mt = net_capacity_mt_day + available_inventory_mt
    production_required_mt_day = max(scenario_order_mt_day - available_inventory_mt, 0.0)
    capacity_gap_mt = total_capability_mt - scenario_order_mt_day
    shortage_mt = max(0.0, -capacity_gap_mt)
    achievement_pct = scenario_order_mt_day / planned_demand_mt_day * 100.0 if planned_demand_mt_day > 0 else 0.0
    utilization_pct = production_required_mt_day / net_capacity_mt_day * 100.0 if net_capacity_mt_day > 0 else 0.0
    if scenario_order_mt_day > total_capability_mt:
        capacity_status, warning_type = "CAPACITY_BREACH", "Capacity Breach"
    elif utilization_pct > 100:
        capacity_status, warning_type = "OVER_CAPACITY", "Over Capacity"
    elif utilization_pct > 85:
        capacity_status, warning_type = "CAPACITY_PRESSURE", "Capacity Pressure"
    elif utilization_pct >= 60:
        capacity_status, warning_type = "HEALTHY", "Healthy"
    elif utilization_pct >= 40:
        capacity_status, warning_type = "UNDER_UTILIZED", "Under-Utilized"
    else:
        capacity_status, warning_type = "CRITICAL_UNDER_UTILIZATION", "Critical Under-Utilization"
    persistence_label = "Normal" if capacity_status == "HEALTHY" else "Observe" if persistence_days < 3 else "Warning" if persistence_days < 5 else "Operational Recommendation" if persistence_days < 15 else "Structural Review"

    def channel_status(pct):
        return "Strong Overachievement" if pct >= 120 else "On Plan / Above Plan" if pct >= 100 else "Watch" if pct >= 80 else "Marketing Warning" if pct >= 60 else "Critical Under-Plan"

    def channel_comment(channel, pct):
        if channel == "GT" and pct < 100:
            return "GT orders are below planned channel demand. Review distributor activation, outlet coverage, beat productivity and schemes."
        if channel == "QCom" and pct >= 120:
            return "Quick Commerce orders exceed plan. Review dark-store replenishment, stock availability and SLA capability."
        if channel == "HoReCa" and pct < 100:
            return "HoReCa orders are below required planning volume. Increase account activation and contract follow-up before scheduling full production."
        if channel == "Institutional / Government" and pct < 100:
            return "Institutional order release is below the planned tender volume. Review award schedules, documentation and order-release timelines."
        if pct >= 120:
            return f"{channel} orders exceed plan. Verify supply, service capability and commercial exposure before accepting further growth."
        if pct < 100:
            return f"{channel} orders are below planned demand. Review activation, pricing, availability and account follow-up."
        return f"{channel} is tracking to the planned channel demand."

    revenue_per_kg_day = (selected_revenue / working_days) / planned_demand_kg_day if planned_demand_kg_day > 0 else 0.0
    channel_results = {}
    marketing_warnings = []
    affected_channels = []
    for channel, planned in planned_kg_day.items():
        actual = scenario_kg_day.get(channel, 0.0)
        pct = actual / planned * 100.0 if planned > 0 else 0.0
        shortfall = max(0.0, planned - actual)
        excess = max(0.0, actual - planned)
        planned_rev = planned * revenue_per_kg_day
        scenario_rev = actual * revenue_per_kg_day
        if pct < 100 or pct >= 120:
            affected_channels.append(channel)
        if pct < 80:
            spend_pct = 8.0 if pct >= 60 else 0.0
            reason = f"{channel}: {'targeted activation increase of 5% to 10%' if pct >= 60 else 'root-cause review required before increasing spend'}. Shortfall is {shortfall / 1000.0:,.1f} MT/day with revenue gap of {abs(scenario_rev - planned_rev):,.0f}."
            marketing_warnings.append({"channel": channel, "reason": reason, "suggested_increase_pct": spend_pct})
        elif pct < 100:
            reason = f"{channel}: optimize existing activation before adding budget. Shortfall is {shortfall / 1000.0:,.1f} MT/day with revenue gap of {abs(scenario_rev - planned_rev):,.0f}."
        else:
            reason = "No automatic spend increase. Verify supply capability and service readiness first."
        comment = channel_comment(channel, pct)
        channel_results[channel] = {
            "planned_volume_kg": planned,
            "planned_volume_mt_day": planned / 1000.0,
            "planned_demand_mt_day": planned / 1000.0,
            "actual_order_volume_kg": actual,
            "actual_order_kg": actual,
            "scenario_order_mt_day": actual / 1000.0,
            "scenario_demand_mt_day": actual / 1000.0,
            "variance_kg_day": actual - planned,
            "variance_mt_day": (actual - planned) / 1000.0,
            "contribution_to_total_variance_mt_day": (actual - planned) / 1000.0,
            "achievement_pct": pct,
            "shortfall_kg": shortfall,
            "shortfall_mt_day": shortfall / 1000.0,
            "excess_kg": excess,
            "excess_mt_day": excess / 1000.0,
            "planned_revenue": planned_rev,
            "scenario_revenue_equivalent": scenario_rev,
            "revenue_gap": scenario_rev - planned_rev,
            "status": channel_status(pct),
            "commercial_comment": comment,
            "recommended_actions": [comment],
            "marketing_action_required": pct < 80,
            "recommended_marketing_spend_change_pct": 8.0 if 60 <= pct < 80 else 0.0,
            "marketing_reason": reason,
            "current_marketing_spend": _to_float(current_marketing_spend, 0.0),
            "suggested_marketing_spend_increase": _to_float(current_marketing_spend, 0.0) * (8.0 if 60 <= pct < 80 else 0.0) / 100.0,
            "expected_recovery_volume_kg": shortfall * (0.35 if 60 <= pct < 80 else 0.20 if pct < 60 else 0.25 if pct < 100 else 0.0),
            "expected_recovery_revenue": abs(scenario_rev - planned_rev) * (0.35 if 60 <= pct < 80 else 0.20 if pct < 60 else 0.25 if pct < 100 else 0.0),
            "expected_gross_contribution": abs(scenario_rev - planned_rev) * max(0.0, _to_float(gross_contribution_pct, 0.0)),
            "approval_required": "CEO / commercial approval required" if 60 <= pct < 80 else "No budget increase approval required",
        }

    if capacity_status == "CAPACITY_BREACH":
        capacity_recommendations = [
            f"Capacity breach of {shortage_mt:,.1f} MT/day against the selected scenario.",
            "Use remaining releasable inventory first.",
            "Use approved overtime before structural capacity decisions.",
            "Add an additional shift if overtime cannot close the shortage.",
            "Activate idle line capacity.",
            "Use temporary labour.",
            "Evaluate temporary outsourcing.",
            "Increase bird procurement only for executable confirmed demand.",
            "Review logistics and cold-storage readiness.",
            "Consider structural CAPEX only after persistence is proven.",
        ]
    elif capacity_status in {"UNDER_UTILIZED", "CRITICAL_UNDER_UTILIZATION"}:
        capacity_recommendations = ["Consolidate production into fewer days.", "Reduce active shifts.", "Reduce bird lifting.", "Reduce fresh production.", "Divert suitable production into frozen or RTE.", "Increase channel activation.", "Review promotions and pricing.", "Protect fixed-cost recovery."]
    elif capacity_status == "CAPACITY_PRESSURE":
        capacity_recommendations = ["Scenario demand is fulfilable but capacity flexibility is tight.", "Review inventory replenishment, bird procurement and next-day capacity before accepting further orders."]
    else:
        capacity_recommendations = ["Scenario demand is within daily fulfilment capability."]
    marketing_recommendations = [item["reason"] for item in marketing_warnings] or ["No automatic marketing-spend increase recommended."]
    procurement_recommendations = ["Increase live-bird procurement only against executable scenario demand."] if shortage_mt > 0 else ["Align bird lifting with scenario production requirement."]
    logistics_recommendations = ["Review dispatch fleet, route capacity and cold-chain readiness."] if shortage_mt > 0 or utilization_pct > 85 else ["Maintain logistics plan for the selected scenario."]
    manpower_recommendations = ["Use temporary manpower before structural hiring."] if shortage_mt > 0 else ["Align shifts and labour scheduling with scenario production requirement."]
    if capacity_status == "CAPACITY_BREACH":
        ceo_summary = f"Scenario demand exceeds daily fulfilment capability by {shortage_mt:,.1f} MT. Production required is {production_required_mt_day:,.1f} MT/day against {net_capacity_mt_day:,.1f} MT/day available plant capacity."
    elif capacity_status == "CAPACITY_PRESSURE":
        ceo_summary = f"Scenario demand is {achievement_pct - 100.0:,.1f}% above the channel plan but remains fulfilable through {available_inventory_mt:,.1f} MT of releasable inventory and {utilization_pct:,.1f}% plant utilization."
    elif capacity_status in {"UNDER_UTILIZED", "CRITICAL_UNDER_UTILIZATION"}:
        ceo_summary = f"Scenario orders require only {utilization_pct:,.1f}% of available daily plant capacity, creating fixed-cost absorption risk."
    else:
        ceo_summary = "Scenario demand is within the selected daily plant capacity and releasable inventory assumptions."
    offset_channels = [channel for channel, data in channel_results.items() if data.get("variance_mt_day", 0.0) > 0.000001]
    shortfall_channels = [channel for channel, data in channel_results.items() if data.get("variance_mt_day", 0.0) < -0.000001]
    if offset_channels and shortfall_channels:
        scenario_variance_explanation = f"{', '.join(offset_channels)} overachievement partly offsets {', '.join(shortfall_channels)} shortfalls. Consolidated scenario demand is {abs(demand_variance_pct):,.1f}% {'above' if demand_variance_pct > 0 else 'below'} plan."
    elif offset_channels:
        scenario_variance_explanation = f"{', '.join(offset_channels)} overachievement lifts consolidated scenario demand {abs(demand_variance_pct):,.1f}% above plan."
    elif shortfall_channels:
        scenario_variance_explanation = f"{', '.join(shortfall_channels)} shortfalls reduce consolidated scenario demand {abs(demand_variance_pct):,.1f}% below plan."
    else:
        scenario_variance_explanation = "Scenario demand is aligned with the channel-mix planning baseline."
    actual_order_output = build_actual_order_output(operating_mode="EMPTY")
    actual_order_output["demand_by_channel"] = scenario_kg_day
    actual_order_output["actual_order_demand_kg"] = scenario_order_kg_day
    actual_order_output["actual_order_demand_mt"] = scenario_order_mt_day
    inventory_build_risk_kg = max(0.0, planned_demand_kg_day - scenario_order_kg_day)
    avg_bird_weight = max(0.1, _to_float(average_bird_weight_kg, raw_material_output.get("avg_bird_weight", 1.8)))
    additional_birds_required = shortage_mt * 1000.0 / max(0.01, _to_float(raw_material_output.get("weighted_yield", 0.72), 0.72)) / avg_bird_weight if shortage_mt > 0 else 0.0
    return {
        "scenario_active": True,
        "scenario_mode": scenario_mode,
        "order_source": order_source,
        "is_baseline_simulation": False,
        "scenario_horizon": "DAY",
        "planned_demand_kg": planned_demand_kg_day,
        "planned_demand_mt_day": planned_demand_mt_day,
        "scenario_order_demand_kg": scenario_order_kg_day,
        "scenario_order_demand_mt_day": scenario_order_mt_day,
        "demand_variance_kg_day": demand_variance_kg_day,
        "demand_variance_mt_day": demand_variance_mt_day,
        "demand_variance_pct": demand_variance_pct,
        "demand_variance_status": demand_variance_status,
        "demand_variance_explanation": scenario_variance_explanation,
        "scenario_variance_explanation": scenario_variance_explanation,
        "actual_order_demand_kg": scenario_order_kg_day,
        "actual_order_demand_mt": scenario_order_mt_day,
        "overall_achievement_pct": achievement_pct,
        "achievement_pct": achievement_pct,
        "available_inventory_kg": available_inventory_mt * 1000.0,
        "available_inventory_mt": available_inventory_mt,
        "available_production_capacity_kg": net_capacity_mt_day * 1000.0,
        "available_plant_capacity_mt_day": net_capacity_mt_day,
        "total_available_supply_kg": total_capability_mt * 1000.0,
        "total_fulfilment_capability_mt": total_capability_mt,
        "production_required_mt_day": production_required_mt_day,
        "capacity_gap_kg": capacity_gap_mt * 1000.0,
        "capacity_gap_mt": capacity_gap_mt,
        "shortage_kg": shortage_mt * 1000.0,
        "shortage_mt": shortage_mt,
        "additional_capacity_required_mt_day": shortage_mt,
        "plant_utilization_pct": utilization_pct,
        "line_utilization_pct": utilization_pct,
        "scenario_plant_utilization_pct": utilization_pct,
        "scenario_line_utilization_pct": utilization_pct,
        "capacity_status": capacity_status,
        "plant_supply_available_kg": total_capability_mt * 1000.0,
        "inventory_build_risk_kg": inventory_build_risk_kg,
        "stockout_risk": "Yes" if shortage_mt > 0 else "No",
        "fixed_cost_absorption_risk": "Yes" if utilization_pct < _to_float(minimum_line_utilization_pct, 60.0) else "No",
        "status": capacity_status,
        "warning_type": warning_type,
        "recommended_actions": capacity_recommendations,
        "capacity_recommendations": capacity_recommendations,
        "marketing_warnings": marketing_warnings,
        "marketing_recommendations": marketing_recommendations,
        "procurement_recommendations": procurement_recommendations,
        "logistics_recommendations": logistics_recommendations,
        "manpower_recommendations": manpower_recommendations,
        "business_impact": ceo_summary,
        "ceo_summary": ceo_summary,
        "persistence_days": persistence_days,
        "persistence_status": persistence_label,
        "observation_status": f"{persistence_label} - scenario mode is simulated and not yet connected to historical daily order persistence.",
        "actual_order_output": actual_order_output,
        "channel_planned_vs_actual": channel_results,
        "channel_results": channel_results,
        "inventory_impact": {"inventory_build_risk_kg": inventory_build_risk_kg, "days_of_inventory": available_inventory_mt / scenario_order_mt_day if scenario_order_mt_day > 0 else 0.0, "fresh_expiry_risk": "Yes" if inventory_build_risk_kg > 0 else "No", "frozen_storage_impact": inventory_build_risk_kg / 1000.0, "inventory_depletion_days": available_inventory_mt / scenario_order_mt_day if scenario_order_mt_day > 0 else None, "stockout_risk": "Yes" if shortage_mt > 0 else "No"},
        "affected_orders": 0,
        "affected_markets": [],
        "affected_channels": affected_channels,
        "required_extra_shift": "Yes" if shortage_mt > 0 else "No",
        "required_extra_line": "Review if persistent" if shortage_mt > 0 else "No",
        "required_outsourcing_mt": shortage_mt,
        "additional_birds_required": additional_birds_required,
        "cold_storage_impact": "Review releasable inventory and cold-chain flow for the selected day.",
        "logistics_impact": "Additional dispatch planning required." if shortage_mt > 0 else "Normal dispatch plan.",
        "minimum_line_utilization_pct": minimum_line_utilization_pct,
        "underutilization_observation_days": underutilization_observation_days,
        "capacity_breach_observation_days": capacity_breach_observation_days,
    }


def build_contract_pricing_output(
    live_bird_rate,
    contract_volume_kg_month=0.0,
    awarded_volume_kg_month=0.0,
    average_live_bird_weight_kg=1.8,
    dressed_output_kg=1.3,
    processing_cost_per_kg=12.0,
    packaging_cost_per_kg=8.0,
    cold_chain_logistics_cost_per_kg=6.0,
    factory_overhead_per_kg=5.0,
    target_margin_pct=18.0,
    institutional_pack_size_kg=2.0,
    procurement_drivers=None,
    yield_pct=None,
    mortality_pct=None,
    processing_loss_pct=None,
    gt_distributor_margin_pct=None,
    transport_cost_per_kg=None,
    operating_model=None,
    trader_margin_pct=None,
    farm_margin_pct=None,
):
    procurement_drivers = procurement_drivers if isinstance(procurement_drivers, dict) else {}
    inferred_yield_pct = max(0.01, _to_float(dressed_output_kg, 1.3) / max(0.1, _to_float(average_live_bird_weight_kg, 1.8))) * 100.0
    waterfall = build_procurement_cost_waterfall(
        live_bird_rate_per_kg=_procurement_driver_value(procurement_drivers, "live_bird_rate_per_kg", live_bird_rate),
        yield_pct=_procurement_driver_value(procurement_drivers, "yield_pct", yield_pct if yield_pct is not None else inferred_yield_pct),
        mortality_pct=_procurement_driver_value(procurement_drivers, "mortality_pct", mortality_pct if mortality_pct is not None else 0.0),
        processing_loss_pct=_procurement_driver_value(procurement_drivers, "processing_loss_pct", processing_loss_pct if processing_loss_pct is not None else 0.0),
        gt_distributor_margin_pct=_procurement_driver_value(procurement_drivers, "gt_distributor_margin_pct", gt_distributor_margin_pct if gt_distributor_margin_pct is not None else 0.0),
        packaging_cost_per_kg=_procurement_driver_value(procurement_drivers, "packaging_cost_per_kg", packaging_cost_per_kg),
        transport_cost_per_kg=_procurement_driver_value(procurement_drivers, "transport_cost_per_kg", transport_cost_per_kg if transport_cost_per_kg is not None else cold_chain_logistics_cost_per_kg),
        processing_cost_per_kg=processing_cost_per_kg,
        factory_overhead_per_kg=factory_overhead_per_kg,
        target_margin_pct=target_margin_pct,
        operating_model=operating_model,
        trader_margin_pct=trader_margin_pct,
        farm_margin_pct=farm_margin_pct,
    )
    rate = waterfall["live_bird_base_rate_per_kg"]
    raw_material_cost_per_kg = waterfall["raw_material_cost_per_finished_kg"]
    total_cost_per_kg = waterfall["total_delivered_cost_per_kg"]
    recommended_price = waterfall["recommended_delivered_price_per_kg"]
    return {
        "live_bird_rate": rate,
        "gt_distributor_margin_pct": waterfall["gt_distributor_margin_pct"],
        "dressed_yield_pct": waterfall["dressed_yield_pct"] / 100.0,
        "processing_loss_pct": waterfall["processing_loss_pct"],
        "effective_finished_goods_yield_pct": waterfall["effective_finished_goods_yield_pct"],
        "raw_material_cost_per_kg": raw_material_cost_per_kg,
        "processing_cost_per_kg": waterfall["processing_cost_per_kg"],
        "packaging_cost_per_kg": waterfall["packaging_cost_per_kg"],
        "cold_chain_logistics_cost_per_kg": waterfall["transport_cost_per_kg"],
        "factory_overhead_per_kg": waterfall["factory_overhead_per_kg"],
        "total_cost_per_kg": total_cost_per_kg,
        "recommended_selling_price_per_kg": recommended_price,
        "contract_rate_per_kg": recommended_price,
        "horeca_contract_revenue": recommended_price * _to_float(contract_volume_kg_month, 0.0),
        "institutional_contract_revenue": recommended_price * _to_float(awarded_volume_kg_month, 0.0),
        "institutional_pack_size_kg": institutional_pack_size_kg,
        "cost_waterfall": waterfall,
    }


def _required_count(revenue, capacity):
    return math.ceil(max(0.0, _to_float(revenue, 0.0)) / max(1.0, _to_float(capacity, 1.0)))


def build_distributor_output(market_revenue=0.0, product_mix=None, fresh_revenue_per_distributor=25000000.0, frozen_revenue_per_distributor=18000000.0, rte_revenue_per_distributor=15000000.0, fresh_distributor_enabled=True, shared_frozen_rte_distributor=True):
    fresh_share = _mix_share(product_mix, "fresh", 0.5)
    frozen_share = _mix_share(product_mix, "frozen", 0.3)
    rte_share = _mix_share(product_mix, "rte", 0.2)
    fva_share = _mix_share(product_mix, "fva", 0.0)

    revenue_total = _to_float(market_revenue, 0.0)
    fresh_revenue = revenue_total * fresh_share
    frozen_raw_revenue = _to_float(market_revenue, 0.0) * frozen_share
    rte_revenue = _to_float(market_revenue, 0.0) * rte_share
    fva_revenue = _to_float(market_revenue, 0.0) * fva_share
    frozen_raw_distributors = _required_count(frozen_raw_revenue, frozen_revenue_per_distributor)
    rte_distributors = _required_count(rte_revenue, rte_revenue_per_distributor)
    fva_distributors = _required_count(fva_revenue, rte_revenue_per_distributor)
    shared = max(frozen_raw_distributors, rte_distributors) if shared_frozen_rte_distributor else 0
    frozen_capacity = frozen_raw_distributors * _to_float(frozen_revenue_per_distributor, 1.0)
    rte_capacity = rte_distributors * _to_float(rte_revenue_per_distributor, 1.0)
    fva_capacity = fva_distributors * _to_float(rte_revenue_per_distributor, 1.0)
    shared_capacity = shared * max(_to_float(frozen_revenue_per_distributor, 1.0), _to_float(rte_revenue_per_distributor, 1.0))
    fresh_distributors = _required_count(fresh_revenue, fresh_revenue_per_distributor) if fresh_distributor_enabled else 0
    def util(revenue, capacity):
        return revenue / capacity * 100.0 if capacity > 0 else 0.0
    def status(pct):
        return "Additional Partner Required" if pct > 100 else "Near Capacity" if pct > 85 else "Healthy"
    frozen_util = util(frozen_raw_revenue, frozen_capacity)
    rte_util = util(rte_revenue, rte_capacity)
    fva_util = util(fva_revenue, fva_capacity)
    shared_util = util(frozen_raw_revenue + rte_revenue, shared_capacity)
    total_product_revenue = fresh_revenue + frozen_raw_revenue + rte_revenue + fva_revenue
    product_revenue_variance = total_product_revenue - revenue_total
    product_revenue_reconciled = abs(product_revenue_variance) <= 0.01
    return {
        "fresh_chilled_revenue": fresh_revenue,
        "fresh_revenue": fresh_revenue,
        "fresh_distributors": fresh_distributors,
        "fresh_revenue_capacity_per_distributor": _to_float(fresh_revenue_per_distributor, 0.0),
        "fresh_network_capacity": fresh_distributors * _to_float(fresh_revenue_per_distributor, 1.0),
        "fresh_utilization_pct": util(fresh_revenue, fresh_distributors * _to_float(fresh_revenue_per_distributor, 1.0)),
        "fresh_capacity_status": status(util(fresh_revenue, fresh_distributors * _to_float(fresh_revenue_per_distributor, 1.0))),
        "frozen_raw_revenue": frozen_raw_revenue,
        "frozen_raw_distributors": frozen_raw_distributors,
        "frozen_revenue_capacity_per_distributor": _to_float(frozen_revenue_per_distributor, 0.0),
        "frozen_network_capacity": frozen_capacity,
        "frozen_utilization_pct": frozen_util,
        "frozen_capacity_status": status(frozen_util),
        "rte_revenue": rte_revenue,
        "rte_distributors": rte_distributors,
        "rte_revenue_capacity_per_distributor": _to_float(rte_revenue_per_distributor, 0.0),
        "rte_network_capacity": rte_capacity,
        "rte_utilization_pct": rte_util,
        "rte_capacity_status": status(rte_util),
        "fva_revenue": fva_revenue,
        "fva_distributors": fva_distributors,
        "fva_revenue_capacity_per_distributor": _to_float(rte_revenue_per_distributor, 0.0),
        "fva_network_capacity": fva_capacity,
        "fva_utilization_pct": fva_util,
        "fva_capacity_status": status(fva_util),
        "shared_frozen_rte_revenue": frozen_raw_revenue + rte_revenue,
        "shared_frozen_rte_revenue_served": frozen_raw_revenue + rte_revenue,
        "shared_frozen_rte_distributors": shared,
        "shared_frozen_rte_revenue_per_distributor": max(_to_float(frozen_revenue_per_distributor, 0.0), _to_float(rte_revenue_per_distributor, 0.0)),
        "shared_network_capacity": shared_capacity,
        "shared_utilization_pct": shared_util,
        "shared_frozen_rte_capacity_status": status(shared_util),
        "shared_network_is_consolidated_view": True,
        "total_product_revenue": total_product_revenue,
        "product_revenue_variance": product_revenue_variance,
        "product_revenue_reconciled": product_revenue_reconciled,
        "total_distributors": fresh_distributors + (shared if shared_frozen_rte_distributor else frozen_raw_distributors + rte_distributors),
    }


def build_channel_sales_output(market_revenue=0.0, channel_mix=None, working_days=25, gt_revenue_per_sales_executive=6000000.0, gt_outlets_per_sales_executive=120, gt_sales_executives_per_asm=6, mt_revenue_per_kam=12000000.0, quick_commerce_revenue_per_kam=10000000.0, horeca_revenue_per_sales_executive=6000000.0, institution_revenue_per_account_manager=10000000.0, calls_per_sales_executive_day=20, distributor_output=None, business_stage=None, live_bird_rate=120.0, horeca_revenue_mode="CONTRACT", horeca_contract_rate_per_kg=None, horeca_contract_volume_kg_month=0.0, horeca_active_accounts=0, horeca_credit_days=30, institutional_revenue_mode="CONTRACT", institutional_contract_rate_per_kg=None, institutional_awarded_volume_kg_month=0.0, institutional_contract_name="", institutional_contract_start_date="", institutional_contract_end_date="", revenue_mode="PLANNING", procurement_drivers=None, operating_model=None):
    revenue = _to_float(market_revenue, 0.0)
    shares = {
        "gt": _mix_share(channel_mix, "gt", 0.35),
        "mt": _mix_share(channel_mix, "mt", 0.15),
        "qcom": _mix_share(channel_mix, "qcom", 0.15),
        "ecommerce": _mix_share(channel_mix, "ecommerce", 0.05),
        "horeca": _mix_share(channel_mix, "horeca", 0.15),
        "institution": _mix_share(channel_mix, "institution", 0.10),
        "exports": _mix_share(channel_mix, "exports", 0.05),
    }
    total_share = sum(shares.values()) or 1.0
    shares = {k: v / total_share for k, v in shares.items()}
    pricing = build_contract_pricing_output(live_bird_rate=live_bird_rate, procurement_drivers=procurement_drivers, operating_model=operating_model)
    horeca_rate = _to_float(horeca_contract_rate_per_kg, pricing["recommended_selling_price_per_kg"])
    inst_rate = _to_float(institutional_contract_rate_per_kg, pricing["recommended_selling_price_per_kg"])
    horeca_mix_revenue = revenue * shares["horeca"]
    inst_mix_revenue = revenue * shares["institution"]
    planning_mode = str(revenue_mode or "PLANNING").upper() == "PLANNING"
    horeca_revenue = horeca_mix_revenue if planning_mode else horeca_rate * _to_float(horeca_contract_volume_kg_month, 0.0) if horeca_revenue_mode == "CONTRACT" else horeca_mix_revenue
    inst_revenue = inst_mix_revenue if planning_mode else inst_rate * _to_float(institutional_awarded_volume_kg_month, 0.0) if institutional_revenue_mode == "CONTRACT" else inst_mix_revenue
    contract_total = horeca_revenue + inst_revenue
    residual = max(0.0, revenue - contract_total)
    residual_shares = {k: v for k, v in shares.items() if k not in {"horeca", "institution"}}
    residual_total = sum(residual_shares.values()) or 1.0
    gt_revenue = residual * residual_shares["gt"] / residual_total
    mt_revenue = residual * residual_shares["mt"] / residual_total
    qcom_revenue = residual * residual_shares["qcom"] / residual_total
    ecommerce_revenue = residual * residual_shares["ecommerce"] / residual_total
    exports_revenue = residual * residual_shares["exports"] / residual_total
    total_commercial_revenue = gt_revenue + mt_revenue + qcom_revenue + ecommerce_revenue + horeca_revenue + inst_revenue + exports_revenue
    gap = revenue - total_commercial_revenue
    gt_hc = max(1, _required_count(gt_revenue, gt_revenue_per_sales_executive))
    mt_hc = _required_count(mt_revenue, mt_revenue_per_kam)
    qcom_hc = _required_count(qcom_revenue, quick_commerce_revenue_per_kam)
    horeca_hc = max(1 if horeca_revenue > 0 else 0, _required_count(horeca_revenue, horeca_revenue_per_sales_executive))
    inst_hc = 1 if inst_revenue > 0 else 0
    sales_manager = 1
    sales_coordinator = 1 if revenue > 100000000 else 0
    ecommerce_hc = 0
    exports_hc = 0
    commercial_hc_sum = sales_manager + gt_hc + mt_hc + qcom_hc + ecommerce_hc + horeca_hc + inst_hc + exports_hc
    commercial_hc_reported = commercial_hc_sum
    commercial_hc_variance = commercial_hc_reported - commercial_hc_sum
    commercial_hc_reconciled = commercial_hc_variance == 0
    total_hc = commercial_hc_sum
    gt_outlets = gt_hc * int(_to_float(gt_outlets_per_sales_executive, 120))
    gt_calls_day = gt_hc * _to_float(calls_per_sales_executive_day, 20)
    gt_supported_revenue = gt_hc * _to_float(gt_revenue_per_sales_executive, 1.0)
    qcom_platforms = 0 if qcom_revenue <= 0 else min(7, max(3, math.ceil(qcom_revenue / max(1.0, _to_float(quick_commerce_revenue_per_kam, 10000000.0)))))
    qcom_buying_accounts = qcom_platforms
    qcom_buying_regions = 0 if qcom_revenue <= 0 else max(1, min(8, qcom_platforms * 2))
    qcom_dark_stores = 0 if qcom_revenue <= 0 else qcom_buying_regions * 12
    qcom_avg_realization = 240.0
    qcom_monthly_volume_kg = qcom_revenue / qcom_avg_realization if qcom_avg_realization else 0.0
    active_distributors = None
    required_distributors = _required_count(gt_revenue, (distributor_output or {}).get("fresh_revenue_capacity_per_distributor", 4000000.0) if isinstance(distributor_output, dict) else 4000000.0)
    outlets_per_distributor = max(1, math.ceil(gt_outlets / max(1, required_distributors))) if gt_outlets else 0
    coverage_gap = None if active_distributors is None else max(0, required_distributors - active_distributors)
    coverage_status = "Planning Requirement" if active_distributors is None else "Coverage Gap" if coverage_gap else "Covered"
    horeca_obj = {**pricing, "live_bird_rate": _live_bird_rate(live_bird_rate), "average_live_bird_weight_kg": 1.8, "dressed_output_kg": 1.3, "dressed_yield_pct": 1.3 / 1.8, "processing_cost_per_kg": 12.0, "packaging_cost_per_kg": 8.0, "cold_chain_logistics_cost_per_kg": 6.0, "factory_overhead_per_kg": 5.0, "target_margin_pct": 18.0, "actual_margin_pct": 18.0, "pricing_status": "Planning Rate", "revenue": horeca_revenue, "planned_revenue": horeca_revenue, "revenue_mode": "PLANNING" if planning_mode else horeca_revenue_mode, "contract_rate_per_kg": horeca_rate, "required_volume_kg_month": horeca_revenue / max(1.0, horeca_rate), "active_accounts": int(_to_float(horeca_active_accounts, max(1, horeca_hc * 8))), "accounts": int(_to_float(horeca_active_accounts, max(1, horeca_hc * 8))), "required_hc": horeca_hc, "sales_executives": horeca_hc, "revenue_per_sales_executive": _to_float(horeca_revenue_per_sales_executive, 1.0), "credit_days": horeca_credit_days, "reconciliation_variance": horeca_revenue - horeca_mix_revenue}
    institutional_obj = {**pricing, "live_bird_rate": _live_bird_rate(live_bird_rate), "average_live_bird_weight_kg": 1.8, "dressed_output_kg": 1.3, "dressed_yield_pct": 1.3 / 1.8, "processing_cost_per_kg": 12.0, "packaging_cost_per_kg": 8.0, "cold_chain_logistics_cost_per_kg": 6.0, "factory_overhead_per_kg": 5.0, "target_margin_pct": 18.0, "actual_margin_pct": 18.0, "pricing_status": "Planning Rate", "revenue": inst_revenue, "planned_revenue": inst_revenue, "revenue_mode": "PLANNING" if planning_mode else institutional_revenue_mode, "product": "Curry Cut", "pack_size_kg": 2.0, "pack_type": "Institutional Pack", "mrp": "No MRP", "contract_rate_per_kg": inst_rate, "contract_value_per_pack": inst_rate * 2.0, "required_volume_kg_month": inst_revenue / max(1.0, inst_rate), "required_packs_month": inst_revenue / max(1.0, inst_rate) / 2.0, "institutional_required_packs_month": inst_revenue / max(1.0, inst_rate) / 2.0, "active_tenders_contracts": 1 if inst_revenue else 0, "accounts": 1 if inst_revenue else 0, "required_hc": inst_hc, "account_managers": inst_hc, "sales_executives": inst_hc, "contract_name": institutional_contract_name, "contract_start_date": institutional_contract_start_date, "contract_end_date": institutional_contract_end_date, "reconciliation_variance": inst_revenue - inst_mix_revenue}
    return {
        "selected_market_revenue": revenue,
        "contract_revenue_total": contract_total,
        "residual_revenue": residual,
        "gt_revenue": gt_revenue,
        "mt_revenue": mt_revenue,
        "qcom_revenue": qcom_revenue,
        "ecommerce_revenue": ecommerce_revenue,
        "horeca_revenue": horeca_revenue,
        "institutional_government_revenue": inst_revenue,
        "exports_revenue": exports_revenue,
        "total_commercial_revenue": total_commercial_revenue,
        "reconciliation_gap": gap,
        "reconciliation_warning": "" if abs(gap) <= 1 else f"Revenue Reconciliation Gap: {gap:,.0f}",
        "sales_manager": sales_manager,
        "head_sales_hc": sales_manager,
        "gt_sales_executives": gt_hc,
        "general_trade_hc": gt_hc,
        "mt_kam": mt_hc,
        "modern_trade_hc": mt_hc,
        "qcom_kam": qcom_hc,
        "quick_commerce_hc": qcom_hc,
        "ecommerce_hc": ecommerce_hc,
        "e_commerce_hc": ecommerce_hc,
        "ecommerce_kam": ecommerce_hc,
        "exports_hc": exports_hc,
        "export_hc": exports_hc,
        "exports_manager": exports_hc,
        "horeca_sales_hc": horeca_hc,
        "horeca_hc": horeca_hc,
        "institution_government_manager": inst_hc,
        "institutional_hc": inst_hc,
        "institutional_government_manager": inst_hc,
        "sales_coordinator": sales_coordinator,
        "sales_coordinator_mis": sales_coordinator,
        "commercial_hc_sum": commercial_hc_sum,
        "commercial_hc_reported": commercial_hc_reported,
        "commercial_hc_variance": commercial_hc_variance,
        "commercial_hc_reconciled": commercial_hc_reconciled,
        "total_commercial_hc": total_hc,
        "total_sales_hc": total_hc,
        "general_trade": {
            "revenue": gt_revenue,
            "required_distributors": required_distributors,
            "active_distributors": active_distributors,
            "target_outlets": gt_outlets,
            "outlets_per_distributor": outlets_per_distributor,
            "coverage_gap_distributors": coverage_gap,
            "coverage_status": coverage_status,
            "sales_executives": gt_hc,
            "revenue_per_sales_executive": _to_float(gt_revenue_per_sales_executive, 1.0),
            "outlets": gt_outlets,
            "outlets_per_sales_executive": _to_float(gt_outlets_per_sales_executive, 120),
            "beats": max(1, math.ceil(gt_outlets / max(1.0, _to_float(calls_per_sales_executive_day, 20) * 6))),
            "calls_day": gt_calls_day,
            "calls_per_day": gt_calls_day,
            "calls_per_sales_executive_day": _to_float(calls_per_sales_executive_day, 20),
            "supported_revenue": gt_supported_revenue,
            "revenue_at_risk": max(0.0, gt_revenue - gt_supported_revenue),
        },
        "modern_trade": {"revenue": mt_revenue, "accounts": max(1, mt_hc * 4) if mt_revenue else 0, "kam": mt_hc},
        "quick_commerce": {
            "revenue": qcom_revenue,
            "active_platforms": qcom_platforms,
            "platforms": qcom_platforms,
            "buying_accounts": qcom_buying_accounts,
            "buying_regions": qcom_buying_regions,
            "dark_stores_served": qcom_dark_stores,
            "dark_stores": qcom_dark_stores,
            "monthly_volume_kg": qcom_monthly_volume_kg,
            "kam": qcom_hc,
            "required_kam": qcom_hc,
            "average_revenue_per_platform": qcom_revenue / qcom_platforms if qcom_platforms else 0.0,
            "average_volume_per_platform": qcom_monthly_volume_kg / qcom_platforms if qcom_platforms else 0.0,
        },
        "horeca": horeca_obj,
        "institution": institutional_obj,
        "institutional_government": institutional_obj,
    }


def build_product_metrics(product_mix, product_registry=None):
    return {"weighted_yield_pct": 72.0}


def build_channel_metrics(channel_mix, channel_registry=None):
    return {}


def build_financial_chain(product_mix=None, channel_mix=None, product_registry=None, channel_registry=None, pricing_registry=None, cost_registry=None, revenue_rupees=0.0, avg_bird_weight=1.8, working_days=25, stage_profile=None, market_distance_km=0.0, region=None, live_bird_rate=None, yield_pct=None, avg_birds_per_trader=5000, avg_birds_per_farm=25000, plant_capacity_per_line_mt_day=10.0, working_hours_per_shift=8.0, max_shifts=3, cold_storage_buffer_days=3, utilization_threshold_pct=85.0, operating_model=None, business_stage=None, procurement_drivers=None, mortality_pct=None, processing_loss_pct=None, gt_distributor_margin_pct=None, packaging_cost_per_kg=None, transport_cost_per_kg=None, trader_margin_pct=None, farm_margin_pct=None):
    revenue = _to_float(revenue_rupees, 0.0)
    channel_product_volume_output = build_channel_product_volume_output(
        revenue,
        product_mix=product_mix,
        channel_mix=channel_mix,
        product_registry=product_registry,
        pricing_registry=pricing_registry,
        working_days=working_days,
    )
    weighted_selling_price = channel_product_volume_output["weighted_selling_price"]
    finished_goods_kg = channel_product_volume_output["total_planned_finished_goods_kg_month"]
    processing_cost_per_kg = _value_from_cost_registry(cost_registry, "processing_cost_per_kg", 12.0)
    factory_overhead_per_kg = _value_from_cost_registry(cost_registry, "factory_overhead_per_kg", 5.0)
    target_margin_pct = _value_from_cost_registry(cost_registry, "target_margin_pct", 18.0)
    waterfall = build_procurement_cost_waterfall(
        live_bird_rate_per_kg=_procurement_driver_value(procurement_drivers, "live_bird_rate_per_kg", live_bird_rate if live_bird_rate is not None else _value_from_cost_registry(cost_registry, "live_bird_rate", 120.0)),
        yield_pct=_procurement_driver_value(procurement_drivers, "yield_pct", yield_pct if yield_pct is not None else channel_product_volume_output["weighted_yield_pct"]),
        mortality_pct=_procurement_driver_value(procurement_drivers, "mortality_pct", mortality_pct if mortality_pct is not None else 2.0),
        processing_loss_pct=_procurement_driver_value(procurement_drivers, "processing_loss_pct", processing_loss_pct if processing_loss_pct is not None else 3.0),
        gt_distributor_margin_pct=_procurement_driver_value(procurement_drivers, "gt_distributor_margin_pct", gt_distributor_margin_pct if gt_distributor_margin_pct is not None else 6.0),
        packaging_cost_per_kg=_procurement_driver_value(procurement_drivers, "packaging_cost_per_kg", packaging_cost_per_kg if packaging_cost_per_kg is not None else _value_from_cost_registry(cost_registry, "packaging_cost_per_kg", 8.0)),
        transport_cost_per_kg=_procurement_driver_value(procurement_drivers, "transport_cost_per_kg", transport_cost_per_kg if transport_cost_per_kg is not None else _value_from_cost_registry(cost_registry, "transport_cost_per_kg", 0.0)),
        processing_cost_per_kg=processing_cost_per_kg,
        factory_overhead_per_kg=factory_overhead_per_kg,
        target_margin_pct=target_margin_pct,
        operating_model=operating_model,
        trader_margin_pct=trader_margin_pct,
        farm_margin_pct=farm_margin_pct,
    )
    weighted_yield = waterfall["effective_finished_goods_yield_pct"] / 100.0
    dressed_yield = waterfall["dressed_yield_pct"] / 100.0
    survival_rate = waterfall["survival_rate_pct"] / 100.0
    net_live_bird_kg = finished_goods_kg / max(0.01, weighted_yield)
    live_bird_kg = net_live_bird_kg / max(0.01, survival_rate)
    net_birds_required = net_live_bird_kg / max(0.1, _to_float(avg_bird_weight, 1.8))
    birds_required = live_bird_kg / max(0.1, _to_float(avg_bird_weight, 1.8))
    wd = max(1, int(_to_float(working_days, 25)))
    birds_per_day = birds_required / wd
    rate = waterfall["live_bird_rate_per_kg"]
    bird_procurement_cost = live_bird_kg * rate
    processing_expense = finished_goods_kg * waterfall["processing_cost_per_kg"]
    packaging_expense = finished_goods_kg * waterfall["packaging_cost_per_kg"]
    transport_expense = finished_goods_kg * waterfall["transport_cost_per_kg"]
    factory_overhead_expense = finished_goods_kg * waterfall["factory_overhead_per_kg"]
    other_direct_variable_spend = 0.0
    total_direct_variable_spend = bird_procurement_cost + processing_expense + packaging_expense + transport_expense + other_direct_variable_spend
    marketing_cost = revenue * _to_float((stage_profile or {}).get("marketing_pct", 0.04) if isinstance(stage_profile, dict) else 0.04, 0.04)
    warehouse_opex = finished_goods_kg * 3.0
    gross_contribution = revenue - total_direct_variable_spend
    ebitda = gross_contribution - marketing_cost - warehouse_opex
    pat = ebitda * 0.75
    raw = {
        "revenue_rupees": revenue,
        "weighted_selling_price": weighted_selling_price,
        "finished_goods_kg": finished_goods_kg,
        "finished_goods_mt_day": finished_goods_kg / wd / 1000.0,
        "live_bird_kg": live_bird_kg,
        "net_live_bird_kg": net_live_bird_kg,
        "live_weight_kg_day": live_bird_kg / wd,
        "net_birds_required": net_birds_required,
        "birds_required": birds_required,
        "birds_per_day": birds_per_day,
        "working_days": wd,
        "weighted_yield": weighted_yield,
        "dressed_yield": dressed_yield,
        "yield_pct": weighted_yield * 100.0,
        "dressed_yield_pct": waterfall["dressed_yield_pct"],
        "processing_loss_pct": waterfall["processing_loss_pct"],
        "effective_finished_goods_yield_pct": waterfall["effective_finished_goods_yield_pct"],
        "mortality_pct": waterfall["mortality_pct"],
        "survival_rate_pct": waterfall["survival_rate_pct"],
        "avg_bird_weight": _to_float(avg_bird_weight, 1.8),
        "live_bird_rate": rate,
        "live_bird_base_rate_per_kg": waterfall["live_bird_base_rate_per_kg"],
        "gt_distributor_margin_pct": waterfall["gt_distributor_margin_pct"],
        "bird_procurement_cost": bird_procurement_cost,
        "live_bird_procurement_spend_month": bird_procurement_cost,
        "processing_spend_month": processing_expense,
        "packaging_spend_month": packaging_expense,
        "transport_spend_month": transport_expense,
        "other_direct_variable_spend_month": other_direct_variable_spend,
        "total_direct_variable_spend_month": total_direct_variable_spend,
        "cost_waterfall": waterfall,
        "raw_material_cost_per_finished_kg": waterfall["raw_material_cost_per_finished_kg"],
        "total_ex_factory_cost_per_kg": waterfall["total_ex_factory_cost_per_kg"],
        "total_delivered_cost_per_kg": waterfall["total_delivered_cost_per_kg"],
        "recommended_ex_factory_price_per_kg": waterfall["recommended_ex_factory_price_per_kg"],
        "recommended_delivered_price_per_kg": waterfall["recommended_delivered_price_per_kg"],
        "procurement_driver_impact_map": PROCUREMENT_DRIVER_IMPACT_MAP,
        "channel_product_volume_output": channel_product_volume_output,
        "total_planned_finished_goods_kg_month": channel_product_volume_output["total_planned_finished_goods_kg_month"],
        "total_planned_finished_goods_mt_month": channel_product_volume_output["total_planned_finished_goods_mt_month"],
        "total_planned_finished_goods_kg_day": channel_product_volume_output["total_planned_finished_goods_kg_day"],
        "total_planned_finished_goods_mt_day": channel_product_volume_output["total_planned_finished_goods_mt_day"],
    }
    plant = build_plant_capacity_output(
        raw,
        plant_capacity_per_line_mt_day,
        working_hours_per_shift,
        max_shifts,
        cold_storage_buffer_days,
        utilization_threshold_pct,
    )
    manpower = build_manpower_output(raw, plant, channel_mix, operating_model, business_stage, stage_profile, revenue)
    return {
        "revenue": revenue,
        "revenue_rupees": revenue,
        "weighted_selling_price": weighted_selling_price,
        "weighted_yield": weighted_yield,
        "dressed_yield": dressed_yield,
        "dressed_yield_pct": waterfall["dressed_yield_pct"],
        "processing_loss_pct": waterfall["processing_loss_pct"],
        "effective_finished_goods_yield_pct": waterfall["effective_finished_goods_yield_pct"],
        "mortality_pct": waterfall["mortality_pct"],
        "finished_goods_kg": finished_goods_kg,
        "channel_product_volume_output": channel_product_volume_output,
        "total_planned_finished_goods_kg_month": channel_product_volume_output["total_planned_finished_goods_kg_month"],
        "total_planned_finished_goods_mt_month": channel_product_volume_output["total_planned_finished_goods_mt_month"],
        "total_planned_finished_goods_kg_day": channel_product_volume_output["total_planned_finished_goods_kg_day"],
        "total_planned_finished_goods_mt_day": channel_product_volume_output["total_planned_finished_goods_mt_day"],
        "live_bird_kg": live_bird_kg,
        "net_live_bird_kg": net_live_bird_kg,
        "net_birds_required": net_birds_required,
        "birds_required": birds_required,
        "birds_per_day": birds_per_day,
        "traders_required": max(1, math.ceil(birds_required / max(1, _to_float(avg_birds_per_trader, 5000)))),
        "farms_required": max(1, math.ceil(birds_required / max(1, _to_float(avg_birds_per_farm, 25000)))),
        "bird_procurement_cost": bird_procurement_cost,
        "live_bird_procurement_spend_month": bird_procurement_cost,
        "processing_expense": processing_expense,
        "processing_spend_month": processing_expense,
        "packaging_expense": packaging_expense,
        "packaging_spend_month": packaging_expense,
        "transport_expense": transport_expense,
        "transport_spend_month": transport_expense,
        "other_direct_variable_spend_month": other_direct_variable_spend,
        "other_direct_variable_spend": other_direct_variable_spend,
        "factory_overhead_expense": factory_overhead_expense,
        "total_direct_variable_spend_month": total_direct_variable_spend,
        "cost_waterfall": waterfall,
        "raw_material_cost_per_finished_kg": waterfall["raw_material_cost_per_finished_kg"],
        "total_ex_factory_cost_per_kg": waterfall["total_ex_factory_cost_per_kg"],
        "total_delivered_cost_per_kg": waterfall["total_delivered_cost_per_kg"],
        "recommended_ex_factory_price_per_kg": waterfall["recommended_ex_factory_price_per_kg"],
        "recommended_delivered_price_per_kg": waterfall["recommended_delivered_price_per_kg"],
        "procurement_driver_impact_map": PROCUREMENT_DRIVER_IMPACT_MAP,
        "gross_contribution": gross_contribution,
        "marketing_cost": marketing_cost,
        "warehouse_opex": warehouse_opex,
        "ebitda": ebitda,
        "pat": pat,
        "working_capital": revenue * 0.20,
        "warehouse_need": finished_goods_kg / 1000.0 * 0.2,
        "distribution_centre_need": max(1, math.ceil(finished_goods_kg / 100000.0)),
        "raw_material_output": raw,
        "plant_capacity_output": plant,
        "manpower_output": manpower,
        "channel_product_volume_output": channel_product_volume_output,
    }


def build_plant_planning(plant=None, assigned_markets=None, product_mix=None, channel_mix=None, product_registry=None, channel_registry=None, pricing_registry=None, cost_registry=None, avg_bird_weight=1.8, working_days=25, stage_profile=None, live_bird_rate=None, yield_pct=None, operating_model=None, business_stage=None, utilization_threshold_pct=85.0, plant_capacity_per_line_mt_day=10.0, working_hours_per_shift=8.0, max_shifts=3, cold_storage_buffer_days=3, procurement_drivers=None, mortality_pct=None, processing_loss_pct=None, gt_distributor_margin_pct=None, packaging_cost_per_kg=None, transport_cost_per_kg=None, trader_margin_pct=None, farm_margin_pct=None, manpower=_UNSET):
    assigned_revenue = 0.0
    if assigned_markets is not None and not getattr(assigned_markets, "empty", True):
        for col in ("revenue_allocation_cr", "monthly_revenue", "revenue", "assigned_market_revenue", "target_revenue"):
            if col in assigned_markets.columns:
                assigned_revenue = float(assigned_markets[col].apply(lambda v: _to_float(v, 0.0)).sum())
                if col == "revenue_allocation_cr":
                    assigned_revenue *= 10_000_000
                break
    if assigned_revenue <= 0:
        assigned_revenue = _to_float((stage_profile or {}).get("revenue_rupees", 60000000.0) if isinstance(stage_profile, dict) else 60000000.0, 60000000.0)
    plant_data = _normalize_mapping(plant)

    raw_line_capacity = plant_data.get("line_capacity_mt_day", plant_data.get("base_capacity_per_line", plant_capacity_per_line_mt_day))
    line_capacity_mt_day = _to_float(raw_line_capacity, plant_capacity_per_line_mt_day)

    raw_maximum_shifts = plant_data.get("maximum_shifts_per_line", plant_data.get("maximum_shifts", max_shifts))
    maximum_shifts_per_line = max(1, int(round(_to_float(raw_maximum_shifts, max_shifts))))

    raw_current_installed_capacity = plant_data.get(
        "current_installed_capacity_mt_day",
        plant_data.get("installed_capacity_mt_day", line_capacity_mt_day),
    )
    current_installed_capacity_mt_day = _to_float(raw_current_installed_capacity, line_capacity_mt_day)

    raw_installed_lines = plant_data.get("installed_lines", None)
    if raw_installed_lines is None:
        configured_installed_lines = max(1, int(round(current_installed_capacity_mt_day / max(0.1, line_capacity_mt_day))))
    else:
        configured_installed_lines = max(1, int(round(_to_float(raw_installed_lines, 1.0))))

    raw_active_shifts = plant_data.get("active_shifts", 1)
    configured_active_shifts = max(1, int(round(_to_float(raw_active_shifts, 1.0))))

    raw_maximum_lines = plant_data.get("maximum_lines_in_current_plant", plant_data.get("max_lines_in_current_plant", None))
    if raw_maximum_lines is None:
        maximum_lines_in_current_plant = max(configured_installed_lines + 1, configured_installed_lines)
    else:
        maximum_lines_in_current_plant = max(configured_installed_lines, int(round(_to_float(raw_maximum_lines, configured_installed_lines + 1))))

    raw_site_expandable = plant_data.get("site_expandable", plant_data.get("existing_plant_expandable", "Yes"))
    expandable_flag = str(raw_site_expandable).strip().lower() not in {"no", "false", "0"}

    result = build_financial_chain(product_mix, channel_mix, product_registry, channel_registry, pricing_registry, cost_registry, assigned_revenue, avg_bird_weight, working_days, stage_profile, live_bird_rate=live_bird_rate, yield_pct=yield_pct, plant_capacity_per_line_mt_day=line_capacity_mt_day, working_hours_per_shift=working_hours_per_shift, max_shifts=maximum_shifts_per_line, cold_storage_buffer_days=cold_storage_buffer_days, utilization_threshold_pct=utilization_threshold_pct, operating_model=operating_model, business_stage=business_stage, procurement_drivers=procurement_drivers, mortality_pct=mortality_pct, processing_loss_pct=processing_loss_pct, gt_distributor_margin_pct=gt_distributor_margin_pct, packaging_cost_per_kg=packaging_cost_per_kg, transport_cost_per_kg=transport_cost_per_kg, trader_margin_pct=trader_margin_pct, farm_margin_pct=farm_margin_pct)
    result["plant_capacity_output"] = build_plant_capacity_output(
        result.get("raw_material_output", {}),
        capacity_per_line_mt_day=line_capacity_mt_day,
        working_hours_per_shift=working_hours_per_shift,
        max_shifts=maximum_shifts_per_line,
        cold_storage_buffer_days=cold_storage_buffer_days,
        utilization_threshold_pct=utilization_threshold_pct,
        installed_lines=configured_installed_lines,
        active_shifts=configured_active_shifts,
        maximum_lines_in_current_plant=maximum_lines_in_current_plant,
        safe_utilization_pct=85.0,
        review_utilization_pct=90.0,
        critical_utilization_pct=95.0,
        existing_plant_expandable=expandable_flag,
        expansion_line_increment=1,
    )
    if manpower is _UNSET:
        manpower_data = _normalize_mapping(result.get("manpower_output", {}))
    else:
        manpower_data = _normalize_mapping(manpower)
    result["manpower_output"] = manpower_data
    result["assigned_market_revenue"] = assigned_revenue
    return result


def build_reverse_planning(results, base_revenue, sales_team, production_workers, warehouse_team, marketing_team, cold_storage_capacity, production_lines):
    return {}


def build_ceo_recommendation(results, selected_market_name):
    return "Review the current plan against revenue, capacity, procurement and manpower signals."


def build_explainability(kpi_name, results, selected_market_name):
    return {"title": kpi_name, "summary": f"{kpi_name} is calculated from the selected market plan for {selected_market_name}."}
