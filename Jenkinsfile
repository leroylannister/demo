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

        stage('Run Tests') {
            steps {
                script {
                    def platformConfigs = [
                        'chrome_windows': [
                            browser: 'Chrome',
                            browser_version: 'latest',
                            os: 'Windows',
                            os_version: '10'
                        ],
                        'firefox_mac': [
                            browser: 'Firefox',
                            browser_version: 'latest',
                            os: 'OS X',
                            os_version: 'Ventura'
                        ],                 
                        'samsung_mobile': [
                            device: 'Samsung Galaxy S22',
                            platform_name: 'Android',
                            platform_version: '12.0'
                        ],
                    ]

                    def selectedPlatforms = []
                    if (params.PLATFORM_SET == 'all') {
                        selectedPlatforms = platformConfigs.keySet().toList()
                    } else {
                        selectedPlatforms = [params.PLATFORM_SET]
                    }
                    
                    def testMarker = ''
                    if (params.TEST_SUITE != 'all') {
                        testMarker = "-m ${params.TEST_SUITE}"
                    }

                    if (params.PARALLEL_EXECUTION && selectedPlatforms.size() > 1) {
                        def parallelTests = [:]
                        selectedPlatforms.each { platformKey ->
                            parallelTests[platformKey] = {
                                def config = platformConfigs[platformKey]
                                def envVars = [
                                    "BROWSERSTACK_BUILD_NAME=Demo-Build-${env.BUILD_NUMBER}",
                                    "BROWSERSTACK_PROJECT_NAME=Demo-Project",
                                    "BROWSERSTACK_SESSION_NAME=${platformKey}-${env.BUILD_NUMBER}"
                                ]
                                if (config.browser) {
                                    envVars.add("BS_BROWSER=${config.browser}")
                                    envVars.add("BS_BROWSER_VERSION=${config.browser_version}")
                                    envVars.add("BS_OS=${config.os}")
                                    envVars.add("BS_OS_VERSION=${config.os_version}")
                                } else if (config.device) {
                                    envVars.add("BS_DEVICE=${config.device}")
                                    envVars.add("BS_PLATFORM_NAME=${config.platform_name}")
                                    envVars.add("BS_PLATFORM_VERSION=${config.platform_version}")
                                }

                                withEnv(envVars) {
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
                        selectedPlatforms.each { platformKey ->
                            def config = platformConfigs[platformKey]
                            def envVars = [
                                "BROWSERSTACK_BUILD_NAME=Demo-Build-${env.BUILD_NUMBER}",
                                "BROWSERSTACK_PROJECT_NAME=Demo-Project",
                                "BROWSERSTACK_SESSION_NAME=${platformKey}-${env.BUILD_NUMBER}"
                            ]
                            if (config.browser) {
                                envVars.add("BS_BROWSER=${config.browser}")
                                envVars.add("BS_BROWSER_VERSION=${config.browser_version}")
                                envVars.add("BS_OS=${config.os}")
                                envVars.add("BS_OS_VERSION=${config.os_version}")
                            } else if (config.device) {
                                envVars.add("BS_DEVICE=${config.device}")
                                envVars.add("BS_PLATFORM_NAME=${config.platform_name}")
                                envVars.add("BS_PLATFORM_VERSION=${config.platform_version}")
                            }

                            withEnv(envVars) {
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

        stage('Publish Reports and Archive Artifacts') {
            steps {
                script {
                    junit(
                        testResults: 'reports/demo_junit_*.xml',
                        allowEmptyResults: true
                    )
                    archiveArtifacts(
                        artifacts: 'reports/*.html',
                        allowEmptyArchive: true
                    )
                    archiveArtifacts(
                        artifacts: 'logs/*.log',
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
            echo 'Pipeline run has completed.'
            // Clean workspace after build to avoid stale files
            deleteDir()
        }
        success {
            echo '✅ Demo tests passed successfully!'
        }
        failure {
            echo '❌ Demo tests failed!'
            // You can add notifications here if needed
        }
        aborted {
            echo '🚫 Demo tests aborted!'
        }
    }
}
