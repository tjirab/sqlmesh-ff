MODEL (
  name sqlmesh_example.marketing_all_users,
  kind FULL,
  owner 'marketing_team',
  description 'All marketing users consolidated',
  grain user_id
);

SELECT
  u.user_id,
  u.user_name,
  f.revenue
FROM sqlmesh_example.users u
LEFT JOIN sqlmesh_example.finance_stats f
  ON u.user_id = f.user_id;
