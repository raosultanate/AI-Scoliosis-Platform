# Security and data handling

Version 1A is local research tooling and contains no authentication, database, or network service.
Raw data and generated outputs are Git-ignored by default.

- Do not place PHI in filenames, logs, fixtures, commits, screenshots, or the Obsidian vault.
- Verify de-identification independently; removing a name from a filename is not sufficient.
- Preserve dataset licenses and access restrictions.
- Treat reports and annotations as sensitive medical data even when source images are de-identified.
- Before any clinical deployment, perform threat modeling, access-control design, audit logging,
  retention planning, incident response, and applicable regulatory/privacy review.

