# Simple AI Application demonstration using PAIG


## Step 1: Start the PAIG server
If you have not started the PAIG server, please follow the instructions in the [PAIG Quick Start Guide](https://docs.paig.ai/index.html) to start the PAIG server.

## Step 2: Install the PAIG client and dependencies
To install the PAIG client, run the following command:
```bash
pip install openai==1.11.1 paig-client
```

## Step 3: Download the PAIG configuration file
Download the PAIG configuration file from the PAIG server and save it under directory 'privacera'.
```shell
mkdir privacera
```

## Step 4: Set the OPENAI_API_KEY environment variable
Set the OPENAI_API_KEY environment variable to your OpenAI API key.
```bash
export OPENAI_API_KEY=<your_openai_api_key>
```

## Step 5: Run the AI application
Run the AI application using the following command:
```bash
python ai_app.py
```

## Step 6: Verify the results
The AI application will generate PAIG governed text. You can verify access audits and other details on PAIG server dashboard.
