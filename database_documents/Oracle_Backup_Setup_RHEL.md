# Oracle Backup Setup on RHEL

This document describes how to set up backups for Oracle Database 19c on a Red Hat Enterprise Linux (RHEL) system.

## Backup Strategies

### Recovery Manager (RMAN)
- Use RMAN for efficient and reliable backup and recovery.
- Connect to RMAN:
```bash
rman target /
```
- Perform a full backup:
```rman
BACKUP DATABASE PLUS ARCHIVELOG;
```
- Schedule incremental backups to reduce backup time and storage.

### Flashback Database
- Enable Flashback Database for fast point-in-time recovery.
- Configure flash recovery area in `init.ora` or `spfile`:
```
DB_RECOVERY_FILE_DEST = '/u01/app/oracle/fast_recovery_area'
DB_RECOVERY_FILE_DEST_SIZE = 50G
```
- Enable flashback:
```sql
ALTER DATABASE FLASHBACK ON;
```

### Data Guard
- Use Data Guard for disaster recovery and high availability.
- Configure standby databases and log shipping.

## Backup Automation and Scheduling
- Automate RMAN scripts using cron jobs or Oracle Scheduler.
- Example RMAN script for daily backup:
```rman
RUN {
  ALLOCATE CHANNEL c1 DEVICE TYPE DISK;
  BACKUP DATABASE PLUS ARCHIVELOG;
  RELEASE CHANNEL c1;
}
```

## Backup Validation and Testing
- Use RMAN `VALIDATE` command to check backup integrity.
- Regularly perform test restores on non-production systems.

## Backup Storage and Security
- Store backups on separate physical or network storage.
- Use RMAN encryption or Transparent Data Encryption (TDE) for backup security.
- Maintain backup retention policies and purge obsolete backups.

## Additional Notes
- Monitor alert logs for backup errors.
- Keep RMAN catalog up to date if using one.
- Document backup and recovery procedures.
