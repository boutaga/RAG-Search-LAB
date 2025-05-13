# PostgreSQL Backup Setup on Debian

This document describes how to set up backups for PostgreSQL 17 on a Debian system.

## Backup Strategies

### Physical Backups with pg_basebackup
- Use `pg_basebackup` to create a full physical backup of the database cluster.
- Example command:
```bash
pg_basebackup -h localhost -D /var/lib/postgresql/backups/base -U postgres -Fp -Xs -P -v
```
- Schedule regular base backups using cron jobs.

### Continuous Archiving and Point-in-Time Recovery (PITR)
- Enable WAL archiving by setting in `postgresql.conf`:
```
archive_mode = on
archive_command = 'test ! -f /var/lib/postgresql/wal_archive/%f && cp %p /var/lib/postgresql/wal_archive/%f'
```
- Ensure the archive directory exists and is writable.
- Use WAL files along with base backups for PITR.

### Logical Backups with pg_dump and pg_dumpall
- Use `pg_dump` for individual database dumps:
```bash
pg_dump -U postgres -F c -b -v -f /var/lib/postgresql/backups/dbname.backup dbname
```
- Use `pg_dumpall` for global objects and all databases:
```bash
pg_dumpall -U postgres -f /var/lib/postgresql/backups/all_databases.sql
```
- Schedule logical backups for schema and data export.

## Backup Automation and Verification
- Automate backups with cron jobs.
- Verify backups by restoring to a test environment regularly.
- Monitor backup logs for errors.

## Security and Storage
- Store backups on separate physical or network storage.
- Encrypt backups using tools like GPG.
- Maintain backup retention policies.
