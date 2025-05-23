-- Populate ticket_status
INSERT INTO ticket_status (name, description) VALUES
('Open', 'Ticket is open and awaiting action'),
('In Progress', 'Work is ongoing on the ticket'),
('Resolved', 'Issue has been resolved, pending closure'),
('Closed', 'Ticket is closed'),
('On Hold', 'Ticket is on hold due to external dependencies');

-- Populate ticket_priority
INSERT INTO ticket_priority (name, escalation_threshold_hours) VALUES
('Low', 72),
('Medium', 24),
('High', 8),
('Critical', 2);

-- Populate ticket_type
INSERT INTO ticket_type (name, description) VALUES
('Backup Error', 'Errors related to database backups'),
('Long Running Query', 'Queries running longer than expected'),
('Cluster Failover', 'Issues with cluster failover mechanisms'),
('Performance Degradation', 'General performance issues'),
('Security Alert', 'Security related alerts'),
('Configuration Issue', 'Misconfiguration detected'),
('Data Corruption', 'Data integrity issues detected');

-- Populate SLA
INSERT INTO sla (name, response_time_hours, resolution_time_hours, applies_to_type_id) VALUES
('Standard Backup SLA', 4, 24, (SELECT type_id FROM ticket_type WHERE name = 'Backup Error')),
('Query Performance SLA', 2, 12, (SELECT type_id FROM ticket_type WHERE name = 'Long Running Query')),
('Cluster SLA', 1, 6, (SELECT type_id FROM ticket_type WHERE name = 'Cluster Failover')),
('General SLA', 8, 48, NULL);

-- Populate organizations with comic tone names from various sectors
INSERT INTO organization (name, address, main_contact_email, main_contact_phone, default_sla_id) VALUES
('Acme Rocket Science', '123 Rocket Rd, Moon City', 'contact@acmerocket.com', '555-ROCKET', (SELECT sla_id FROM sla WHERE name = 'General SLA')),
('Globex Corporation', '456 Industrial Ave, Metropolis', 'info@globex.com', '555-GLOBEX', (SELECT sla_id FROM sla WHERE name = 'General SLA')),
('Initech', '789 Silicon Blvd, Techville', 'support@initech.com', '555-INITECH', (SELECT sla_id FROM sla WHERE name = 'Standard Backup SLA')),
('Umbrella Corp', '101 Biohazard St, Raccoon City', 'security@umbrella.com', '555-UMBRELLA', (SELECT sla_id FROM sla WHERE name = 'Security Alert')),
('Soylent Industries', '202 Greenway, Foodtown', 'contact@soylent.com', '555-SOY', (SELECT sla_id FROM sla WHERE name = 'General SLA')),
('Stark Enterprises', '303 Iron St, New York', 'tony@starkenterprises.com', '555-STARK', (SELECT sla_id FROM sla WHERE name = 'Cluster SLA')),
('Wonka Factory', '404 Candy Ln, Sweet City', 'hello@wonka.com', '555-WONKA', (SELECT sla_id FROM sla WHERE name = 'General SLA')),
('Duff Brewery', '505 Beer Blvd, Springfield', 'contact@duffbrewery.com', '555-DUFF', (SELECT sla_id FROM sla WHERE name = 'General SLA')),
('Cyberdyne Systems', '606 Future Rd, Silicon Valley', 'info@cyberdyne.com', '555-CYBER', (SELECT sla_id FROM sla WHERE name = 'Cluster SLA')),
('Hooli', '707 Tech Park, Silicon Valley', 'support@hooli.com', '555-HOOLI', (SELECT sla_id FROM sla WHERE name = 'Query Performance SLA')),
('Pied Piper', '808 Compression St, Silicon Valley', 'contact@piedpiper.com', '555-PIED', (SELECT sla_id FROM sla WHERE name = 'Long Running Query')),
('Vandelay Industries', '909 Importer Rd, New York', 'sales@vandelay.com', '555-VANDELAY', (SELECT sla_id FROM sla WHERE name = 'General SLA')),
('Bluth Company', '111 Banana Stand, Newport', 'info@bluth.com', '555-BLUTH', (SELECT sla_id FROM sla WHERE name = 'General SLA')),
('Prestige Worldwide', '222 Yacht Club, Miami', 'contact@prestigeworldwide.com', '555-PRESTIGE', (SELECT sla_id FROM sla WHERE name = 'General SLA')),
('Oceanic Airlines', '333 Flight Rd, Lost Island', 'support@oceanic.com', '555-OCEANIC', (SELECT sla_id FROM sla WHERE name = 'General SLA')),
('Monsters Inc', '444 Scare St, Monstropolis', 'hello@monstersinc.com', '555-MONSTER', (SELECT sla_id FROM sla WHERE name = 'General SLA')),
('Dunder Mifflin', '555 Paper Rd, Scranton', 'contact@dundermifflin.com', '555-DUNDER', (SELECT sla_id FROM sla WHERE name = 'General SLA')),
('Soylent Green', '666 Mystery Ln, Unknown', 'info@soylentgreen.com', '555-GREEN', (SELECT sla_id FROM sla WHERE name = 'General SLA')),
('Tyrell Corporation', '777 Nexus St, Los Angeles', 'support@tyrell.com', '555-TYRELL', (SELECT sla_id FROM sla WHERE name = 'Security Alert')),
('Gekko & Co', '888 Wall St, New York', 'contact@gekko.com', '555-GEKKO', (SELECT sla_id FROM sla WHERE name = 'General SLA'));

