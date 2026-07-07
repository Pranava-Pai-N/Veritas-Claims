# Assumptions and Limitations

## Assumptions

### 1. Business & Process Context

- **Batch Traffic Spikes:** Assumed that the 200,000+ daily medical records are not evenly distributed across 24 hours but arrive in unpredictable traffic bursts (e.g., at clinic closing hours).

- **Onboarding Velocity:** Assumed that new clinics onboarded onto the system will provide a documented JSON schema blueprint, allowing meta-configuration updates to take effect within 1 business day .

### 2. Technical & Infrastructure Choices
- **Input Structures:** Input files are JSON documents containing a verifiable data path structure (e.g., `data.responseDetails`).

- **Storage Suitability:** A local SQLite relational database is used strictly for prototype demonstration and lightweight transactional testing. Production architectures require columnar or distributed engines- BigQuery/ PgSQL.

- **Config-Driven Domain Mappings:** Medical reference ranges, fuzzy vocabulary matrices, and clinic mapping dictionaries are maintained exclusively in external config dictionaries (JSON/YAML) to enable runtime updates without triggering infrastructure redeployments.

### 3. Data & Clinical Scope
- **Standardized Medical Scope:** The current solution focuses primarily on lab-report-style clinical content (e.g., Haemoglobin, WBC parameters) where numerical outputs dominate.

- **Schema Permissiveness:** If a test is entirely absent from an ingestion block, leaving the corresponding five canonical targets empty is safe and mathematically valid rather than failing the process transaction.

## Limitations
- The pipeline is not yet designed for large-scale distributed processing.
- Error handling is basic and relies on moving invalid files to a duplicate queue + Log files for reasoning.
- The current dashboard is a simple monitoring UI rather than a full enterprise reporting portal.
- The implementation is best suited for sample data and prototyping rather than production-grade healthcare workflows.
