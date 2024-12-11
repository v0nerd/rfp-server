<div align="center">

# **AugierAI Proposal Generator**
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 

</div>

![Alt text](https://github.com/v0nerd/rfp-server/blob/main/Assets/Augier-assessment.png)

This project is an AI-powered solution designed to automate proposal generation and compliance checking for small businesses. It leverages state-of-the-art NLP models, including BART for proposal generation and BERT for compliance checking, to streamline the creation of business proposals from RFP (Request for Proposal) documents. The solution is built using **FastAPI**, **Redis**, and **AWS** services, ensuring high scalability and efficient processing.

## Table of Contents
- [**AugierAI Proposal Generator**](#augierai-proposal-generator)
  - [Table of Contents](#table-of-contents)
  - [Project Overview](#project-overview)
  - [Key Features](#key-features)
  - [Architecture](#architecture)
  - [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Local Development Setup](#local-development-setup)
  - [Usage](#usage)
    - [File Upload](#file-upload)
    - [Generate Proposal](#generate-proposal)
    - [Generate Compliance Report](#generate-compliance-report)
  - [API Endpoints](#api-endpoints)
    - [`/upload/`](#upload)
    - [`/generate/proposal/`](#generateproposal)
    - [`/generate/compliance-report/`](#generatecompliance-report)
  - [Dockerization](#dockerization)
  - [CI/CD Pipeline](#cicd-pipeline)
    - [Installation](#installation-1)
    - [Create a new cluster in your EKS](#create-a-new-cluster-in-your-eks)
    - [Deploy pods for RDS and Generator](#deploy-pods-for-rds-and-generator)
    - [Re-run the pods](#re-run-the-pods)
    - [Run the service](#run-the-service)
    - [Monitor the service](#monitor-the-service)
  - [Contributing](#contributing)

## Project Overview

AugierAI automates the creation of proposals and compliance reports from uploaded **RFP documents** (.pdf or .docx). The project includes two main features:

1. **Proposal Generation**: Generates executive summaries and technical approaches for proposals, incorporating user-uploaded documents and specific technical requirements.
2. **Compliance Checking**: Analyzes RFP documents for compliance against predefined criteria.

The application utilizes **Redis** for caching responses, **Jinja2 templates** for rendering dynamic HTML outputs, and integrates with **AWS S3** for file storage.

## Key Features

- **FastAPI Backend**: Lightweight and fast web framework.
- **File Upload and Processing**: Handles PDF and DOCX file uploads for processing.
- **Caching**: Uses **Redis** to cache proposal and compliance report results for improved performance.
- **Document Extraction**: Extracts relevant sections from RFPs, including technical requirements, budget info, and compliance checks.
- **Template Rendering**: Generates dynamic HTML responses using **Jinja2** templates.
- **Scalability**: Supports containerized deployment with **AWS EKS** for handling high traffic loads.
- **CI/CD Pipeline**: Fully automated deployment pipeline using **AWS CodePipeline**, **ECR**, and **Docker**.

## Architecture

The architecture consists of multiple services interacting with each other:

- **FastAPI** serves as the API gateway and backend service.
- **Redis** caches frequently requested proposals and compliance reports.
- **S3** stores the uploaded RFP documents and fine-tuned models.
- **EC2** instances are used for training and fine-tuning NLP models (BART and BERT).
- **AWS EKS** (Elastic Kubernetes Service) is used to deploy the application in a scalable manner.
- **AWS CodePipeline** automates the build, test, and deployment process.
  
For a detailed system architecture, refer to the diagram in the documentation.

## Installation

### Prerequisites

Before running this project, make sure you have the following:

- **Python 3.8+**
- **Redis** (for local development or an existing Redis server)
- **Docker** (for containerization)
- **AWS Account** (for S3 and other AWS services)

### Local Development Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/v0nerd/rfp-server.git
    cd rfp-server
    ```

2. Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install dependencies:
    ```bash
    pip3 install -r requirements.txt
    ```

4. Configure Redis:
    - Either set up a local Redis server (`redis-server`) or use a cloud-based Redis service.
    - Update the `REDIS_URL` in the `.env` file (or your environment variables).

5. Set up AWS S3 credentials for file storage (if required):
    - Ensure your AWS credentials are properly configured (`aws configure`).

6. Run the application:
    ```bash
    python3 main.py
    ```

The application will be running at `http://localhost:8080`.

## Usage

### File Upload

Use the `/upload/` endpoint to upload `.docx` or `.pdf` RFP documents:

- **Method**: `POST`
- **Endpoint**: `/upload/`
- **Request**: A file to upload (either `.pdf` or `.docx`)
- **Response**: Returns the `file_key` for the uploaded document.

### Generate Proposal

Use the `/generate/proposal/` endpoint to generate a proposal:

- **Method**: `POST`
- **Endpoint**: `/generate/proposal/`
- **Request**: An uploaded RFP file.
- **Response**: An HTML page with the generated proposal, including executive summary, technical approach, and budget information.

### Generate Compliance Report

Use the `/generate/compliance-report/` endpoint to generate a compliance report:

- **Method**: `POST`
- **Endpoint**: `/generate/compliance-report/`
- **Request**: An uploaded RFP file.
- **Response**: An HTML page with the compliance report.

## API Endpoints

### `/upload/`
- **Method**: POST
- **Description**: Uploads a file to S3 for processing.
- **Parameters**: `file` (multipart/form-data)
- **Response**: `{"message": "Uploaded", "file_key": "your_file_key"}`

### `/generate/proposal/`
- **Method**: POST
- **Description**: Generates a business proposal from an uploaded RFP document.
- **Parameters**: `file` (multipart/form-data)
- **Response**: HTML page displaying the proposal.

### `/generate/compliance-report/`
- **Method**: POST
- **Description**: Generates a compliance report from an uploaded RFP document.
- **Parameters**: `file` (multipart/form-data)
- **Response**: HTML page displaying the compliance report.

## Dockerization

To run the application inside Docker, use the following steps:

1. Build the Docker image:
    ```bash
    docker build -t rfp-server .
    ```

2. Run the Docker container:
    ```bash
    docker run -p 8080:8080 rfp-server
    ```

The application will be accessible at `http://localhost:8080`.

## CI/CD Pipeline

### Installation

   - Install ***eksctl*** and **kubectl**

### Create a new cluster in your EKS

```bash
eksctl create cluster --name <cluster-name> --region <your-region> --nodes <node-number>
```

### Deploy pods for RDS and Generator

```bash
kubectl apply -f k8s/
```

This project uses **AWS CodePipeline** for automated deployment:

- Push changes to GitHub to trigger the pipeline.
- The pipeline automatically builds Docker images using **ECR**, and deploys the updated version to **EKS**.

### Re-run the pods
After building an updated Docker image, restart the pods.

```bash
# Rolling Restart of Deployments

kubectl rollout restart deployment <your-deployment-name>
```

### Run the service

```bash
kubectl get svc
curl <service-External-IP>:8080/docs
```

P.S. You must ensure that the service is running with LoadBalancer.

### Monitor the service

```bash
kubectl get pods
kubectl logs <pod-name>
```

## Contributing

We welcome contributions! If you'd like to contribute to this project, please follow these steps:

1. Fork the repository and create a new branch for your feature or fix.
2. Make your changes, then commit them with clear messages.
3. Push your changes to your fork.
4. Create a pull request to the main repository.

Please ensure that your changes are tested and conform to the coding standards.
