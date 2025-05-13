# PostgreSQL Best Practices for DBAs

## Installation and Configuration

### Version Selection
- Always use the latest stable release to benefit from security patches and performance improvements.
- Verify compatibility with your operating system and application requirements.

### Data Directory and Storage
- Place data directory on high-performance storage with redundancy (e.g., RAID 10).
- Separate WAL (Write-Ahead Log) files on dedicated disks to reduce I/O contention.

### Memory Configuration
- `shared_buffers`: Set to 25-40% of total system RAM. This is the main cache for PostgreSQL.
- `work_mem`: Allocate based on expected query complexity and concurrency; too high can cause memory exhaustion.
- `maintenance_work_mem`: Increase during maintenance operations like VACUUM and CREATE INDEX.

### Connection Settings
- `max_connections`: Set according to workload; use connection pooling (PgBouncer) to handle large numbers of clients efficiently.
- `effective_cache_size`: Set to estimate of OS disk cache available to PostgreSQL, typically 50-75% of RAM.

### Logging and Monitoring
- Enable `logging_collector` and configure log rotation.
- Set `log_min_duration_statement` to capture slow queries.
- Use `pg_stat_statements` extension for query tracking.

### Security
- Configure `pg_hba.conf` to restrict access by IP and authentication method.
- Use SSL/TLS for client connections.
- Regularly update passwords and roles.

## Performance Tuning

### Vacuum and Analyze
- Schedule regular autovacuum to prevent table bloat.
- Manually run `VACUUM FULL` and `ANALYZE` on large or heavily updated tables as needed.

### Indexing
- Create indexes on columns used in WHERE clauses and JOINs.
- Use partial indexes for selective queries.
- Consider expression indexes for computed columns.

### Query Optimization
- Use `EXPLAIN ANALYZE` to understand query plans.
- Rewrite queries to avoid sequential scans on large tables.
- Use prepared statements and parameterized queries.

### Partitioning
- Use declarative partitioning for large tables to improve query performance and maintenance.
- Choose partition keys that align with query patterns.

### Resource Management
- Tune autovacuum parameters (`autovacuum_vacuum_cost_limit`, `autovacuum_naptime`) based on workload.
- Monitor and adjust `max_parallel_workers_per_gather` for parallel query execution.

## Backup and Recovery

### Backup Strategies
- Use `pg_basebackup` for full physical backups.
- Implement continuous archiving with WAL shipping for point-in-time recovery.
- Use logical backups (`pg_dump`, `pg_dumpall`) for schema and data export.

### Testing
- Regularly test backup restoration procedures.
- Automate backup verification scripts.

### Storage and Security
- Store backups offsite or in cloud storage.
- Encrypt backups to protect sensitive data.

## Major and Minor Updates

### Minor Updates
- Apply minor version updates promptly to fix bugs and security issues.
- Use package manager or PostgreSQL's official repositories.

### Major Upgrades
- Test upgrades in staging environments.
- Use `pg_upgrade` for in-place upgrades to minimize downtime.
- Review deprecated features and adjust applications accordingly.
- Backup database before upgrade.
- Monitor performance and logs post-upgrade.

## Additional DBA Tips
- Use monitoring tools like `pgAdmin`, `Prometheus`, and `Grafana`.
- Automate routine maintenance tasks with cron jobs or scheduling tools.
- Document configuration changes and maintenance activities.
- Stay informed with PostgreSQL community and release notes.
