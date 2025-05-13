-- Populate users
INSERT INTO users (name, email) VALUES
('Alice Johnson', 'alice.johnson@example.com'),
('Bob Smith', 'bob.smith@example.com'),
('Carol White', 'carol.white@example.com'),
('David Brown', 'david.brown@example.com');

-- Populate categories
INSERT INTO categories (name) VALUES
('PostgreSQL DBA'),
('Oracle DBA'),
('Backup Specialist'),
('Performance Tuning');

-- Assign users to categories
INSERT INTO user_categories (user_id, category_id) VALUES
((SELECT user_id FROM users WHERE name = 'Alice Johnson'), (SELECT category_id FROM categories WHERE name = 'PostgreSQL DBA')),
((SELECT user_id FROM users WHERE name = 'Bob Smith'), (SELECT category_id FROM categories WHERE name = 'Oracle DBA')),
((SELECT user_id FROM users WHERE name = 'Carol White'), (SELECT category_id FROM categories WHERE name = 'Backup Specialist')),
((SELECT user_id FROM users WHERE name = 'David Brown'), (SELECT category_id FROM categories WHERE name = 'Performance Tuning')),
((SELECT user_id FROM users WHERE name = 'Alice Johnson'), (SELECT category_id FROM categories WHERE name = 'Backup Specialist'));

-- Populate documents with metadata for the created markdown files
INSERT INTO document (title, description, version, status, effective_date, author_id, reviewer_id, category_id, file_path, format, file_size, page_count) VALUES
('PostgreSQL Best Practices for DBAs', 'Detailed best practices for PostgreSQL installation, configuration, performance tuning, backup, and updates.', '1.0', 'active', CURRENT_DATE - INTERVAL 30,
 (SELECT user_id FROM users WHERE name = 'Alice Johnson'),
 (SELECT user_id FROM users WHERE name = 'David Brown'),
 (SELECT category_id FROM categories WHERE name = 'PostgreSQL DBA'),
 'database_documents/PostgreSQL_Best_Practices.md', 'md', 10240, 25),

('Oracle Database Best Practices for DBAs', 'Detailed best practices for Oracle installation, configuration, performance tuning, backup, and updates.', '1.0', 'active', CURRENT_DATE - INTERVAL 30,
 (SELECT user_id FROM users WHERE name = 'Bob Smith'),
 (SELECT user_id FROM users WHERE name = 'David Brown'),
 (SELECT category_id FROM categories WHERE name = 'Oracle DBA'),
 'database_documents/Oracle_Best_Practices.md', 'md', 11264, 28),

('PostgreSQL 17 Installation Procedure on Debian', 'Step-by-step installation guide for PostgreSQL 17 on Debian.', '1.0', 'active', CURRENT_DATE - INTERVAL 15,
 (SELECT user_id FROM users WHERE name = 'Alice Johnson'),
 NULL,
 (SELECT category_id FROM categories WHERE name = 'PostgreSQL DBA'),
 'database_documents/PostgreSQL_17_Installation_Debian.md', 'md', 5120, 12),

('Oracle 19c Installation Procedure on RHEL', 'Step-by-step installation guide for Oracle 19c on Red Hat Enterprise Linux.', '1.0', 'active', CURRENT_DATE - INTERVAL 15,
 (SELECT user_id FROM users WHERE name = 'Bob Smith'),
 NULL,
 (SELECT category_id FROM categories WHERE name = 'Oracle DBA'),
 'database_documents/Oracle_19_Installation_RHEL.md', 'md', 6144, 14),

('PostgreSQL Backup Setup on Debian', 'Guide to setting up backups for PostgreSQL 17 on Debian.', '1.0', 'active', CURRENT_DATE - INTERVAL 10,
 (SELECT user_id FROM users WHERE name = 'Carol White'),
 NULL,
 (SELECT category_id FROM categories WHERE name = 'Backup Specialist'),
 'database_documents/PostgreSQL_Backup_Setup_Debian.md', 'md', 4096, 10),

('Oracle Backup Setup on RHEL', 'Guide to setting up backups for Oracle 19c on Red Hat Enterprise Linux.', '1.0', 'active', CURRENT_DATE - INTERVAL 10,
 (SELECT user_id FROM users WHERE name = 'Carol White'),
 NULL,
 (SELECT category_id FROM categories WHERE name = 'Backup Specialist'),
 'database_documents/Oracle_Backup_Setup_RHEL.md', 'md', 4608, 11);
