// Jenkinsfile for Demo Selenium Tests with BrowserStack Integration

pipeline {
    agent any // Designates that the pipeline can run on any available Jenkins agent

    // Global options for the pipeline
    options {
        // Keeps only the last 10 successful builds' logs and artifacts
        buildDiscarder(logRotator(numToKeepStr: '10'))
        // Sets a timeout for the entire pipeline
        timeout(time: 30, unit: 'MINUTES')
        // Adds timestamps to the console output for easier debugging
        timestamps()
    }

    // Define environment variables
    environment {
        // Load secure credentials from Jenkins Credentials Store
        BROWSERSTACK_USERNAME = credentials('browserstack-username')
        BROWSERSTACK_ACCESS_KEY = credentials('browserstack-access-key')
        TEST_USERNAME = credentials('test-username')
        TEST_PASSWORD = credentials('test-password')

        // Define explicit paths for 'uv' (Python package manager) if not globally available
        // Ensures 'uv' and other tools are found in the execution environment
        PATH = "${env.HOME}/.local/bin:${env.HOME}/.cargo/bin:${env.PATH}"
    }

    // Define build parameters for user input
    parameters {
        // Dropdown for selecting browser/OS combinations or 'all' predefined ones
        choice(
            name: 'PLATFORM_SET',
            choices: [
                'all',               // Option to run all predefined combinations
                'chrome_windows',    // Specific combination
                'firefox_mac',       // Specific combination
                'edge_windows',      // Specific combination
                'safari_mac',        // Specific combination
                'samsung_mobile',    // Specific mobile device combination
                'iphone_mobile'      // Specific iPhone combination
            ],
            description: 'Which browser/OS combination(s) to test on BrowserStack.'
        )
        // Dropdown for selecting test suite to run
        choice(
            name: 'TEST_SUITE',
            choices: ['smoke', 'regression', 'all'],
            description: 'Which Demo test suite to run (via pytest markers).'
        )
        // Boolean parameter for parallel execution
        booleanParam(
            name: 'PARALLEL_EXECUTION',
            defaultValue: true,
            description: 'Run tests for selected platforms in parallel.'
        )
    }

    // Define the stages of the pipeline
    stages {
        // Stage for checking out the source code
        stage('Checkout') {
            steps {
                echo "🔄 Checking out Demo project..."
                // Checks out the source code from the configured SCM (GitHub)
                checkout scm
            }
        }

        // Stage for setting up the Python environment and dependencies
        stage('Setup Environment') {
            steps {
                script {
                    // Check if 'uv' is installed, and install it if not
                    sh '''
                        if ! command -v uv &> /dev/null; then
                            echo "Installing UV..."
                            curl -LsSf https://astral.sh/uv/install.sh | sh
                        fi
                        
                        # Verify 'uv' installation
                        uv --version
                        
                        # Create a virtual environment using 'uv'
                        uv venv
                        
                        # Activate the virtual environment and install project dependencies
                        # `uv pip sync` installs exact versions from pyproject.toml
                        # `uv pip install -e ".[dev]"` installs editable dev dependencies
                        source .venv/bin/activate
                        uv pip sync pyproject.toml
                        uv pip install -e ".[dev]"
                        
                        # Verify pytest is available
                        pytest --version
                    '''
                }
            }
        }

        // Stage for running the automated tests on BrowserStack
        stage('Run Tests') {
            steps {
                script {
                    // Define a map of common BrowserStack platform configurations
                    // These keys correspond to the PLATFORM_SET parameter choices
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
                            os_version: 'Sonoma'
                        ],
                        'edge_windows': [
                            browser: 'Edge',
                            browser_version: 'latest',
                            os: 'Windows',
                            os_version: '10'
                        ],
                        'safari_mac': [
                            browser: 'Safari',
                            browser_version: 'latest',
                            os: 'OS X',
                            os_version: 'Sonoma'
                        ],
                        'samsung_mobile': [
                            device: 'Samsung Galaxy S22',
                            platform_name: 'Android',
                            platform_version: '12.0'
                        ],
                        'iphone_mobile': [
                            device: 'iPhone 15',
                            platform_name: 'iOS',
                            platform_version: '17'
                        ]
                    ]

                    def selectedPlatforms = []

                    // Determine which platforms to test based on user input
                    if (params.PLATFORM_SET == 'all') {
                        // If 'all' is selected, run tests on all defined platform configurations
                        selectedPlatforms = platformConfigs.keySet().toList()
                    } else {
                        // Otherwise, use the single selected platform
                        selectedPlatforms = [params.PLATFORM_SET]
                    }
                    
                    // Build the pytest marker string if a specific test suite is chosen
                    def testMarker = ''
                    if (params.TEST_SUITE != 'all') {
                        testMarker = "-m ${params.TEST_SUITE}"
                    }

                    // Check if parallel execution is enabled and if there's more than one platform to test
                    if (params.PARALLEL_EXECUTION && selectedPlatforms.size() > 1) {
                        def parallelTests = [:]
                        // Create a separate parallel branch for each selected platform
                        selectedPlatforms.each { platformKey ->
                            parallelTests[platformKey] = {
                                // Get the specific configuration for the current platform
                                def config = platformConfigs[platformKey]
                                
                                // Set environment variables for BrowserStack configuration
                                def envVars = [
                                    "BROWSERSTACK_BUILD_NAME=Demo-Build-${env.BUILD_NUMBER}",
                                    "BROWSERSTACK_PROJECT_NAME=Demo-Project",
                                    "BROWSERSTACK_SESSION_NAME=${platformKey}-${env.BUILD_NUMBER}"
                                ]
                                
                                // Add platform-specific environment variables
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
                                        # Activate the virtual environment
                                        source .venv/bin/activate
                                        
                                        # Create reports directory if it doesn't exist
                                        mkdir -p reports
                                        
                                        # Run pytest with environment-based configuration
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
                        // Execute tests in parallel
                        parallel parallelTests
                    } else {
                        // If parallel execution is off or only one platform is selected, run sequentially
                        selectedPlatforms.each { platformKey ->
                            def config = platformConfigs[platformKey]
                            
                            // Set environment variables for BrowserStack configuration
                            def envVars = [
                                "BROWSERSTACK_BUILD_NAME=Demo-Build-${env.BUILD_NUMBER}",
                                "BROWSERSTACK_PROJECT_NAME=Demo-Project",
                                "BROWSERSTACK_SESSION_NAME=${platformKey}-${env.BUILD_NUMBER}"
                            ]
                            
                            // Add platform-specific environment variables
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
                                    # Activate the virtual environment
                                    source .venv/bin/activate
                                    
                                    # Create reports directory if it doesn't exist
                                    mkdir -p reports
                                    
                                    # Run pytest with environment-based configuration
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

        // Stage for publishing test reports and archiving artifacts
        stage('Publish Reports and Archive Artifacts') {
            steps {
                script {
                    // Archive JUnit XML test results for Jenkins' built-in reporting
                    junit(
                        testResults: 'reports/demo_junit_*.xml',
                        allowEmptyResults: true
                    )

                    // Archive HTML reports
                    archiveArtifacts(
                        artifacts: 'reports/*.html',
                        allowEmptyArchive: true
                    )

                    // Archive log files
                    archiveArtifacts(
                        artifacts: 'logs/*.log',
                        allowEmptyArchive: true
                    )

                    // Archive screenshots (fixed typo: archiveAartifacts -> archiveArtifacts)
                    archiveArtifacts(
                        artifacts: 'screenshots/*.png',
                        allowEmptyArchive: true
                    )

                    // Publish HTML reports using the HTML Publisher Plugin
                    publishHTML([
                        allowMissing: false,            // Fail build if report files are missing
                        alwaysLinkToLastBuild: true,    // Always link to the latest build's report
                        keepAll: true,                  // Keep historical reports
                        reportDir: 'reports',           // Directory containing HTML reports
                        reportFiles: '*.html',          // Pattern for report files
                        reportName: 'Demo Test Reports' // Name displayed in Jenkins UI
                    ])
                }
            }
        }
    }

    // Post-build actions (run after all stages complete)
    post {
        // Actions to run always, regardless of the pipeline's outcome
        always {
            // No steps block needed - direct commands only
            echo 'Pipeline run has completed.'
            
            // Clean up workspace if needed
            cleanWs(
                cleanWhenNotBuilt: false,
                deleteDirs: true,
                disableDeferredWipeout: true,
                notFailBuild: true,
                patterns: [[pattern: '.venv/**', type: 'INCLUDE']]
            )
        }
        // Actions to run if the pipeline succeeds
        success {
            echo '✅ Demo tests passed successfully!'
        }
        // Actions to run if the pipeline fails
        failure {
            echo '❌ Demo tests failed!'
            
            // Send notification if needed
            // emailext(
            //     subject: "Build Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
            //     body: "The build failed. Check the console output for details.",
            //     to: 'team@example.com'
            // )
        }
        // Actions to run if the pipeline is aborted
        aborted {
            echo '🚫 Demo tests aborted!'
        }
    }
}