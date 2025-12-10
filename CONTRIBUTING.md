# **Contributing Guidelines**

Thank you for your interest in contributing to the **Chicago Crime Spatial Analysis & Forecasting Platform**.
This document outlines the contribution process, coding standards, and expectations for maintainers and collaborators.

Contributions of all kinds are welcome, including feature development, documentation improvements, performance optimisation, bug reports, and model enhancements.

---

## **1. Code of Conduct**

All contributors are expected to adhere to respectful, professional conduct.
Please review the project’s `CODE_OF_CONDUCT.md` before participating.

---

## **2. How to Contribute**

### **2.1 Reporting Issues**

If you encounter a bug, inconsistency, or unexpected behaviour:

1. Check the existing issues to ensure it has not already been reported.
2. Open a new issue and include:

   * A clear, concise description of the problem
   * Steps to reproduce
   * Expected behaviour
   * Error logs or screenshots
   * Your environment (OS, Python version, package versions)

High-quality issue reports accelerate the debugging process significantly.

---

### **2.2 Requesting Features**

If you have a proposal for a new capability:

1. Review the existing roadmap or open issues.
2. Open a **Feature Request** issue describing:

   * The motivation
   * The intended use case
   * Proposed API/UI changes
   * Any dependencies or implications on performance

Feature requests are evaluated based on impact, feasibility, and alignment with project objectives.

---

### **2.3 Submitting Pull Requests**

Before starting any major work, please open an issue first so that your proposal can be discussed.

#### **PR Requirements**

A Pull Request must:

* Target the `main` or the appropriate development branch
* Pass all tests and linting checks
* Contain clean, well-documented code
* Modify only what is necessary
* Include unit tests for new functionality (where applicable)

#### **PR Process**

1. Fork the repository.
2. Create a feature branch:

   ```
   git checkout -b feature/your-feature-name
   ```
3. Make commits with clear, descriptive messages.
4. Push your branch and open a Pull Request.
5. Participate in the code review cycle until approved.

Maintainers reserve the right to request changes for clarity, consistency, or architectural alignment.

---

## **3. Development Environment**

### **3.1 Setup**

Create and activate a Python virtual environment:

```
python -m venv crime_env
source crime_env/bin/activate        # macOS/Linux
crime_env\Scripts\activate           # Windows
```

Install dependencies:

```
pip install -r requirements.txt
```

### **3.2 Running the Pipeline**

```
python run_pipeline.py
```

### **3.3 Launching the Dashboard**

```
python run_app.py
```

Ensure the pipeline has been run before using the dashboard so required model output files exist.

---

## **4. Coding Standards**

### **4.1 Style**

This project follows:

* **PEP 8** for Python code
* **PEP 257** for docstrings
* Clear modular architecture across `src/`

Please maintain consistent naming conventions and avoid unnecessary complexity.

---

### **4.2 Documentation**

Every function should include:

* Purpose and behaviour
* Parameter documentation
* Return value descriptions
* Expected input formats (especially for GeoDataFrames)

Modules must include a top-level description of their role in the system.

---

### **4.3 Geospatial Data Practices**

When working with GeoDataFrames:

* Always confirm coordinate reference systems (`gdf.crs`).
* Use EPSG:4326 for dashboard outputs.
* Avoid geometry mutations without copying the underlying GeoDataFrame.

For spatial weights or heavy computations, ensure that performance implications are considered.

---

## **5. Model Development Guidelines**

When enhancing the modelling workflow (e.g., adding a new regression model):

1. Ensure reproducibility.
2. Log model assumptions and diagnostics.
3. Include fallback paths for large datasets (as with GWR).
4. Provide relevant metrics in the output parquet file.
5. Add appropriate visual integration in the dashboard (if intended for end-users).

---

## **6. Testing**

Any new analytical or GIS functionality should include:

* Unit tests for pure Python logic
* Validation tests comparing expected vs actual geospatial behaviour
* Safeguards around CRS, NaN handling, and index alignment

Testing guidelines will be expanded as the project matures.

---

## **7. File Structure Expectations**

Contributors should preserve the existing structure:

```
app/             # Dash dashboard
data/raw/        # Input datasets
data/processed/  # Outputs (generated)
src/             # Core analytical engine
```

Avoid placing generated output inside the source directory.

---

## **8. Performance and Optimisation**

When improving performance:

* Prefer vectorised GeoPandas/Pandas operations
* Minimise repeated spatial joins
* Cache intermediate results when appropriate
* Avoid unnecessary deep copies of large dataframes
* Consider algorithmic complexity for models running on >5,000 grid cells

Performance regressions will not be accepted unless justified.

---

## **9. Security and Data Ethics**

Because the project may handle real-world crime data:

* Never expose raw sensitive datasets in commits
* Avoid storing personally identifiable information
* Ensure reproducibility without compromising privacy

---

## **10. Contribution Recognition**

Contributors will be acknowledged in project release notes and documentation.
Substantial contributions may result in co-authorship opportunities for academic publications.

---

## **11. Contact**

For questions, clarifications, or collaboration proposals, please open an issue or contact the project maintainer via the repository discussion board.