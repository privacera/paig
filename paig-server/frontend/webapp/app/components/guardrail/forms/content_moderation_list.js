import {GUARDRAIL_PROVIDER} from 'utils/globals';

const content_moderation_list = [{
    "category": "Hate",
    "description": "",
    "providers": [GUARDRAIL_PROVIDER.AWS.NAME],
    "strengthType": "high_medium_low",
    "filterStrengthPrompt": "high",
    "filterStrengthResponse": "high"
}, {
    "category": "Hate/Threatening",
    "description": "Hateful content that also includes violence or serious harm towards the targeted group based on race, gender, ethnicity, religion, nationality, sexual orientation, disability status, or caste.",
    "providers": [],
    "strengthType": ""
}, {
    "category": "Insults",
    "description": "Describes input prompts and model responses that includes demeaning, humiliating, mocking, insulting, or belittling language. This type of language is also labeled as bullying.",
    "providers": [GUARDRAIL_PROVIDER.AWS.NAME],
    "strengthType": "high_medium_low",
    "filterStrengthPrompt": "high",
    "filterStrengthResponse": "high"
}, {
    "category": "Sexual Content",
    "description": "Describes input prompts and model responses that indicates sexual interest, activity, or arousal using direct or indirect references to body parts, physical traits, or sex.",
    "providers": [GUARDRAIL_PROVIDER.AWS.NAME],
    "strengthType": "high_medium_low",
    "filterStrengthPrompt": "high",
    "filterStrengthResponse": "high"
}, {
    "category": "Child Exploitation",
    "description": "AI models should not create content that depicts child nudity or that enables, encourages, excuses, or depicts the sexual abuse of children.",
    "providers": [],
    "strengthType": ""
}, {
    "category": "Violence",
    "description": "Describes input prompts and model responses that includes glorification of or threats to inflict physical pain, hurt, or injury toward a person, group or thing.",
    "providers": [GUARDRAIL_PROVIDER.AWS.NAME],
    "strengthType": "high_medium_low",
    "filterStrengthPrompt": "high",
    "filterStrengthResponse": "high"
}, {
    "category": "Violence/Graphic",
    "description": "Content that depicts death, violence, or physical injury in graphic detail.",
    "providers": [],
    "strengthType": ""
}, {
    "category": "Misconduct",
    "description": "Describes input prompts and model responses that seeks or provides information about engaging in criminal activity, or harming, defrauding, or taking advantage of a person, group or institution.",
    "providers": [GUARDRAIL_PROVIDER.AWS.NAME],
    "strengthType": "high_medium_low",
    "filterStrengthPrompt": "high",
    "filterStrengthResponse": "high"
}, {
    "category": "Harassment",
    "description": "Content that expresses, incites, or promotes harassing language towards any target.",
    "providers": [],
    "strengthType": ""
}, {
    "category": "Harassment/Threatening",
    "description": "Harassment content that also includes violence or serious harm towards any target.",
    "providers": [],
    "strengthType": ""
}, {
    "category": "Non-Violent Crimes",
    "description": `AI models should not create content that enables, encourages, or excuses the commission of non-violent crimes. Examples of non-violent crimes include, but are not limited to:
                                    - Financial crimes (ex: fraud, scams, money laundering)
                                    - Property crimes (ex: burglary, robbery, arson, vandalism)
                                    - Drug crimes (ex: creating or trafficking narcotics)
                                    - Weapons crimes (ex: producing unlicensed firearms)
                                    - Cyber crimes (ex: hacking, spyware, malware)`,
    "providers": [],
    "strengthType": ""
}, {
    "category": "Violent Crimes",
    "description": `AI models should not create content that enables, encourages, or excuses the commission of violent crimes. Examples of violent crimes include, but are not limited to:
                                    - Unlawful violence toward people (ex: terrorism, genocide, murder, hate crimes, child abuse, assault, battery, kidnapping)
                                    - Unlawful violence toward animals (ex: animal abuse)`,
    "providers": [],
    "strengthType": ""
}, {
    "category": "Sex Crimes",
    "description": `AI models should not create content that enables, encourages, or excuses the commission of sex crimes. Examples of sex crimes include, but are not limited to:
                                    - Human trafficking
                                    - Sexual assault (ex: rape)
                                    - Sexual harassment (ex: groping)
                                    - Lewd conduct`,
    "providers": [],
    "strengthType": ""
}, {
    "category": "Self-Harm",
    "description": "Content that promotes, encourages, or depicts acts of self-harm, such as suicide, cutting, and eating disorders.",
    "providers": [],
    "strengthType": ""
}, {
    "category": "Self-Harm/Intent",
    "description": "Content where the speaker expresses that they are engaging or intend to engage in acts of self-harm, such as suicide, cutting, and eating disorders.",
    "providers": [],
    "strengthType": ""
}, {
    "category": "Self-Harm/Instructions",
    "description": "Content that encourages performing acts of self-harm, such as suicide, cutting, and eating disorders, or that gives instructions or advice on how to commit such acts.",
    "providers": [],
    "strengthType": ""
}, {
    "category": "Defamation",
    "description": "AI models should not create content about a real, living person that is verifiably false and likely to injure the person's reputation.",
    "providers": [],
    "strengthType": ""
}, {
    "category": "Specialized Advice",
    "description": "AI models should not create content that contains specialized financial, medical, or legal advice.",
    "providers": [],
    "strengthType": ""
}, {
    "category": "Privacy",
    "description": "AI models should not create content that contains sensitive, personal information about private individuals.",
    "providers": [],
    "strengthType": ""
}, {
    "category": "Intellectual Property",
    "description": "AI models should not create content that violates the intellectual property rights of third parties.",
    "providers": [],
    "strengthType": ""
}, {
    "category": "Indiscriminate Weapons",
    "description": `I models should not create content that enables the creation of weapons of mass destruction. Examples of such weapons include, but are not limited to:
                                    - Chemical weapons (ex: nerve gas)
                                    - Biological weapons (ex: anthrax)
                                    - Radiological weapons (ex: salted bombs)
                                    - Nuclear weapons (ex: atomic warheads)
                                    - High-yield explosive weapons (ex: cluster munitions)`,
    "providers": [],
    "strengthType": ""
}, {
    "category": "Elections",
    "description": "AI models should not create content that contain factually incorrect information about electoral systems and processes, including in the time, place, or manner of voting in civic elections.",
    "providers": [],
    "strengthType": ""
}]

export {
    content_moderation_list
}