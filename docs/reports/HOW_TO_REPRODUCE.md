# How to repeat the Part-3 test run

    pip install -r requirements.txt -r requirements-dev.txt
    export GITHUB_ACTIONS=true              (makes Django use SQLite)
    coverage run manage.py test -v 2 > docs/reports/unit_test_log.txt 2>&1
    coverage report
    coverage html && coverage xml && coverage json
    python scripts/performance_test.py > docs/reports/performance_test_output.txt
    python scripts/system_validation.py     (writes system_validation_results.json)
    python scripts/build_reports.py         (rebuilds the Markdown reports)

unit_test_results.xml comes from the unittest-xml-reporting Django runner
(xmlrunner.extra.djangotestrunner.XMLTestRunner with TEST_OUTPUT_FILE_NAME=results.xml).
coverage.py writes a .gitignore inside docs/reports/coverage_html. Delete it before committing or git will skip the HTML files.
