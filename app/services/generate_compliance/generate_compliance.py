import os
from transformers import BertForSequenceClassification, BertTokenizer

from app.services.generate_compliance.compliance_model import ComplianceModel


async def generate_compliance(section_text):
    """
    This function generates a compliance report based on the provided technical requirements.
    """

    compliance_model = ComplianceModel()
    compliance_model.input = section_text

    if not os.path.isdir(compliance_model.config["model"]["model_path"]):
        compliance_model.download_from_s3("rfp-models", "compliance_model_fine_tuned")

    compliance_model.model = BertForSequenceClassification.from_pretrained(
        compliance_model.model_name, num_labels=9, use_safetensors=True
    )
    compliance_model.tokenizer = BertTokenizer.from_pretrained(
        compliance_model.model_name, use_safetensors=True
    )

    compliance_model.predict_compliance()
    compliance_report = compliance_model.output

    return compliance_report
