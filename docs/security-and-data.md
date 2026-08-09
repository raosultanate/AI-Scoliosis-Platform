# Security and data handling

Version 1A is research tooling with a local FastAPI network service, a responsive browser interface,
and no authentication or database. The current browser preview does not transmit a selected real
X-ray to the server; only the bundled synthetic fixture can be analyzed through the API. Raw data
and generated outputs are Git-ignored by default.

- Do not place PHI in filenames, logs, fixtures, commits, screenshots, or the Obsidian vault.
- Verify de-identification independently; removing a name from a filename is not sufficient.
- Preserve dataset licenses and access restrictions.
- Treat reports and annotations as sensitive medical data even when source images are de-identified.
- Do not expose the development service to untrusted networks or accept real medical images until
  authentication, authorization, upload validation, retention, and deletion controls are designed.
- Before any clinical deployment, perform threat modeling, access-control design, audit logging,
  retention planning, incident response, and applicable regulatory/privacy review.
