-- BLACKOUT Graph Schema for HydraDB
-- Run once at pipeline start

-- Constraints (uniqueness)
CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.canonical_id IS UNIQUE;
CREATE CONSTRAINT claim_id IF NOT EXISTS FOR (c:Claim) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT decision_id IF NOT EXISTS FOR (d:Decision) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT document_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT message_id IF NOT EXISTS FOR (m:Message) REQUIRE m.id IS UNIQUE;
CREATE CONSTRAINT ticket_id IF NOT EXISTS FOR (t:Ticket) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT pullrequest_id IF NOT EXISTS FOR (pr:PullRequest) REQUIRE pr.id IS UNIQUE;
CREATE CONSTRAINT deal_id IF NOT EXISTS FOR (dl:Deal) REQUIRE dl.id IS UNIQUE;
CREATE CONSTRAINT project_id IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT system_id IF NOT EXISTS FOR (s:System) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT incident_id IF NOT EXISTS FOR (i:Incident) REQUIRE i.id IS UNIQUE;

-- Indexes (query performance)
CREATE INDEX claim_status IF NOT EXISTS FOR (c:Claim) ON (c.status);
CREATE INDEX message_source IF NOT EXISTS FOR (m:Message) ON (m.source_system);
CREATE INDEX document_source IF NOT EXISTS FOR (d:Document) ON (d.source_system);
CREATE INDEX person_name IF NOT EXISTS FOR (p:Person) ON (p.name);
