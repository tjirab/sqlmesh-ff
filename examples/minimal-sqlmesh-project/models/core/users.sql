MODEL (
  name sqlmesh_example.users,
  kind FULL,
  description 'Core users table',
  grain user_id
);

SELECT
  *
FROM sqlmesh_example.src_users;
