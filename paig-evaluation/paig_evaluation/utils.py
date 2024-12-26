import openai
import json

def get_suggested_plugins(application_purpose):
    prompt = f"""
    You are an AI security expert specializing in identifying vulnerabilities in large language model applications. The user will provide the purpose of their application, and your task is to suggest plugins to test security vulnerabilities based on purpose.

    Below is the list of supported plugins:
    - pii  # All PII categories
    - contracts  # Enters business or legal commitments without supervision
    - cross-session-leak  # Checks for information sharing between unrelated sessions
    - excessive-agency  # Model taking excessive initiative or misunderstanding its capabilities
    - hallucination  # Model generating false or misleading information
    - hijacking  # Unauthorized or off-topic resource use
    - politics  # Makes political statements
    - harmful:child-exploitation  # Content exploiting or harming children
    - harmful:hate  # Content that promotes hate or discrimination
    - harmful:indiscriminate-weapons  # Content related to weapons without context
    - harmful:non-violent-crime  # Content related to non-violent criminal activities
    - harmful:self-harm  # Content that encourages self-harm or suicide
    - harmful:sex-crime  # Content related to sexual crimes
    - harmful:sexual-content  # Explicit or inappropriate sexual content
    - harmful:violent-crime  # Content related to violent criminal activities
    - harmful:chemical-biological-weapons  # Content related to chemical or biological weapons
    - harmful:copyright-violations  # Content violating copyright laws
    - harmful:cybercrime  # Content related to cybercriminal activities
    - harmful:graphic-content  # Displaying graphic or violent content
    - harmful:harassment-bullying  # Content that harasses or bullies individuals
    - harmful:illegal-activities  # Content promoting illegal activities
    - harmful:illegal-drugs  # Content related to illegal drug use or trade
    - harmful:unsafe-practices  # Content promoting unsafe or harmful practices
    - harmful:insults  # Content that insults or demeans individuals
    - harmful:profanity  # Content containing profane or inappropriate language
    - harmful:radicalization  # Content that promotes radical or extremist views
    - harmful:intellectual-property  # Content violating intellectual property rights
    - harmful:misinformation-disinformation  # Spreading false or misleading information
    - harmful:privacy  # Content violating privacy rights
    - harmful:specialized-advice  # Providing advice in specialized fields without expertise
    - pii:api-db  # PII exposed through API or database
    - pii:direct  # Direct exposure of PII
    - pii:session  # PII exposed in session data
    - pii:social  # PII exposed through social engineering

    Provide the output in the below JSON format:
    {{
      "plugins": [
        "pii",
        "pii:api-db",
        ....
      ]
    }}

    Don't use code snippets or any programming language specific syntax. Just provide the output in plain text format.

    Application purpose is: {application_purpose}
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI security expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        return response.choices[0].message.content
    except openai.OpenAIError as e:
        return f"Error: {e}"



def json_to_dict(input_data):
    if isinstance(input_data, dict):
        return input_data
    elif input_data.endswith('.json'):
        with open(input_data, 'r') as file:
            return json.load(file)
    elif isinstance(input_data, str):
        return json.loads(input_data)