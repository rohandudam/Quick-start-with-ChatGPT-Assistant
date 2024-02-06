# Quick-start-with-ChatGPT-Assistant
This repository helps to create, update and use ChatGPT assistant quickly.

------
Setup:
------

Follow below steps to get set to start with ChatGPT Assistant.

1. Create a virtual envirnment and activate it
2. Install dependencies using following command: `pip install -r requirements.txt`
3. Set envirnmental variable for OpenAI api key using following command: `export OPENAI_API_KEY='Add your key here'`
4. Update conf/assistant_config.py file for assistant related configuration
5. Update conf/url_list.py file if you want to use any webpage for RAG

-------
Command to run OpenAI Assistant script:
-------
Use following command to run the assistant script:
`python chatgpt_assistant.py`

Once script starts running, it will ask some interactive questions to create new assistant, modify existing assistant or make conversation with assistant.