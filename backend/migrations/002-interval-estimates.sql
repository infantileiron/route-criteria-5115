-- 002: interval estimates and sampling basis (for databases created before this feature).
-- Fresh installs get these columns/tables from SQLAlchemy metadata; run once on existing MySQL.
-- Existing decision_runs/reports are untouched: old rows get empty estimate metadata and an empty basis.
ALTER TABLE decision_runs ADD COLUMN estimate_id VARCHAR(80) NOT NULL DEFAULT '';
ALTER TABLE decision_runs ADD COLUMN samples INT NOT NULL DEFAULT 0;
ALTER TABLE decision_runs ADD COLUMN seed INT NOT NULL DEFAULT 0;
ALTER TABLE decision_reports ADD COLUMN basis JSON NULL;
UPDATE decision_reports SET basis = JSON_OBJECT() WHERE basis IS NULL;
ALTER TABLE decision_reports MODIFY COLUMN basis JSON NOT NULL;
CREATE TABLE estimate_profiles (
 id VARCHAR(80) PRIMARY KEY,
 name VARCHAR(160) NOT NULL UNIQUE,
 dataset_id VARCHAR(80) NOT NULL,
 ranges JSON NOT NULL,
 created_at VARCHAR(64) NOT NULL,
 CONSTRAINT fk_estimate_dataset FOREIGN KEY (dataset_id) REFERENCES alternative_datasets(id)
);