-- Populate users: 10 operators and 4 consultants
INSERT INTO "user" (name, email, phone, organization_id, role) VALUES
('Operator One', 'operator1@acmerocket.com', '555-0001', (SELECT organization_id FROM organization WHERE name = 'Acme Rocket Science'), 'operator'),
('Operator Two', 'operator2@globex.com', '555-0002', (SELECT organization_id FROM organization WHERE name = 'Globex Corporation'), 'operator'),
('Operator Three', 'operator3@initech.com', '555-0003', (SELECT organization_id FROM organization WHERE name = 'Initech'), 'operator'),
('Operator Four', 'operator4@umbrella.com', '555-0004', (SELECT organization_id FROM organization WHERE name = 'Umbrella Corp'), 'operator'),
('Operator Five', 'operator5@soylent.com', '555-0005', (SELECT organization_id FROM organization WHERE name = 'Soylent Industries'), 'operator'),
('Operator Six', 'operator6@starkenterprises.com', '555-0006', (SELECT organization_id FROM organization WHERE name = 'Stark Enterprises'), 'operator'),
('Operator Seven', 'operator7@wonka.com', '555-0007', (SELECT organization_id FROM organization WHERE name = 'Wonka Factory'), 'operator'),
('Operator Eight', 'operator8@duffbrewery.com', '555-0008', (SELECT organization_id FROM organization WHERE name = 'Duff Brewery'), 'operator'),
('Operator Nine', 'operator9@cyberdyne.com', '555-0009', (SELECT organization_id FROM organization WHERE name = 'Cyberdyne Systems'), 'operator'),
('Operator Ten', 'operator10@hooli.com', '555-0010', (SELECT organization_id FROM organization WHERE name = 'Hooli'), 'operator'),

('Consultant Alpha', 'consultant.alpha@piedpiper.com', '555-1010', (SELECT organization_id FROM organization WHERE name = 'Pied Piper'), 'consultant'),
('Consultant Beta', 'consultant.beta@vandelay.com', '555-1011', (SELECT organization_id FROM organization WHERE name = 'Vandelay Industries'), 'consultant'),
('Consultant Gamma', 'consultant.gamma@bluth.com', '555-1012', (SELECT organization_id FROM organization WHERE name = 'Bluth Company'), 'consultant'),
('Consultant Delta', 'consultant.delta@prestigeworldwide.com', '555-1013', (SELECT organization_id FROM organization WHERE name = 'Prestige Worldwide'), 'consultant');

