-- stg_participant is extracted/cleaned in Python; dimensional loading and
-- wide-to-long transformation are SQL. Keys are deterministic for a snapshot.
INSERT INTO dim_assignment VALUES (0,'Control'), (1,'AI offer');
INSERT INTO dim_period VALUES (1,'Baseline'), (2,'Post');
INSERT INTO dim_participant (source_participant_id, task_a_first)
SELECT prolific_pid, a_first FROM stg_participant ORDER BY prolific_pid;
INSERT INTO dim_occupation (occupation_name)
SELECT DISTINCT occupation FROM stg_participant ORDER BY occupation;
INSERT INTO dim_incentive (incentive_name, primary_arm)
SELECT DISTINCT incentive_arm, CASE WHEN incentive_arm IN ('linear','convex') THEN 1 ELSE 0 END
FROM stg_participant ORDER BY incentive_arm;

INSERT INTO fact_outcome
SELECT p.participant_key, 1, s.assignment, o.occupation_key, i.incentive_key,
       s.time_pre, s.grade_pre, s.page_pre
FROM stg_participant s
JOIN dim_participant p ON p.source_participant_id=s.prolific_pid
JOIN dim_occupation o ON o.occupation_name=s.occupation
JOIN dim_incentive i ON i.incentive_name=s.incentive_arm
UNION ALL
SELECT p.participant_key, 2, s.assignment, o.occupation_key, i.incentive_key,
       s.time_post, s.grade_post, s.page_post
FROM stg_participant s
JOIN dim_participant p ON p.source_participant_id=s.prolific_pid
JOIN dim_occupation o ON o.occupation_name=s.occupation
JOIN dim_incentive i ON i.incentive_name=s.incentive_arm;
INSERT INTO fact_usage
SELECT p.participant_key, s.used_ai, s.followup_used_ai
FROM stg_participant s JOIN dim_participant p ON p.source_participant_id=s.prolific_pid;

-- Pivot to one participant BEFORE joining the usage fact. Joining two
-- multirow facts directly would multiply measures; this pattern avoids it.
CREATE VIEW mart_participant AS
WITH paired AS (
    SELECT participant_key, assignment_key, occupation_key, incentive_key,
           MAX(CASE WHEN period_key=1 THEN completion_minutes END) AS time_pre,
           MAX(CASE WHEN period_key=2 THEN completion_minutes END) AS time_post,
           MAX(CASE WHEN period_key=1 THEN writing_rating END) AS grade_pre,
           MAX(CASE WHEN period_key=2 THEN writing_rating END) AS grade_post,
           MAX(CASE WHEN period_key=1 THEN page_minutes END) AS page_pre,
           MAX(CASE WHEN period_key=2 THEN page_minutes END) AS page_post
    FROM fact_outcome GROUP BY participant_key, assignment_key, occupation_key, incentive_key
)
SELECT p.source_participant_id AS prolific_pid, x.assignment_key AS assignment,
       o.occupation_name AS occupation, i.incentive_name AS incentive_arm,
       p.task_a_first AS a_first, i.primary_arm,
       x.time_pre, x.time_post, x.grade_pre, x.grade_post, x.page_pre, x.page_post,
       u.experimental_use AS used_ai, u.followup_use AS followup_used_ai
FROM paired x
JOIN dim_participant p ON p.participant_key=x.participant_key
JOIN dim_occupation o ON o.occupation_key=x.occupation_key
JOIN dim_incentive i ON i.incentive_key=x.incentive_key
JOIN fact_usage u ON u.participant_key=x.participant_key;

-- Compatibility view keeps the existing CTE/window/self-join analyses intact.
CREATE VIEW participants AS SELECT * FROM mart_participant;
CREATE VIEW mart_experiment_kpi AS
SELECT a.assignment_label, f.assignment_key AS assignment, o.occupation_name AS occupation,
       t.period_name, COUNT(*) AS participants,
       COUNT(completion_minutes) AS time_observations, AVG(completion_minutes) AS mean_minutes,
       COUNT(writing_rating) AS quality_observations, AVG(writing_rating) AS mean_quality
FROM fact_outcome f
JOIN dim_assignment a ON a.assignment_key=f.assignment_key
JOIN dim_occupation o ON o.occupation_key=f.occupation_key
JOIN dim_period t ON t.period_key=f.period_key
JOIN dim_incentive i ON i.incentive_key=f.incentive_key
WHERE i.primary_arm=1
GROUP BY f.assignment_key, a.assignment_label, o.occupation_name, t.period_name;
