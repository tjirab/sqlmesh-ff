MODEL (
  name sqlmesh_example.finance_stats,
  kind FULL,
  owner 'finance_team',
  description 'Core finance statistics',
  grain user_id
);

SELECT
  user_id,
  CAST(100.0 AS DOUBLE) AS revenue
FROM sqlmesh_example.users;
