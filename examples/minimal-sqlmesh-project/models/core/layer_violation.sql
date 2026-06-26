MODEL (
  name sqlmesh_example.layer_violation,
  kind FULL,
  owner 'core_team',
  description 'Violates layer integrity by depending on marts',
  grain user_id
);

SELECT
  user_id
FROM sqlmesh_example.finance_stats;
