-- SQL script to insert document metadata into the document database

INSERT INTO documents (title, description, file_path, created_at) VALUES
('PostgreSQL Best Practices for DBAs', 'Detailed best practices for PostgreSQL installation, configuration, performance tuning, backup, and updates.', 'database_documents/PostgreSQL_Best_Practices.md', NOW()),
('Oracle Database Best Practices for DBAs', 'Detailed best practices for Oracle installation, configuration, performance tuning, backup, and updates.', 'database_documents/Oracle_Best_Practices.md', NOW()),
('PostgreSQL 17 Installation Procedure on Debian', 'Step-by-step installation guide for PostgreSQL 17 on Debian.', 'database_documents/PostgreSQL_17_Installation_Debian.md', NOW()),
('Oracle 19c Installation Procedure on RHEL', 'Step-by-step installation guide for Oracle 19c on Red Hat Enterprise Linux.', 'database_documents/Oracle_19_Installation_RHEL.md', NOW()),
('PostgreSQL Backup Setup on Debian', 'Guide to setting up backups for PostgreSQL 17 on Debian.', 'database_documents/PostgreSQL_Backup_Setup_Debian.md', NOW()),
('Oracle Backup Setup on RHEL', 'Guide to setting up backups for Oracle 19c on Red Hat Enterprise Linux.', 'database_documents/Oracle_Backup_Setup_RHEL.md', NOW());
