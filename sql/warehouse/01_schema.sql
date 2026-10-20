-- Local analytical warehouse. Grain and uniqueness are enforced, not inferred.
PRAGMA foreign_keys = ON;
CREATE TABLE dim_participant (
    participant_key INTEGER PRIMARY KEY,
    source_participant_id TEXT NOT NULL UNIQUE,
    task_a_first INTEGER NOT NULL CHECK (task_a_first IN (0,1))
);
CREATE TABLE dim_assignment (
    assignment_key INTEGER PRIMARY KEY CHECK (assignment_key IN (0,1)),
    assignment_label TEXT NOT NULL UNIQUE
);
CREATE TABLE dim_occupation (
    occupation_key INTEGER PRIMARY KEY,
    occupation_name TEXT NOT NULL UNIQUE
);
CREATE TABLE dim_incentive (
    incentive_key INTEGER PRIMARY KEY,
    incentive_name TEXT NOT NULL UNIQUE,
    primary_arm INTEGER NOT NULL CHECK (primary_arm IN (0,1))
);
CREATE TABLE dim_period (
    period_key INTEGER PRIMARY KEY CHECK (period_key IN (1,2)),
    period_name TEXT NOT NULL UNIQUE
);
-- One retained participant x measurement period, including missing measurements.
CREATE TABLE fact_outcome (
    participant_key INTEGER NOT NULL REFERENCES dim_participant(participant_key),
    period_key INTEGER NOT NULL REFERENCES dim_period(period_key),
    assignment_key INTEGER NOT NULL REFERENCES dim_assignment(assignment_key),
    occupation_key INTEGER NOT NULL REFERENCES dim_occupation(occupation_key),
    incentive_key INTEGER NOT NULL REFERENCES dim_incentive(incentive_key),
    completion_minutes REAL CHECK (completion_minutes >= 0),
    writing_rating REAL CHECK (writing_rating BETWEEN 1 AND 7),
    page_minutes REAL CHECK (page_minutes >= 0),
    PRIMARY KEY (participant_key, period_key)
);
-- One retained participant, with nullable reported use indicators.
CREATE TABLE fact_usage (
    participant_key INTEGER PRIMARY KEY REFERENCES dim_participant(participant_key),
    experimental_use INTEGER CHECK (experimental_use IN (0,1)),
    followup_use INTEGER CHECK (followup_use IN (0,1))
);
CREATE INDEX outcome_by_assignment_period ON fact_outcome(assignment_key, period_key);
