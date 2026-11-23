pipeline {
    agent any

    environment {
        AWS_REGION          = 'us-east-1'
        AWS_ACCOUNT_ID      = '123456789012' // Replace with your AWS Account ID
        ECR_REGISTRY        = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        IMAGE_TAG           = "${env.BUILD_NUMBER}-${env.GIT_COMMIT ? env.GIT_COMMIT.take(7) : 'latest'}"
        GITOPS_REPO_NAME    = 'microservices-gitops'
        GITOPS_REPO_URL     = "https://git-codecommit.${AWS_REGION}.amazonaws.com/v1/repos/${GITOPS_REPO_NAME}"
        AWS_CREDENTIALS_ID  = 'aws-credentials'
        CODECOMMIT_CREDS_ID = 'codecommit-git-creds'
    }

    stages {
        stage('Code Analysis & Lint') {
            steps {
                echo "===> Running preliminary sanity checks..."
                sh '''
                    python3 -m py_compile user-service/app.py
                    python3 -m py_compile product-service/app.py
                    python3 -m py_compile order-service/app.py
                    python3 -m py_compile notification-service/app.py
                    python3 -m py_compile frontend/app.py
                '''
            }
        }

        stage('AWS ECR Login') {
            steps {
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: env.AWS_CREDENTIALS_ID
                ]]) {
                    echo "===> Authenticating with Amazon ECR..."
                    sh '''
                        aws ecr get-login-password --region ${AWS_REGION} | \
                        docker login --username AWS --password-stdin ${ECR_REGISTRY}
                    '''
                }
            }
        }

        stage('Build & Push Container Images (Parallel)') {
            parallel {
                stage('User Service') {
                    steps {
                        script { buildAndPush('user-service') }
                    }
                }
                stage('Product Service') {
                    steps {
                        script { buildAndPush('product-service') }
                    }
                }
                stage('Order Service') {
                    steps {
                        script { buildAndPush('order-service') }
                    }
                }
                stage('Notification Service') {
                    steps {
                        script { buildAndPush('notification-service') }
                    }
                }
                stage('Frontend') {
                    steps {
                        script { buildAndPush('frontend') }
                    }
                }
            }
        }

        stage('Update GitOps Repo (AWS CodeCommit)') {
            steps {
                echo "===> Updating Kubernetes manifests in GitOps repository..."
                withCredentials([usernamePassword(
                    credentialsId: env.CODECOMMIT_CREDS_ID,
                    usernameVariable: 'GIT_USER',
                    passwordVariable: 'GIT_PASS'
                )]) {
                    sh '''
                        rm -rf ${GITOPS_REPO_NAME}
                        git clone https://${GIT_USER}:${GIT_PASS}@git-codecommit.${AWS_REGION}.amazonaws.com/v1/repos/${GITOPS_REPO_NAME}
                        cd ${GITOPS_REPO_NAME}/k8s

                        # Update image tags in Kubernetes deployment manifests
                        sed -i "s|image: ${ECR_REGISTRY}/user-service:.*|image: ${ECR_REGISTRY}/user-service:${IMAGE_TAG}|g" 01-user-service.yaml
                        sed -i "s|image: ${ECR_REGISTRY}/product-service:.*|image: ${ECR_REGISTRY}/product-service:${IMAGE_TAG}|g" 02-product-service.yaml
                        sed -i "s|image: ${ECR_REGISTRY}/order-service:.*|image: ${ECR_REGISTRY}/order-service:${IMAGE_TAG}|g" 03-order-service.yaml
                        sed -i "s|image: ${ECR_REGISTRY}/notification-service:.*|image: ${ECR_REGISTRY}/notification-service:${IMAGE_TAG}|g" 04-notification-service.yaml
                        sed -i "s|image: ${ECR_REGISTRY}/frontend:.*|image: ${ECR_REGISTRY}/frontend:${IMAGE_TAG}|g" 05-frontend-service.yaml

                        git config user.name "jenkins-bot"
                        git config user.email "jenkins@cloud.local"

                        git add .
                        git diff --staged --quiet || git commit -m "chore(gitops): auto-update image tags to ${IMAGE_TAG} [skip ci]"
                        git push origin main
                    '''
                }
            }
        }
    }

    post {
        always {
            echo "===> Cleaning up temporary Docker images..."
            sh "docker image prune -f"
        }
        success {
            echo "===> CI succeeded! ArgoCD will now sync to k3s."
        }
        failure {
            echo "===> Pipeline failed! Please inspect logs."
        }
    }
}

def buildAndPush(serviceName) {
    echo "===> Building image for ${serviceName}..."
    sh """
        docker build -t ${ECR_REGISTRY}/${serviceName}:${IMAGE_TAG} -t ${ECR_REGISTRY}/${serviceName}:latest ./app-repo/${serviceName}
        docker push ${ECR_REGISTRY}/${serviceName}:${IMAGE_TAG}
        docker push ${ECR_REGISTRY}/${serviceName}:latest
    """
}
