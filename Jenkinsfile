pipeline {
    agent any
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }
    
    environment {
        // Load secure credentials from Jenkins store
        BROWSERSTACK_USERNAME = credentials('browserstack-username')
        BROWSERSTACK_ACCESS_KEY = credentials('browserstack-access-key')
        TEST_USERNAME = credentials('test-username')
        TEST_PASSWORD = credentials('test-password')
        
        // Define an explicit path for UV if needed (your current PATH setup is good)
        PATH = "${env.HOME}/.local/bin:${env.HOME}/.cargo/bin:${env.PATH}"
    }
    
    parameters { /* ... (your existing parameters) ... */ }
    
    stages {
        stage('Checkout') {
            steps {
                echo "🔄 Checking out Demo project..."
                checkout scm
            }
        }
        
        stage('Load Environment Variables') { // NEW STAGE
            steps {
                script {
                    // This reads the .env file and sets variables in the current build's environment
                    // Assumes you have the EnvInject plugin or similar
                    // The .env file must be at the root of your checked-out repo
                    sh 'cat .env >> ./.jenkins_env_vars' // Creates a temp file to parse
                    load_env '.jenkins_env_vars' // This step loads from the file
                    sh 'rm ./.jenkins_env_vars' // Clean up temp file
                    
                    // You can echo to verify (secrets will be masked by Jenkins)
                    echo "Loaded ENVIRONMENT: ${env.ENVIRONMENT}"
                    echo "Loaded BASE_URL: ${env.BASE_URL}"
                }
            }
        }
        
        stage('Setup Environment') { /* ... (your existing setup stage) ... */ }
        
        stage('Run Tests') {
            steps {
                script {
                    // Your tests will now automatically use ENVIRONMENT, BASE_URL etc.
                    // For example, if pytest is configured to read from env vars:
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
        
        stage('Publish Reports and Archive Artifacts') { /* ... (your existing publish stage) ... */ }
    }
    
    post { /* ... (your existing post-build actions) ... */ }
}
