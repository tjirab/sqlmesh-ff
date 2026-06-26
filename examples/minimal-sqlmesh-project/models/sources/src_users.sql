MODEL (
  name sqlmesh_example.src_users,
  kind FULL,
  owner 'data_team',
  description 'Staging users source table',
  grain user_id
);

SELECT
  CAST(1 AS VARCHAR) AS user_id,
  'Alice' AS user_name,
  '2026-06-25'::date AS created_date;
