#!/bin/bash
# Script to test Jenkins setup locally

echo "🧪 Testing Demo Jenkins Pipeline Locally"

# Export test credentials (replace with your actual values)
export BROWSERSTACK_USERNAME="michaelzada_kKTcgR"
export BROWSERSTACK_ACCESS_KEY="voDkvRqyaPzkku9ncwt8"
export TEST_USERNAME="demouser"
export TEST_PASSWORD="testingisfun99"

# Create reports directory
mkdir -p reports

# Run tests
source .venv/bin/activate
pytest tests/ \
    --browser=chrome_windows \
    -m smoke \
    --html=reports/demo_report_local.html \
    --self-contained-html \
    -v

echo "✅ Test complete. Check reports/demo_report_local.html"