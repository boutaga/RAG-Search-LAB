

# RAG-Search-LAB
This repository has educational purpose on advanced RAG Search techniques based on PostgreSQL-pgvector-pgvectorscale-pgai...
In order to expose a real use cases and prove the point and added value of advanced RAG Search techniques, I created the following data sources
and the associated scenario of a Service Desk team that would take leverage of AI/LLM and RAG Search techniques.   
An AI Agent for the Service Desk team is holding the business logic and has deferent tools like email, document management,... This AI Agent also take leverage of
the RAG Search process that is at the center of experiment. The goal is to explain how different RAG search techniques can impact the response of the Agent.


Intent of the solution and added value expected : 

- Faster Time to Resolution for teams.
- Improvements on the quality of service. 
    - avoid having twice the same error by learning from past resolution
    - link alerts with solutions
    - link SOP with best practices
    - no hanging tickets with automated routing
    - KPI generation for mgmt

![image](https://github.com/user-attachments/assets/5b8d301b-3e73-4d8e-a7b5-a3c5a7453ccd)


# Documents database

This is a sample database that is storing informations about document storage application like Sharepoint or M-Files. 
The intent is to store SOP (Standard Operationnal Procedures) in various format like pdf or makdown to allow retrieval from the RAG Search workflow. 
It is important to note that the database is holding metadata informations of the documents and links of there real paths on the file system. 

## Description of the data model

# Service Desk database 

This database is a sample database of customer service request made on technologies like PostgreSQL, SQL Server, Oracle, RHEL, Ubuntu, ...etc. 
Since there is no sample source of information or model available this database was completely created for this purpose.


## 1. Lookup Tables  

```sql
-- 1.1 Ticket status lookup
CREATE TABLE ticket_status (
  status_id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- identity column  ([Documentation: 17: 5.3. Identity Columns - PostgreSQL](https://www.postgresql.org/docs/current/ddl-identity-columns.html?utm_source=chatgpt.com))
  name        VARCHAR(50)       NOT NULL,
  description TEXT
);

-- 1.2 Ticket priority lookup
CREATE TABLE ticket_priority (
  priority_id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- identity column  ([Documentation: 17: 5.3. Identity Columns - PostgreSQL](https://www.postgresql.org/docs/current/ddl-identity-columns.html?utm_source=chatgpt.com))
  name                  VARCHAR(50)       NOT NULL,
  escalation_threshold_hours INT           NOT NULL
);

-- 1.3 Ticket type lookup
CREATE TABLE ticket_type (
  type_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- identity column  ([Documentation: 17: 5.3. Identity Columns - PostgreSQL](https://www.postgresql.org/docs/current/ddl-identity-columns.html?utm_source=chatgpt.com))
  name       VARCHAR(50)       NOT NULL,
  description TEXT
);
```
- Uses `GENERATED ALWAYS AS IDENTITY` for standards-compliant auto-incrementing keys  ([Documentation: 17: 5.3. Identity Columns - PostgreSQL](https://www.postgresql.org/docs/current/ddl-identity-columns.html?utm_source=chatgpt.com)).  
- Basic lookup tables with small `VARCHAR` keys.

---

## 2. SLA & Organization  

```sql
-- 2.1 Service Level Agreements
CREATE TABLE sla (
  sla_id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name                 VARCHAR(100) NOT NULL,
  response_time_hours  INT          NOT NULL,
  resolution_time_hours INT         NOT NULL,
  applies_to_type_id   BIGINT,
  FOREIGN KEY (applies_to_type_id) REFERENCES ticket_type(type_id)
);

-- 2.2 Client organizations
CREATE TABLE organization (
  organization_id  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name             VARCHAR(100)        NOT NULL,
  address          TEXT,
  main_contact_email VARCHAR(255),
  main_contact_phone VARCHAR(50),
  default_sla_id   BIGINT,
  FOREIGN KEY (default_sla_id) REFERENCES sla(sla_id)
);
```
- Links each org to an SLA, and SLAs optionally to a ticket type  ([PostgreSQL partitioning (2): Range partitioning - dbi services](https://www.dbi-services.com/blog/postgresql-partitioning-2-range-partitioning/?utm_source=chatgpt.com)).

---

## 3. Users  

```sql
CREATE TABLE "user" (
  user_id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name            VARCHAR(100)        NOT NULL,
  email           VARCHAR(255)        NOT NULL UNIQUE,
  phone           VARCHAR(50),
  organization_id BIGINT,
  role            VARCHAR(20)         NOT NULL,
  FOREIGN KEY (organization_id) REFERENCES organization(organization_id)
);
```
- Support agents and requesters share this table, distinguished by `role`.

---

## 4. Configuration Items  

```sql
-- 4.1 CIs (assets/components)
CREATE TABLE configuration_item (
  ci_id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name       VARCHAR(100) NOT NULL,
  ci_type    VARCHAR(50),
  identifier VARCHAR(100) UNIQUE,
  status     VARCHAR(50)
);

-- 4.2 CI relationships (parent/child)
CREATE TABLE ci_relationship (
  relationship_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  parent_ci_id    BIGINT NOT NULL,
  child_ci_id     BIGINT NOT NULL,
  relationship_type VARCHAR(50),
  FOREIGN KEY (parent_ci_id) REFERENCES configuration_item(ci_id),
  FOREIGN KEY (child_ci_id)  REFERENCES configuration_item(ci_id)
);
```

---

## 5. Schedules & On-Call  

```sql
-- 5.1 Business hours schedules
CREATE TABLE schedule (
  schedule_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name           VARCHAR(100) NOT NULL,
  timezone       TEXT         NOT NULL,
  business_hours JSONB        NOT NULL  -- JSONB for flexible hours definitions  ([PostgreSQL partitioning (2): Range partitioning - dbi services](https://www.dbi-services.com/blog/postgresql-partitioning-2-range-partitioning/?utm_source=chatgpt.com))
);

-- 5.2 On-call assignments
CREATE TABLE oncall_schedule (
  oncall_schedule_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  schedule_id        BIGINT NOT NULL,
  user_id            BIGINT NOT NULL,
  start_date         DATE NOT NULL,
  end_date           DATE NOT NULL,
  FOREIGN KEY (schedule_id) REFERENCES schedule(schedule_id),
  FOREIGN KEY (user_id)       REFERENCES "user"(user_id)
);
```

---

## 6. Partitioned Ticket Table  

```sql
-- 6.1 Create parent table partitioned by closure_date
CREATE TABLE ticket (
  ticket_id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  title             VARCHAR(255)       NOT NULL,
  description       TEXT,
  created_at        TIMESTAMPTZ        NOT NULL DEFAULT now(),  -- timestamp with time zone  ([PostgreSQL NOW() Function: Getting the Current Date and Time](https://neon.tech/postgresql/postgresql-date-functions/postgresql-now?utm_source=chatgpt.com))
  updated_at        TIMESTAMPTZ        NOT NULL DEFAULT now(),  -- timestamp with time zone  ([PostgreSQL NOW() Function: Getting the Current Date and Time](https://neon.tech/postgresql/postgresql-date-functions/postgresql-now?utm_source=chatgpt.com))
  closure_date      DATE,
  status_id         BIGINT             NOT NULL,
  priority_id       BIGINT             NOT NULL,
  type_id           BIGINT             NOT NULL,
  organization_id   BIGINT             NOT NULL,
  requester_user_id BIGINT             NOT NULL,
  assignee_user_id  BIGINT,
  sla_id            BIGINT             NOT NULL,
  FOREIGN KEY (status_id)       REFERENCES ticket_status(status_id),
  FOREIGN KEY (priority_id)     REFERENCES ticket_priority(priority_id),
  FOREIGN KEY (type_id)         REFERENCES ticket_type(type_id),
  FOREIGN KEY (organization_id) REFERENCES organization(organization_id),
  FOREIGN KEY (requester_user_id) REFERENCES "user"(user_id),
  FOREIGN KEY (assignee_user_id)  REFERENCES "user"(user_id),
  FOREIGN KEY (sla_id)          REFERENCES sla(sla_id)
) PARTITION BY RANGE (closure_date);  -- declarative range partitioning  ([Documentation: 17: 5.12. Table Partitioning - PostgreSQL](https://www.postgresql.org/docs/current/ddl-partitioning.html?utm_source=chatgpt.com))
```

---

## 7. Default Partition for Open Tickets  

```sql
CREATE TABLE ticket_open PARTITION OF ticket
  DEFAULT;  -- catches NULL or out-of-range closure_date rows  ([How to use table partitioning to scale PostgreSQL - EDB](https://www.enterprisedb.com/postgres-tutorials/how-use-table-partitioning-scale-postgresql?utm_source=chatgpt.com))
```

---

## 8. Yearly Partitions (2025–2035)  

```sql
CREATE TABLE ticket_2025 PARTITION OF ticket
  FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE ticket_2026 PARTITION OF ticket
  FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

-- …repeat similarly through…

CREATE TABLE ticket_2035 PARTITION OF ticket
  FOR VALUES FROM ('2035-01-01') TO ('2036-01-01');
```
- Each partition covers [Jan 1, Year] to [Jan 1, Year+1)  ([How to create table partition in PostgreSQL? - TablePlus](https://tableplus.com/blog/2019/09/create-table-partition-postgresql.html?utm_source=chatgpt.com)).

---

## 9. Automate Future Yearly Partitions  

```sql
DO $$
DECLARE
  start_year INT := EXTRACT(YEAR FROM CURRENT_DATE)::INT;
  end_year   INT := start_year + 10;
  yr         INT;
BEGIN
  FOR yr IN start_year..end_year LOOP
    EXECUTE FORMAT(
      'CREATE TABLE IF NOT EXISTS ticket_%s PARTITION OF ticket
         FOR VALUES FROM (%L) TO (%L);',
      yr,
      TO_CHAR(MAKE_DATE(yr,1,1),   'YYYY-MM-DD'),
      TO_CHAR(MAKE_DATE(yr+1,1,1), 'YYYY-MM-DD')
    );
  END LOOP;
END
$$;
```
- Dynamic DDL via PL/pgSQL `DO` block  ([How can I finish a "RANGE type" partition in PostgreSQL?](https://dba.stackexchange.com/questions/324612/how-can-i-finish-a-range-type-partition-in-postgresql?utm_source=chatgpt.com)).

---

Running the above SQL in sequence will fully build your schema—with a partitioned `ticket` table ready for 24/7 operations and future growth.

## Description of the data model


# RAG database

This database is to allow management of the RAG search process of our application. 
It holds user profile information 


