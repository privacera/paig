# Simple AI Application demonstration using PAIG

## Step 0: Create Virtual Environment(Optional)
```shell
python3 -m venv venv
sh ./venv/bin/activate
```

## Step 1: Start the PAIG server
If you have not started the PAIG server, please follow instructions as given below:-

#### Install dependencies
```shell
pip install paig-server
python -m spacy download en_core_web_lg
```

#### Start Server
```shell
paig run
```

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

***Note*** - If you have started server on 4545 port , PAIG default config can be downloaded using url http://127.0.0.1:4545/governance-service/api/ai/application/1/config/json/download

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
