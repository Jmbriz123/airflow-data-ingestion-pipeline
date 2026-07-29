-- create DB table matching the YAML schema

CREATE TABLE IF NOT EXISTS public.customer_care_emails (
    subject                  TEXT                     NOT NULL,
    sender                   TEXT                     NOT NULL,
    receiver                 TEXT                     NOT NULL,
    "timestamp"              TIMESTAMP WITH TIME ZONE NOT NULL,
    message_body             TEXT                     NOT NULL,
    thread_id                TEXT                     NOT NULL,
    email_types              JSONB,
    email_status             TEXT                     NOT NULL,
    email_criticality        TEXT                     NOT NULL,
    product_types            JSONB,
    agent_effectivity        TEXT,
    agent_efficiency         TEXT,
    customer_satisfaction    NUMERIC,

    CONSTRAINT customer_care_emails_pkey
        PRIMARY KEY (thread_id, "timestamp")
);