-- Populate configuration items (CIs) for Oracle and PostgreSQL on Ubuntu and RHEL with versions
INSERT INTO configuration_item (name, ci_type, identifier, status) VALUES
('Oracle DB 19c on Ubuntu 20.04', 'Database', 'oracle_19c_ubuntu_20_04', 'Active'),
('Oracle DB 12c on RHEL 7', 'Database', 'oracle_12c_rhel_7', 'Active'),
('PostgreSQL 13 on Ubuntu 18.04', 'Database', 'postgresql_13_ubuntu_18_04', 'Active'),
('PostgreSQL 14 on RHEL 8', 'Database', 'postgresql_14_rhel_8', 'Active'),
('PostgreSQL 12 on Ubuntu 20.04', 'Database', 'postgresql_12_ubuntu_20_04', 'Active'),
('Oracle DB 21c on RHEL 8', 'Database', 'oracle_21c_rhel_8', 'Active');

-- Ticket activity table to store exchanges between operators and customers
CREATE TABLE ticket_activity (
  activity_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  ticket_id BIGINT NOT NULL,
  activity_time TIMESTAMPTZ NOT NULL DEFAULT now(),
  actor VARCHAR(100) NOT NULL, -- e.g. operator or customer name
  message TEXT NOT NULL,
  FOREIGN KEY (ticket_id) REFERENCES ticket(ticket_id)
);

-- Populate tickets with various statuses and realistic error messages and resolution paths
INSERT INTO ticket (title, description, created_at, updated_at, closure_date, status_id, priority_id, type_id, organization_id, requester_user_id, assignee_user_id, sla_id) VALUES
-- Active tickets (around 20)
('Backup failed on Oracle DB 19c', 
 'Backup job failed with error: ORA-19505: failed to identify file\nResolution: Check disk space and retry backup.', 
 NOW() - INTERVAL '2 days', NOW() - INTERVAL '1 day', NULL, 
 (SELECT status_id FROM ticket_status WHERE name = 'Open'), 
 (SELECT priority_id FROM ticket_priority WHERE name = 'High'), 
 (SELECT type_id FROM ticket_type WHERE name = 'Backup Error'), 
 (SELECT organization_id FROM organization WHERE name = 'Acme Rocket Science'), 
 (SELECT user_id FROM "user" WHERE email = 'operator1@acmerocket.com'), 
 (SELECT user_id FROM "user" WHERE email = 'consultant.alpha@piedpiper.com'), 
 (SELECT sla_id FROM sla WHERE name = 'Standard Backup SLA')),

('Long running query on PostgreSQL 13', 
 'Query running for over 2 hours causing performance degradation.\nResolution: Analyze query plan and optimize indexes.', 
 NOW() - INTERVAL '3 days', NOW() - INTERVAL '2 days', NULL, 
 (SELECT status_id FROM ticket_status WHERE name = 'In Progress'), 
 (SELECT priority_id FROM ticket_priority WHERE name = 'Medium'), 
 (SELECT type_id FROM ticket_type WHERE name = 'Long Running Query'), 
 (SELECT organization_id FROM organization WHERE name = 'Globex Corporation'), 
 (SELECT user_id FROM "user" WHERE email = 'operator2@globex.com'), 
 (SELECT user_id FROM "user" WHERE email = 'consultant.beta@vandelay.com'), 
 (SELECT sla_id FROM sla WHERE name = 'Query Performance SLA')),

