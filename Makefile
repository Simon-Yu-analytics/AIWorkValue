PYTHON ?= python3
export PYTHONPATH := src:$(PYTHONPATH)
.PHONY: download run sql extension research dashboard test report notebook check package
download:
	$(PYTHON) scripts/download_data.py
run:
	$(PYTHON) scripts/run_analysis.py
	$(PYTHON) scripts/run_sql.py
	$(PYTHON) scripts/build_task_extension.py
	$(PYTHON) scripts/validate_research.py
sql:
	$(PYTHON) scripts/run_sql.py
extension:
	$(PYTHON) scripts/build_task_extension.py
research:
	$(PYTHON) scripts/validate_research.py
dashboard:
	$(PYTHON) -m streamlit run dashboard/app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true
test:
	$(PYTHON) -m unittest discover -s tests -v
report: extension
	$(PYTHON) scripts/build_report.py
notebook:
	$(PYTHON) scripts/build_notebook.py
check: test
	$(PYTHON) scripts/validate_outputs.py
package:
	$(PYTHON) scripts/package_project.py
