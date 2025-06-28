pipeline {
    agent any // Designates that the pipeline can run on any available Jenkins agent

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }

    environment {
        BROWSERSTACK_USERNAME = credentials('browserstack-username')
        BROWSERSTACK_ACCESS_KEY = credentials('browserstack-access-key')
        TEST_USERNAME = credentials('test-username')
        TEST_PASSWORD = credentials('test-password')
        PATH = "${env.HOME}/.local/bin:${env.HOME}/.cargo/bin:${env.PATH}"
        USE_BROWSERSTACK = 'true'  // Enable BrowserStack by default
    }

    parameters {
        choice(
            name: 'PLATFORM_SET',
            choices: [
                'all',
                'chrome_windows',
                'firefox_mac',
                'samsung_mobile',
            ],
            description: 'Which browser/OS combination(s) to test on BrowserStack.'
        )
        choice(
            name: 'TEST_SUITE',
            choices: ['smoke', 'regression', 'all'],
            description: 'Which Demo test suite to run (via pytest markers).'
        )
        booleanParam(
            name: 'PARALLEL_EXECUTION',
            defaultValue: true,
            description: 'Run tests for selected platforms in parallel.'
        )
        booleanParam(
            name: 'RUN_LOCAL',
            defaultValue: false,
            description: 'Run tests locally instead of on BrowserStack (for debugging).'
        )
    }

    stages {
        stage('Clean Workspace') {
            steps {
                script {
                    echo "🧹 Cleaning workspace before checkout..."
                    deleteDir()  // <-- Added: cleans entire workspace for fresh checkout
                    echo "Workspace cleaned."
                }
            }
        }

        stage('Checkout') {
            steps {
                echo "🔄 Checking out Demo project..."
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
                script {
                    sh '''
                        if ! command -v uv &> /dev/null; then
                            echo "Installing UV..."
                            curl -LsSf https://astral.sh/uv/install.sh | sh
                        fi
                        
                        uv --version
                        uv venv
                        source .venv/bin/activate
                        uv pip sync pyproject.toml
                        uv pip install -e ".[dev]"
                        pytest --version
                    '''
                }
            }
        }

        stage('Validate BrowserStack Credentials') {
            when {
                not { params.RUN_LOCAL }
            }
            steps {
                script {
                    sh '''
                        echo "🔍 Validating BrowserStack credentials..."
                        if [ -z "$BROWSERSTACK_USERNAME" ] || [ -z "$BROWSERSTACK_ACCESS_KEY" ]; then
                            echo "❌ BrowserStack credentials not found!"
                            exit 1
                        fi
                        
                        # Test BrowserStack API connection
                        curl -u "$BROWSERSTACK_USERNAME:$BROWSERSTACK_ACCESS_KEY" \\
                             https://api.browserstack.com/automate/plan.json \\
                             -f -s -o /dev/null || {
                            echo "❌ Failed to connect to BrowserStack API!"
                            exit 1
                        }
                        echo "✅ BrowserStack credentials validated successfully"
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // Define which platforms to test
                    def selectedPlatforms = []
                    if (params.PLATFORM_SET == 'all') {
                        selectedPlatforms = ['chrome_windows', 'firefox_mac', 'samsung_mobile']
                    } else {
                        selectedPlatforms = [params.PLATFORM_SET]
                    }
                    
                    def testMarker = ''
                    if (params.TEST_SUITE != 'all') {
                        testMarker = "-m ${params.TEST_SUITE}"
                    }

                    // Determine execution mode
                    def useBrowserStack = !params.RUN_LOCAL
                    def buildName = "Demo-Build-${env.BUILD_NUMBER}"
                    
                    echo "🚀 Starting tests..."
                    echo "Platforms: ${selectedPlatforms.join(', ')}"
                    echo "Test Suite: ${params.TEST_SUITE}"
                    echo "BrowserStack: ${useBrowserStack ? 'Enabled' : 'Disabled (Local)'}"
                    echo "Parallel: ${params.PARALLEL_EXECUTION}"

                    if (params.PARALLEL_EXECUTION && selectedPlatforms.size() > 1) {
                        def parallelTests = [:]
                        selectedPlatforms.each { platformKey ->
                            parallelTests[platformKey] = {
                                def envVars = [
                                    "BROWSER_TYPE=${platformKey}",
                                    "USE_BROWSERSTACK=${useBrowserStack}",
                                    "BUILD_NUMBER=${env.BUILD_NUMBER}",
                                    "JOB_NAME=${env.JOB_NAME}"
                                ]

                                withEnv(envVars) {
                                    sh """
                                        source .venv/bin/activate
                                        mkdir -p reports
                                        echo "🧪 Running ${platformKey} tests..."
                                        pytest tests/ \\
                                            ${testMarker} \\
                                            --html=reports/demo_report_${platformKey}.html \\
                                            --self-contained-html \\
                                            --junitxml=reports/demo_junit_${platformKey}.xml \\
                                            -v \\
                                            --tb=short
                                    """
                                }
                            }
                        }
                        parallel parallelTests
                    } else {
                        selectedPlatforms.each { platformKey ->
                            def envVars = [
                                "BROWSER_TYPE=${platformKey}",
                                "USE_BROWSERSTACK=${useBrowserStack}",
                                "BUILD_NUMBER=${env.BUILD_NUMBER}",
                                "JOB_NAME=${env.JOB_NAME}"
                            ]

                            withEnv(envVars) {
                                sh """
                                    source .venv/bin/activate
                                    mkdir -p reports
                                    echo "🧪 Running ${platformKey} tests..."
                                    pytest tests/ \\
                                        ${testMarker} \\
                                        --html=reports/demo_report_${platformKey}.html \\
                                        --self-contained-html \\
                                        --junitxml=reports/demo_junit_${platformKey}.xml \\
                                        -v \\
                                        --tb=short
                                """
                            }
                        }
                    }
                }
            }
        }

        stage('Publish Reports and Archive Artifacts') {
            steps {
                script {
                    echo "📊 Publishing test reports..."
                    
                    // Publish JUnit test results
                    junit(
                        testResults: 'reports/demo_junit_*.xml',
                        allowEmptyResults: true
                    )
                    
                    // Archive HTML reports
                    archiveArtifacts(
                        artifacts: 'reports/*.html',
                        allowEmptyArchive: true
                    )
                    
                    // Archive logs if they exist
                    archiveArtifacts(
                        artifacts: 'logs/*.log',
                        allowEmptyArchive: true
                    )
                    
                    // Archive screenshots if they exist
                    archiveArtifacts(
                        artifacts: 'screenshots/*.png',
                        allowEmptyArchive: true
                    )
                    
                    // Publish HTML reports
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports',
                        reportFiles: '*.html',
                        reportName: 'Demo Test Reports'
                    ])
                    
                    echo "✅ Reports published successfully"
                }
            }
        }

        stage('BrowserStack Session Links') {
            when {
                not { params.RUN_LOCAL }
            }
            steps {
                script {
                    sh '''
                        echo "🔗 BrowserStack Dashboard Links:"
                        echo "Build Dashboard: https://automate.browserstack.com/dashboard/v2/builds"
                        echo "Build Name: Demo-Build-${BUILD_NUMBER}"
                        echo ""
                        echo "📱 Individual Session Links:"
                        echo "Note: Session URLs will be available in test logs with session IDs"
                    '''
                }
            }
        }
    }

    post {
        always {
            script {
                echo "🏁 Pipeline completed at: ${new Date()}"
                
                // Display summary
                sh '''
                    echo "📋 Test Execution Summary:"
                    if [ -d "reports" ]; then
                        echo "HTML Reports generated: $(ls reports/*.html 2>/dev/null | wc -l)"
                        echo "JUnit Reports generated: $(ls reports/*.xml 2>/dev/null | wc -l)"
                    fi
                    if [ -d "screenshots" ]; then
                        echo "Screenshots captured: $(ls screenshots/*.png 2>/dev/null | wc -l)"
                    fi
                '''
            }
            
            // Clean workspace after build to avoid stale files
            deleteDir()
        }
        success {
            echo '✅ Demo tests passed successfully!'
            script {
                if (!params.RUN_LOCAL) {
                    echo "🎉 BrowserStack sessions completed successfully!"
                    echo "View results at: https://automate.browserstack.com/dashboard/v2/builds"
                }
            }
        }
        failure {
            echo '❌ Demo tests failed!'
            script {
                echo "💡 Troubleshooting tips:"
                echo "1. Check individual test reports in the artifacts"
                echo "2. Review screenshots for visual debugging"
                echo "3. Verify BrowserStack session logs if using BrowserStack"
                if (!params.RUN_LOCAL) {
                    echo "4. Check BrowserStack dashboard for session details"
                }
            }
        }
        aborted {
            echo '🚫 Demo tests aborted!'
        }
        unstable {
            echo '⚠️  Demo tests completed with some failures!'
        }
    }
}