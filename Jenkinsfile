pipeline {
    agent any

    // Use a single environment block to define all dynamic variables.
    // In Declarative Pipeline, you can reference built-in variables directly.
    environment {
        DOCKER_USER = 'bhargav1518'
        IMAGE_NAME = "contract-life-cycle-flask-app"
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        FULL_IMAGE_NAME = "${env.DOCKER_USER}/${env.IMAGE_NAME}"
    }

    stages {
        stage('Build Docker Image') {
            steps {
                // Use the full image name and the dynamic tag
                bat "docker build -t ${env.FULL_IMAGE_NAME}:${env.IMAGE_TAG} ."
            }
        }

        // Optional: Run Unit Tests
        stage('Run Unit Tests') {
            steps {
                // The `docker run` command will now use the correct full image name and tag
                bat "docker run --rm ${env.FULL_IMAGE_NAME}:${env.IMAGE_TAG} python -m pytest tests/"
            }
        }

        stage('Deploy to Server') {
            steps {
                script {
                    // Use a more robust try/catch block
                    try {
                        bat "docker stop clmp-container"
                    } catch (Exception e) {
                        echo "Container 'clmp-container' was not running, proceeding anyway."
                    }
                    try {
                        bat "docker rm clmp-container"
                    } catch (Exception e) {
                        echo "Container 'clmp-container' did not exist, proceeding anyway."
                    }
                }
                // This command now uses the correct full image name and tag
                bat "docker run -d --name clmp-container -p 5000:5000 ${env.FULL_IMAGE_NAME}:${env.IMAGE_TAG}"
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withDockerRegistry(credentialsId: 'dockerhub-credentials', url: 'https://index.docker.io/v1/') {
                    // Push the uniquely tagged image
                    bat "docker push ${env.FULL_IMAGE_NAME}:${env.IMAGE_TAG}"
                    
                    // Also tag and push a 'latest' version for convenience
                    bat "docker tag ${env.FULL_IMAGE_NAME}:${env.IMAGE_TAG} ${env.FULL_IMAGE_NAME}:latest"
                    bat "docker push ${env.FULL_IMAGE_NAME}:latest"
                }
            }
        }
    }
    post {
        always {
            echo 'Pipeline finished.'
        }
    }
}