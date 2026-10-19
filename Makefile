PYTHON ?= python3
export PYTHONPATH := src:$(PYTHONPATH)
.PHONY: download run test report notebook check package
download:
	$(PYTHON) scripts/download_data.py
run:
	$(PYTHON) scripts/run_analysis.py
	$(PYTHON) scripts/run_sql.py
test:
	$(PYTHON) -m unittest discover -s tests -v
report:
	$(PYTHON) scripts/build_report.py
notebook:
	$(PYTHON) scripts/build_notebook.py
check: test
	$(PYTHON) scripts/validate_outputs.py
package:
	$(PYTHON) scripts/package_project.py
