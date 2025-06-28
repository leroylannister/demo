pipeline {
    agent any

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
            description: 'Which browser/OS combination(s) to test.'
        )
        choice(
            name: 'TEST_SUITE',
            choices: ['smoke', 'regression', 'all'],
            description: 'Which test suite to run.'
        )
        booleanParam(
            name: 'PARALLEL_EXECUTION',
            defaultValue: true,
            description: 'Run tests in parallel.'
        )
    }

    stages {
        stage('Clean Workspace') {
            steps {
                script {
                    echo "🧹 Cleaning workspace..."
                    deleteDir()
                    echo "Workspace cleaned."
                }
            }
        }

        stage('Checkout') {
            steps {
                echo "🔄 Checking out code..."
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

        stage('Run Tests') {
            steps {
                script {
                    // Select platforms
                    def selectedPlatforms = []
                    if (params.PLATFORM_SET == 'all') {
                        selectedPlatforms = ['chrome_windows', 'firefox_mac', 'samsung_mobile']
                    } else {
                        selectedPlatforms = [params.PLATFORM_SET]
                    }
                    
                    // Set test marker
                    def testMarker = ''
                    if (params.TEST_SUITE != 'all') {
                        testMarker = "-m ${params.TEST_SUITE}"
                    }

                    echo "🚀 Running tests on: ${selectedPlatforms.join(', ')}"

                    if (params.PARALLEL_EXECUTION && selectedPlatforms.size() > 1) {
                        // Parallel execution
                        def parallelTests = [:]
                        selectedPlatforms.each { platformKey ->
                            parallelTests[platformKey] = {
                                withEnv(["BROWSER_TYPE=${platformKey}"]) {
                                    sh """
                                        source .venv/bin/activate
                                        mkdir -p reports
                                        pytest tests/ \\
                                            ${testMarker} \\
                                            --html=reports/demo_report_${platformKey}.html \\
                                            --self-contained-html \\
                                            --junitxml=reports/demo_junit_${platformKey}.xml \\
                                            -v
                                    """
                                }
                            }
                        }
                        parallel parallelTests
                    } else {
                        // Sequential execution
                        selectedPlatforms.each { platformKey ->
                            withEnv(["BROWSER_TYPE=${platformKey}"]) {
                                sh """
                                    source .venv/bin/activate
                                    mkdir -p reports
                                    pytest tests/ \\
                                        ${testMarker} \\
                                        --html=reports/demo_report_${platformKey}.html \\
                                        --self-contained-html \\
                                        --junitxml=reports/demo_junit_${platformKey}.xml \\
                                        -v
                                """
                            }
                        }
                    }
                }
            }
        }

        stage('Publish Reports') {
            steps {
                script {
                    echo "📊 Publishing reports..."
                    
                    junit(
                        testResults: 'reports/demo_junit_*.xml',
                        allowEmptyResults: true
                    )
                    archiveArtifacts(
                        artifacts: 'reports/*.html',
                        allowEmptyArchive: true
                    )
                    archiveArtifacts(
                        artifacts: 'screenshots/*.png',
                        allowEmptyArchive: true
                    )
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports',
                        reportFiles: '*.html',
                        reportName: 'Demo Test Reports'
                    ])
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline completed.'
            deleteDir()
        }
        success {
            echo '✅ Tests passed!'
        }
        failure {
            echo '❌ Tests failed!'
        }
    }
}