('Patroni cluster failover issue on PostgreSQL 14', 
 'Cluster failover did not complete successfully.\nError: Patroni failed to promote replica.\nResolution: Check Patroni logs and restart cluster.', 
 NOW() - INTERVAL '1 day', NOW() - INTERVAL '12 hours', NULL, 
 (SELECT status_id FROM ticket_status WHERE name = 'Open'), 
 (SELECT priority_id FROM ticket_priority WHERE name = 'Critical'), 
 (SELECT type_id FROM ticket_type WHERE name = 'Cluster Failover'), 
 (SELECT organization_id FROM organization WHERE name = 'Initech'), 
 (SELECT user_id FROM "user" WHERE email = 'operator3@initech.com'), 
 (SELECT user_id FROM "user" WHERE email = 'consultant.gamma@bluth.com'), 
 (SELECT sla_id FROM sla WHERE name = 'Cluster SLA')),

('Backup job error on Oracle DB 12c', 
 'Backup failed due to ORA-27037: unable to obtain file status.\nResolution: Verify backup device and permissions.', 
 NOW() - INTERVAL '5 days', NOW() - INTERVAL '4 days', NOW() - INTERVAL '1 day', 
 (SELECT status_id FROM ticket_status WHERE name = 'Closed'), 
 (SELECT priority_id FROM ticket_priority WHERE name = 'High'), 
 (SELECT type_id FROM ticket_type WHERE name = 'Backup Error'), 
 (SELECT organization_id FROM organization WHERE name = 'Umbrella Corp'), 
 (SELECT user_id FROM "user" WHERE email = 'operator4@umbrella.com'), 
 (SELECT user_id FROM "user" WHERE email = 'consultant.delta@prestigeworldwide.com'), 
 (SELECT sla_id FROM sla WHERE name = 'Standard Backup SLA')),

('Long running query on PostgreSQL 12', 
 'Query execution time exceeded threshold.\nResolution: Review query and optimize.', 
 NOW() - INTERVAL '7 days', NOW() - INTERVAL '6 days', NOW() - INTERVAL '2 days', 
 (SELECT status_id FROM ticket_status WHERE name = 'Resolved'), 
 (SELECT priority_id FROM ticket_priority WHERE name = 'Medium'), 
 (SELECT type_id FROM ticket_type WHERE name = 'Long Running Query'), 
 (SELECT organization_id FROM organization WHERE name = 'Soylent Industries'), 
 (SELECT user_id FROM "user" WHERE email = 'operator5@soylent.com'), 
 (SELECT user_id FROM "user" WHERE email = 'consultant.alpha@piedpiper.com'), 
 (SELECT sla_id FROM sla WHERE name = 'Query Performance SLA')),

('Cluster failover alert on Oracle DB 21c', 
 'Failover event detected but cluster did not stabilize.\nResolution: Investigate cluster nodes and network.', 
 NOW() - INTERVAL '10 hours', NOW() - INTERVAL '5 hours', NULL, 
 (SELECT status_id FROM ticket_status WHERE name = 'In Progress'), 
 (SELECT priority_id FROM ticket_priority WHERE name = 'Critical'), 
 (SELECT type_id FROM ticket_type WHERE name = 'Cluster Failover'), 
 (SELECT organization_id FROM organization WHERE name = 'Stark Enterprises'), 
 (SELECT user_id FROM "user" WHERE email = 'operator6@starkenterprises.com'), 
 (SELECT user_id FROM "user" WHERE email = 'consultant.beta@vandelay.com'), 
 (SELECT sla_id FROM sla WHERE name = 'Cluster SLA')),

('Backup failure on PostgreSQL 14', 
 'Backup process terminated unexpectedly.\nResolution: Check backup scripts and storage.', 
 NOW() - INTERVAL '4 days', NOW() - INTERVAL '3 days', NULL, 
 (SELECT status_id FROM ticket_status WHERE name = 'Open'), 
 (SELECT priority_id FROM ticket_priority WHERE name = 'High'), 
 (SELECT type_id FROM ticket_type WHERE name = 'Backup Error'), 
 (SELECT organization_id FROM organization WHERE name = 'Wonka Factory'), 
 (SELECT user_id FROM "user" WHERE email = 'operator7@wonka.com'), 
 (SELECT user_id FROM "user" WHERE email = 'consultant.gamma@bluth.com'), 
 (SELECT sla_id FROM sla WHERE name = 'Standard Backup SLA')),

