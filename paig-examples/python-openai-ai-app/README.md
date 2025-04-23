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

## Step 3: Create a new AI application and Generate an API key
- To create a new application and generate an API key, follow these steps:
     - Login to PAIG.
     - Go to `Paig Navigator` → `AI Applications` and click the `CREATE APPLICATION` button at the top-right.
     - A dialog box will open where you can enter the details of your application.
     - Once the Application is created:
       - Navigate to `Paig Navigator` → `AI Applications` and select the application for which you want to generate the API key.
       - In the `API KEYS` tab, click the `GENERATE API KEY` button in the top-right corner.
       - Provide a `Name` and `Description`, and set an `Expiry`, or select the `Max Validity (1 year)` checkbox to use the default expiry.

       > **Note:** Once the API key is generated, it will not be shown again. Ensure you copy and securely store it immediately after generation.

   - To initialize the **PAIG Shield** library in your application, export the `PAIG_APP_API_KEY` as an environment variable:

     ```bash
     export PAIG_APP_API_KEY=<<AI_APPLICATION_API_KEY>>
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
