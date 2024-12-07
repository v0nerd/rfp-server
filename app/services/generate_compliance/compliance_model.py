import yaml
import torch
import os
import boto3
from botocore.exceptions import NoCredentialsError

config_path = os.path.join(os.path.dirname(__file__), "config.yaml")

# Load configuration
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

label_map = {
    0: "Compliance Score: 68%\\nIssues:\\nMissing Purpose of the RFP and Background (FAR 15.203).\\nProject Goals and Expected Outcomes not provided (FAR 15.203).\\nTimeline and Project Milestones not clearly defined (FAR 15.204-3, FAR 15.304).\\nVendor Qualifications and Financial Stability not outlined (FAR 9.104).\\nProposal Submission instructions not provided (FAR 15.203).\\nMissing Payment Terms and Budget Limitations (FAR 15.402).\\nConfidentiality, Indemnification, Governing Law, and Contractual Agreement missing (FAR 52.215-1, FAR 52.212-4).\\nMissing Contact Information (FAR 15.203(b)).",
    1: "Compliance Score: 85%\\nIssues:\\nDeliverables and Timeline need more clarity, especially for contract milestones and deadlines (FAR 15.304, FAR 15.204-3).\\nMissing Project Requirements details related to performance expectations (FAR 15.304).\\nProposal Submission instructions not explicitly provided (FAR 15.203).\\nLack of detailed Proposal Format guidelines (FAR 15.204-1).\\nMissing instructions for Questions and Clarifications (FAR 15.203(b)).\\nPayment Terms and Budget Limitations not clearly outlined (FAR 15.402).\\nEvaluation Process and Scoring System need further detail on relative weight and evaluation factors (FAR 15.304).",
    2: "Compliance Score: 90%\\nIssues:\\nDeliverables: The deliverables are well-defined but should include more specific milestones or deadlines to meet FAR 15.304 requirements for measurable outputs.\\nTimeline: Not explicitly provided in terms of dates or specific phases for deliverables (FAR 15.204-3).\\nProject Requirements: Needs more detailed descriptions of vendor responsibilities and performance metrics to ensure compliance with FAR 15.304.",
    3: "Compliance Score: 92%\\nIssues:\\nTimeline and Project Milestones: These should be explicitly detailed with dates and phases to align with FAR 15.204-3.\\nPayment Terms: Not clearly outlined, should specify payment schedule or conditions (FAR 15.402, FAR 52.232-1).\\nProposal Submission: Needs clear instructions on submission method and deadline (FAR 15.203).\\nConfidentiality, Indemnification, and Governing Law: Should include FAR-specific clauses (e.g., FAR 52.215-1, FAR 52.212-4) for full legal clarity.",
    4: "Compliance Score: 95%\\nIssues:\\nTimeline: The document requests proposed timelines from vendors, but the RFP should also provide a defined project timeline with specific milestones and deadlines to ensure consistency across submissions (FAR 15.204-3).\\nPayment Terms: While the payment structure is outlined, the specific conditions for payment and any performance-based milestones should be more detailed (FAR 52.232-1).\\nProposal Submission: Clear instructions are given, but confirming electronic submission methods and deadlines would enhance compliance (FAR 15.203).\\nConfidentiality, Indemnification, and Governing Law: These are mentioned, but should reference relevant FAR clauses for completeness (e.g., FAR 52.215-1, FAR 52.212-4).",
    5: "Compliance Score: 90%\\nIssues:\\nVendor Qualifications: The criteria should specify any certifications, experience, or specific qualifications required for the vendor, in alignment with FAR 9.104.\\nFinancial Stability: While financial stability is noted, the RFP should clarify the exact financial requirements and the evaluation process, as per FAR 9.104-1.\\nReferences: Clear guidelines on the type of references required (e.g., past projects or client feedback) should be provided for better compliance with FAR 9.104-3.\\nProject Description and Scope of Work: Well outlined, but should include measurable milestones and deliverables for alignment with FAR 15.304.\\nProject Outcomes: Need to define specific, measurable outcomes to ensure clarity for vendors, as per FAR 15.203 and FAR 15.304.",
    6: "Compliance Score: 92%\\nIssues:\\nTimeline: Missing specific dates and deadlines for milestones and deliverables, which should be included for better alignment with FAR 15.204-3.\\nProposal Submission: Clear instructions are needed on submission methods and deadlines to comply with FAR 15.203.\\nPayment Terms: While payment terms are mentioned, the conditions for milestone payments or other specific payment structures should be more detailed (FAR 52.232-1).\\nBudget Limitations: Should specify budget caps or constraints to help vendors tailor their proposals (FAR 15.402).\\nConfidentiality, Indemnification, and Governing Law: These clauses should reference applicable FAR provisions (e.g., FAR 52.215-1, FAR 52.212-4) for full compliance and clarity.",
    7: "Compliance Score: 85%\\nIssues:\\nEvaluation Criteria: The document lacks a clear, detailed Evaluation Criteria section (FAR 15.304). It’s essential to outline how proposals will be scored and evaluated to ensure transparency and fairness.\\nProposal Instructions: The proposal requirements are outlined but should clarify how to submit electronically (FAR 15.204-1) and provide clear submission deadlines (FAR 15.203).\\nContact Information: The document does not explicitly provide a contact section for clarifications (FAR 15.203(b)), which could lead to confusion for potential vendors.\\nTimeline: While some dates are specified for pilot programs, more detailed milestones and project deadlines are needed (FAR 15.204-3).\\nTerms and Conditions: While a disclaimer and sample contract are mentioned, more details should be provided on Confidentiality, Indemnification, and Governing Law, referencing applicable FAR clauses (e.g., FAR 52.215-1, FAR 52.212-4).",
    8: "Compliance Score: 60%\\nIssues:\\nPurpose of this RFP: The document references a Pre-Proposal Conference (MAY 2018) but does not explicitly outline the overall purpose of the RFP, which should be clearly stated (FAR 15.203).\\nBackground: Not provided. The Background section is crucial for setting context (FAR 15.203).\\nProject Goals and Expected Outcomes: Not explicitly provided, which are essential for vendors to understand the desired results (FAR 15.203, FAR 15.304).\\nScope of Work: Lacks clear deliverables, timelines, and project requirements. These must be defined to ensure vendors can respond appropriately (FAR 15.204-3, FAR 15.304).\\nVendor Qualifications: Not explicitly provided, which is essential to ensure vendors meet required standards (FAR 9.104).\\nFinancial Stability and References: Missing. These are key eligibility requirements for ensuring contractor responsibility (FAR 9.104-1, FAR 9.104-3).\\nProposal Instructions: Only mentions Expense Related to Proposal Submissions (MAY 2018), with no clear guidance on submission method or format (FAR 15.203, FAR 15.204-1).\\nEvaluation Criteria: Lacks an explicit Evaluation Process and Scoring System, which are necessary for fair and transparent proposal assessment (FAR 15.304).\\nPricing Structure: Not provided. The Pricing Structure, Payment Terms, and Budget Limitations are critical to ensure vendors understand cost expectations and constraints (FAR 15.402, FAR 52.232-1).\\nTimeline: Missing key dates for project milestones and deliverables, which are essential for effective project management (FAR 15.204-3).\\nTerms and Conditions: Only Confidentiality is partially mentioned with a vague reference to safeguards, but Indemnification, Governing Law, and Contractual Agreement need more clarity and reference to FAR clauses (e.g., FAR 52.215-1, FAR 52.212-4).\\nContact Information: Missing clear contact details for questions and clarifications (FAR 15.203(b)).",
}