('Performance degradation on PostgreSQL 13', 
 'System experiencing slow response times.\nResolution: Check resource usage and tune parameters.', 
 NOW() - INTERVAL '6 days', NOW() - INTERVAL '5 days', NULL, 
 (SELECT status_id FROM ticket_status WHERE name = 'Open'), 
 (SELECT priority_id FROM ticket_priority WHERE name = 'Medium'), 
 (SELECT type_id FROM ticket_type WHERE name = 'Performance Degradation'), 
 (SELECT organization_id FROM organization WHERE name = 'Duff Brewery'), 
 (SELECT user_id FROM "user" WHERE email = 'operator8@duffbrewery.com'), 
 (SELECT user_id FROM "user" WHERE email = 'consultant.delta@prestigeworldwide.com'), 
 (SELECT sla_id FROM sla WHERE name = 'General SLA')),

('Security alert on Oracle DB 19c', 
 'Unauthorized access attempt detected.\nResolution: Review security logs and update credentials.', 
 NOW() - INTERVAL '8 days', NOW() - INTERVAL '7 days', NOW() - INTERVAL '1 day', 
 (SELECT status_id FROM ticket_status WHERE name = 'Closed'), 
 (SELECT priority_id FROM ticket_priority WHERE name = 'Critical'), 
 (SELECT type_id FROM ticket_type WHERE name = 'Security Alert'), 
 (SELECT organization_id FROM organization WHERE name = 'Cyberdyne Systems'), 
 (SELECT user_id FROM "user" WHERE email = 'operator9@cyberdyne.com'), 
 (SELECT user_id FROM "user" WHERE email = 'consultant.alpha@piedpiper.com'), 
 (SELECT sla_id FROM sla WHERE name = 'Security Alert')),

('Configuration issue on PostgreSQL 14', 
 'Misconfiguration causing replication lag.\nResolution: Adjust replication settings.', 
 NOW() - INTERVAL '3 days', NOW() - INTERVAL '2 days', NULL, 
 (SELECT status_id FROM ticket_status WHERE name = 'In Progress'), 
 (SELECT priority_id FROM ticket_priority WHERE name = 'Medium'), 
 (SELECT type_id FROM ticket_type WHERE name = 'Configuration Issue'), 
 (SELECT organization_id FROM organization WHERE name = 'Hooli'), 
 (SELECT user_id FROM "user" WHERE email = 'operator10@hooli.com'), 
 (SELECT user_id FROM "user" WHERE email = 'consultant.beta@vandelay.com'), 
 (SELECT sla_id FROM sla WHERE name = 'General SLA')),

-- Additional tickets to reach around 40 total with various statuses and types
('Backup error on Oracle DB 12c', 
 'Backup failed due to disk full.\nResolution: Free up disk space and retry.', 
 NOW() - INTERVAL '15 days', NOW() - INTERVAL '14 days', NOW() - INTERVAL '10 days', 
 (SELECT status_id FROM ticket_status WHERE name = 'Closed'), 
 (SELECT priority_id FROM ticket_priority WHERE name = 'High'), 
 (SELECT type_id FROM ticket_type WHERE name = 'Backup Error'), 
 (SELECT organization_id FROM organization WHERE name = 'Vandelay Industries'), 
 (SELECT user_id FROM "user" WHERE email = 'operator1@acmerocket.com'), 
 (SELECT user_id FROM "user" WHERE email = 'consultant.gamma@bluth.com'), 
 (SELECT sla_id FROM sla WHERE name = 'Standard Backup SLA')),

