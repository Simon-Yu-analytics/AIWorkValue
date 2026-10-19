-- Independently calculate three business cases from assumptions + estimated time effect.
-- Money is hypothetical capacity value, not cash savings. Inputs are not vendor quotes.
SELECT scenario, offered_seats, net_minutes, capacity_hours, gross_capacity_value,
       recurring_cost, net_capacity_value, operating_seat_cost_ceiling,
       capacity_payback_months, effect_only_value_low, effect_only_value_high
FROM v_business_value WHERE scenario_kind = 'named'
ORDER BY CASE scenario WHEN 'conservative' THEN 1 WHEN 'base' THEN 2 ELSE 3 END;
