pipeline {
    agent any
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }
    
    environment {
        // Load credentials from Jenkins
        BROWSERSTACK_USERNAME = credentials('browserstack-username')
        BROWSERSTACK_ACCESS_KEY = credentials('browserstack-access-key')
        TEST_USERNAME = credentials('test-username')
        TEST_PASSWORD = credentials('test-password')
        
        // Python/UV paths - adjust based on your Jenkins setup
        PATH = "${env.HOME}/.local/bin:${env.HOME}/.cargo/bin:${env.PATH}"
    }
    
    parameters {
        choice(
            name: 'BROWSER_SET',
            choices: ['all', 'chrome_windows', 'firefox_mac', 'samsung_mobile'],
            description: 'Which browser(s) to test on for Demo'
        )
        choice(
            name: 'TEST_SUITE',
            choices: ['smoke', 'regression', 'all'],
            description: 'Which Demo test suite to run'
        )
        booleanParam(
            name: 'PARALLEL_EXECUTION',
            defaultValue: true,
            description: 'Run Demo tests in parallel'
        )
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo "🔄 Checking out Demo project..."
                checkout scm
            }
        }
        
        stage('Setup Environment') {
            steps {
                script {
                    // Check if UV is installed, if not install it
                    sh '''
                        if ! command -v uv &> /dev/null; then
                            echo "Installing UV..."
                            curl -LsSf https://astral.sh/uv/install.sh | sh
                        fi
                        
                        # Verify UV installation
                        uv --version
                        
                        # Create virtual environment
                        uv venv
                        
                        # Install dependencies
                        source .venv/bin/activate
                        uv pip sync pyproject.toml
                        uv pip install -e ".[dev]"
                        
                        # Verify pytest is available
                        pytest --version
                    '''
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    def browsers = []
                    
                    if (params.BROWSER_SET == 'all') {
                        browsers = ['chrome_windows', 'firefox_mac', 'samsung_mobile']
                    } else {
                        browsers = [params.BROWSER_SET]
                    }
                    
                    def testMarker = ''
                    if (params.TEST_SUITE != 'all') {
                        testMarker = "-m ${params.TEST_SUITE}"
                    }
                    
                    if (params.PARALLEL_EXECUTION && browsers.size() > 1) {
                        // Run tests in parallel
                        def parallelTests = [:]
                        
                        browsers.each { browser ->
                            parallelTests[browser] = {
                                sh """
                                    source .venv/bin/activate
                                    pytest tests/ \
                                        --browser=${browser} \
                                        ${testMarker} \
                                        --html=reports/demo_report_${browser}.html \
                                        --self-contained-html \
                                        --junitxml=reports/demo_junit_${browser}.xml \
                                        -v
                                """
                            }
                        }
                        
                        parallel parallelTests
                    } else {
                        // Run tests sequentially
                        browsers.each { browser ->
                            sh """
                                source .venv/bin/activate
                                pytest tests/ \
                                    --browser=${browser} \
                                    ${testMarker} \
                                    --html=reports/demo_report_${browser}.html \
                                    --self-contained-html \
                                    --junitxml=reports/demo_junit_${browser}.xml \
                                    -v
                            """
                        }
                    }
                }
            }
        }
    }
    
    post {
        always {
            // Archive test results
            junit 'reports/demo_junit_*.xml'
            
            // Archive HTML reports
            archiveArtifacts artifacts: 'reports/*.html', allowEmptyArchive: true
            
            // Archive logs
            archiveArtifacts artifacts: 'logs/*.log', allowEmptyArchive: true
            
            // Archive screenshots
            archiveArtifacts artifacts: 'screenshots/*.png', allowEmptyArchive: true
            
            // Publish HTML reports
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'reports',
                reportFiles: '*.html',
                reportName: 'Demo Test Reports'
            ])
        }
        
        success {
            echo '✅ Demo tests passed successfully!'
        }
        
        failure {
            echo '❌ Demo tests failed!'
        }
    }
}