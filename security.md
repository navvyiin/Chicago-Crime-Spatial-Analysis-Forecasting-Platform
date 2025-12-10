# **Security Policy**

## **Supported Versions**

The following table describes which versions of the project currently receive security updates.

| Version                      | Supported           |
| ---------------------------- | ------------------- |
| `main` branch                | ✔️ Yes              |
| Tagged releases `< 1.0`      | ❌ No                |
| Development feature branches | ⚠️ Best-effort only |

Security fixes are applied only to the latest stable release and the `main` branch unless otherwise stated.

---

## **Reporting a Vulnerability**

We take the security of this project seriously.
If you discover a security issue or vulnerability, **please do not open a public GitHub issue**.

Instead, contact the maintainers directly at:

📧 **navalg@gmail.com**

When reporting a vulnerability, please include:

* A clear description of the issue
* Steps to reproduce the vulnerability
* Any relevant logs, screenshots, or proof-of-concept code
* Your suggested fix (if available)
* Your contact information for follow-up

We aim to respond within **72 hours**, and if validated, issue a patch or mitigation within **7–14 days** depending on severity.

---

## **Vulnerability Disclosure Process**

Once a report is received:

1. The maintainers review and validate the issue.
2. A severity rating is assigned using the **CVSS v3.1** scoring system.
3. A fix is developed privately in a restricted branch.
4. The reporter is kept informed of progress.
5. A patched release is published.
6. A public advisory is posted **after** users have an opportunity to upgrade.

If the reporter wishes, credit will be given in the release notes.

---

## **Security Best Practices for Contributors**

When contributing code, please ensure:

* No secrets, credentials, or API keys are committed.
* Cryptographic operations use established libraries rather than custom code.
* External dependencies are pinned to safe versions.
* Data inputs—especially user-generated inputs—are validated and sanitised.
* Spatial datasets with sensitive attributes (if any) are handled according to applicable data regulations (GDPR, HIPAA, local statutes).

---

## **Dependency Security**

This project relies on geospatial and machine-learning libraries. To reduce supply-chain risk:

* Keep dependencies updated via `pip-tools` or `dependabot` (optional).
* Review the release notes for any dependency with native extensions (GDAL, shapely, pyproj, numba, etc.).
* Never install packages from untrusted sources.
* Avoid running external scripts or Jupyter notebooks without review.

---

## **Responsible Use**

This repository analyses real-world crime patterns.
Users and contributors must:

* Avoid attempts to deanonymise individuals or sensitive locations.
* Use the model outputs for research, civic analytics, or policy evaluation—not improper surveillance.
* Follow all local and national laws regarding spatial data use.

Misuse of the project is strictly discouraged.