class ComplianceModel:
    def __init__(self, model_name=config["model"]["model_path"], config=config):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.input = ""
        self.output = ""
        self.config = config

    def predict_compliance(self):
        # Tokenize the input text
        inputs = self.tokenizer(
            self.input,
            padding="max_length",
            truncation=True,
            max_length=512,
            return_tensors="pt",
        )

        # Ensure the model is in evaluation mode
        self.model.eval()

        # Make predictions (forward pass)
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Get the logits output from the model
        logits = outputs.logits

        # Convert logits to probabilities using softmax
        softmax = torch.nn.Softmax(dim=-1)
        probabilities = softmax(logits)

        # Get the predicted label index (class)
        predicted_label = torch.argmax(probabilities, dim=-1)

        # Convert the predicted index to the corresponding label name
        self.output = label_map[predicted_label.item()]


    def download_from_s3(self, bucket_name, model_key):
        # Create an S3 client
        s3_client = boto3.client("s3")

        # Download the model files recursively from S3
        def download_directory_from_s3(s3_bucket, s3_prefix, local_path):
            if not os.path.exists(local_path):
                os.makedirs(local_path)

            # List objects under the specified S3 prefix (model_key)
            try:
                response = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=s3_prefix)
                if "Contents" in response:
                    for obj in response["Contents"]:
                        s3_file_key = obj["Key"]
                        local_file_path = os.path.join(
                            local_path, os.path.relpath(s3_file_key, s3_prefix)
                        )

                        # Create directories if they do not exist
                        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

                        # Download the file from S3
                        print(f"Downloading {s3_file_key} to {local_file_path}")
                        s3_client.download_file(s3_bucket, s3_file_key, local_file_path)
                else:
                    print(f"No files found for {s3_prefix} in bucket {s3_bucket}")
            except NoCredentialsError:
                print("Credentials not available")
            except Exception as e:
                print(f"Error downloading from S3: {str(e)}")

        # Download the model and tokenizer from the S3 bucket to the local model_key directory
        download_directory_from_s3(
            bucket_name, model_key, config["model"]["model_path"]
        )