('Long running query on PostgreSQL 12', 
 'Query causing deadlock.\nResolution: Kill query and optimize.', 
 NOW() - INTERVAL '12 days', NOW() - INTERVAL '11 days', NOW() - INTERVAL '9 days', 
 (SELECT status_id FROM ticket_status WHERE name = 'Resolved'), 
 (SELECT priority_id FROM ticket_priority WHERE name = 'Medium'), 
 (SELECT type_id FROM ticket_type WHERE name = 'Long Running Query'), 
 (SELECT organization_id FROM organization WHERE name = 'Bluth Company'), 
 (SELECT user_id FROM "user" WHERE email = 'operator2@globex.com'), 
 (SELECT user_id FROM "user" WHERE email = 'consultant.delta@prestigeworldwide.com'), 
 (SELECT sla_id FROM sla WHERE name = 'Query Performance SLA')),

('Cluster failover issue on PostgreSQL 14', 
 'Failover took longer than expected.\nResolution: Review cluster health.', 
 NOW() - INTERVAL '20 days', NOW() - INTERVAL '19 days', NOW() - INTERVAL '18 days', 
 (SELECT status_id FROM ticket_status WHERE name = 'Closed'), 
 (SELECT priority_id FROM ticket_priority WHERE name = 'Critical'), 
 (SELECT type_id FROM ticket_type WHERE name = 'Cluster Failover'), 
 (SELECT organization_id FROM organization WHERE name = 'Oceanic Airlines'), 
 (SELECT user_id FROM "user" WHERE email = 'operator3@initech.com'), 
 (SELECT user_id FROM "user" WHERE email = 'consultant.alpha@piedpiper.com'), 
 (SELECT sla_id FROM sla WHERE name = 'Cluster SLA')),

('Performance degradation on Oracle DB 21c', 
 'High CPU usage detected.\nResolution: Tune database parameters.', 
 NOW() - INTERVAL '25 days', NOW() - INTERVAL '24 days', NOW() - INTERVAL '23 days', 
 (SELECT status_id FROM ticket_status WHERE name = 'Closed'), 
 (SELECT priority_id FROM ticket_priority WHERE name = 'Medium'), 
 (SELECT type_id FROM ticket_type WHERE name = 'Performance Degradation'), 
 (SELECT organization_id FROM organization WHERE name = 'Monsters Inc'), 
 (SELECT user_id FROM "user" WHERE email = 'operator4@umbrella.com'), 
 (SELECT user_id FROM "user" WHERE email = 'consultant.beta@vandelay.com'), 
 (SELECT sla_id FROM sla WHERE name = 'General SLA')),

('Security alert on PostgreSQL 13', 
 'Suspicious login attempts detected.\nResolution: Block IP and reset passwords.', 
 NOW() - INTERVAL '30 days', NOW() - INTERVAL '29 days', NOW() - INTERVAL '28 days', 
 (SELECT status_id FROM ticket_status WHERE name = 'Closed'), 
 (SELECT priority_id FROM ticket_priority WHERE name = 'Critical'), 
 (SELECT type_id FROM ticket_type WHERE name = 'Security Alert'), 
 (SELECT organization_id FROM organization WHERE name = 'Dunder Mifflin'), 
 (SELECT user_id FROM "user" WHERE email = 'operator5@soylent.com'), 
 (SELECT user_id FROM "user" WHERE email = 'consultant.gamma@bluth.com'), 
 (SELECT sla_id FROM sla WHERE name = 'Security Alert')),

('Configuration issue on Oracle DB 19c', 
 'Parameter misconfiguration causing slow startup.\nResolution: Correct parameters and restart.', 
 NOW() - INTERVAL '35 days', NOW() - INTERVAL '34 days', NOW() - INTERVAL '33 days', 
 (SELECT status_id FROM ticket_status WHERE name = 'Closed'), 
 (SELECT priority_id FROM ticket_priority WHERE name = 'Low'), 
 (SELECT type_id FROM ticket_type WHERE name = 'Configuration Issue'), 
 (SELECT organization_id FROM organization WHERE name = 'Soylent Green'), 
 (SELECT user_id FROM "user" WHERE email = 'operator6@starkenterprises.com'), 
 (SELECT user_id FROM "user" WHERE email = 'consultant.delta@prestigeworldwide.com'), 
 (SELECT sla_id FROM sla WHERE name = 'General SLA'));

