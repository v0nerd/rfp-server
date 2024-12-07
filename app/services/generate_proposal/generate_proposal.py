from app.services.generate_proposal.summarization_model import SummarizationModel
from transformers import BartForConditionalGeneration, BartTokenizer
import os

import openai
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY")


def generate_technical_content(requirements):
    """
    Generate a technical approach based on given requirements and expertise.

    Parameters:
        requirements (str): A description of the requirements.
        expertise (str): A description of the expertise or domain knowledge.

    Returns:
        str: The generated technical approach content.
    """
    try:
        # Initialize ChatOpenAI with the API key and model configuration
        chat_gpt = ChatOpenAI(
            api_key=api_key,  # Replace with your actual API key or use environment variables for security
            model="gpt-4",
            temperature=0,  # Control creativity (lower = more deterministic)
        )

        # Prepare the message for the AI model
        messages = [
            HumanMessage(
                content=(
                    f"Generate a technical approach based on the following requirements:\n"
                    f"Requirements: {requirements}\n"
                    f"Output a detailed and structured technical approach to achieve RFP contract phase by phase."
                )
            ),
        ]

        # Call the AI model to get a response
        ai_message = chat_gpt.invoke(messages)

        return ai_message.content

    except Exception as e:
        # Handle any errors that occur during the process
        print(f"Error generating technical content: {e}")
        return "An error occurred while generating the technical content."


async def generate_proposal(content, technical_requirements):
    summarization_model = SummarizationModel()
    summarization_model.input = content

    if not os.path.isdir(summarization_model.config["model"]["model_path"]):
        summarization_model.download_from_s3(
            "rfp-models", "summarization_model_fine_tuned"
        )

    summarization_model.model = BartForConditionalGeneration.from_pretrained(
        "models/summarization_model_fine_tuned"
    )
    summarization_model.tokenizer = BartTokenizer.from_pretrained(
        "models/summarization_model_fine_tuned"
    )
    summarization_model.generate_summary()
    summary = summarization_model.output

    technical_approach = generate_technical_content(technical_requirements)

    return {"executive_summary": summary, "technical_approach": technical_approach}
