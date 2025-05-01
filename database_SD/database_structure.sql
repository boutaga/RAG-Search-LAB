-- 1.1 Ticket status lookup
CREATE TABLE ticket_status (
  status_id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- identity column 
  name        VARCHAR(50)       NOT NULL,
  description TEXT
);

-- 1.2 Ticket priority lookup
CREATE TABLE ticket_priority (
  priority_id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- identity column 
  name                  VARCHAR(50)       NOT NULL,
  escalation_threshold_hours INT           NOT NULL
);

-- 1.3 Ticket type lookup
CREATE TABLE ticket_type (
  type_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- identity column 
  name       VARCHAR(50)       NOT NULL,
  description TEXT
);


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


CREATE TABLE "user" (
  user_id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name            VARCHAR(100)        NOT NULL,
  email           VARCHAR(255)        NOT NULL UNIQUE,
  phone           VARCHAR(50),
  organization_id BIGINT,
  role            VARCHAR(20)         NOT NULL,
  FOREIGN KEY (organization_id) REFERENCES organization(organization_id)
);


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


-- 5.1 Business hours schedules
CREATE TABLE schedule (
  schedule_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name           VARCHAR(100) NOT NULL,
  timezone       TEXT         NOT NULL,
  business_hours JSONB        NOT NULL  -- JSONB for flexible hours definitions
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


-- 6.1 Create parent table partitioned by closure_date
CREATE TABLE ticket (
  ticket_id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  title             VARCHAR(255)       NOT NULL,
  description       TEXT,
  created_at        TIMESTAMPTZ        NOT NULL DEFAULT now(),  -- timestamp with time zone 
  updated_at        TIMESTAMPTZ        NOT NULL DEFAULT now(),  -- timestamp with time zone 
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
) PARTITION BY RANGE (closure_date);  -- declarative range partitioning


CREATE TABLE ticket_open PARTITION OF ticket
  DEFAULT;  -- catches NULL or out-of-range closure_date rows 


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