-- Populate ticket_activity with exchanges between operators and customers
INSERT INTO ticket_activity (ticket_id, activity_time, actor, message) VALUES
-- For ticket: Backup failed on Oracle DB 19c
((SELECT ticket_id FROM ticket WHERE title = 'Backup failed on Oracle DB 19c'), NOW() - INTERVAL '1 day 20 hours', 'Operator One', 'Initial assessment: Disk space is sufficient, backup device accessible.'),
((SELECT ticket_id FROM ticket WHERE title = 'Backup failed on Oracle DB 19c'), NOW() - INTERVAL '1 day 18 hours', 'Customer', 'Confirmed no recent changes to backup device or storage.'),
((SELECT ticket_id FROM ticket WHERE title = 'Backup failed on Oracle DB 19c'), NOW() - INTERVAL '1 day 15 hours', 'Operator One', 'Found corrupted backup file in backup directory, removed it and retried backup.'),
((SELECT ticket_id FROM ticket WHERE title = 'Backup failed on Oracle DB 19c'), NOW() - INTERVAL '1 day 10 hours', 'Customer', 'Backup completed successfully after cleanup.'),
((SELECT ticket_id FROM ticket WHERE title = 'Backup failed on Oracle DB 19c'), NOW() - INTERVAL '1 day 5 hours', 'Operator One', 'Ticket resolved: Corrupted backup file caused failure. Backup process verified and successful.'),

-- For ticket: Long running query on PostgreSQL 13
((SELECT ticket_id FROM ticket WHERE title = 'Long running query on PostgreSQL 13'), NOW() - INTERVAL '2 days 20 hours', 'Operator Two', 'Requesting query text and execution plan for analysis.'),
((SELECT ticket_id FROM ticket WHERE title = 'Long running query on PostgreSQL 13'), NOW() - INTERVAL '2 days 18 hours', 'Customer', 'Provided query text and EXPLAIN ANALYZE output.'),
((SELECT ticket_id FROM ticket WHERE title = 'Long running query on PostgreSQL 13'), NOW() - INTERVAL '2 days 15 hours', 'Operator Two', 'Identified missing index on join column, recommended index creation.'),
((SELECT ticket_id FROM ticket WHERE title = 'Long running query on PostgreSQL 13'), NOW() - INTERVAL '2 days 10 hours', 'Customer', 'Index created, query performance improved significantly.'),
((SELECT ticket_id FROM ticket WHERE title = 'Long running query on PostgreSQL 13'), NOW() - INTERVAL '2 days 5 hours', 'Operator Two', 'Ticket resolved: Query optimized with new index.'),

-- For ticket: Patroni cluster failover issue on PostgreSQL 14
((SELECT ticket_id FROM ticket WHERE title = 'Patroni cluster failover issue on PostgreSQL 14'), NOW() - INTERVAL '20 hours', 'Operator Three', 'Checking Patroni logs for failover errors.'),
((SELECT ticket_id FROM ticket WHERE title = 'Patroni cluster failover issue on PostgreSQL 14'), NOW() - INTERVAL '18 hours', 'Customer', 'No recent configuration changes reported.'),
((SELECT ticket_id FROM ticket WHERE title = 'Patroni cluster failover issue on PostgreSQL 14'), NOW() - INTERVAL '15 hours', 'Operator Three', 'Detected network latency causing failover delay, recommended network check.'),
((SELECT ticket_id FROM ticket WHERE title = 'Patroni cluster failover issue on PostgreSQL 14'), NOW() - INTERVAL '10 hours', 'Customer', 'Network issues resolved, cluster failover successful.'),
((SELECT ticket_id FROM ticket WHERE title = 'Patroni cluster failover issue on PostgreSQL 14'), NOW() - INTERVAL '5 hours', 'Operator Three', 'Ticket resolved: Network latency caused failover delay, issue fixed.'),

-- Additional ticket activities can be added similarly for other tickets
;
