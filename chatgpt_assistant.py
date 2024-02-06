"""
This ChatGPT assistant script designed to
- Create Assistant
- Modify Assistant
- Make conversation with assistant
"""

import os
import time
from llama_index import download_loader
from openai import OpenAI
from types import SimpleNamespace
from urllib.parse import urlparse, unquote

#import configs
import conf.assistant_config as assistant_conf
import conf.url_list as url_conf  

assistant_id = assistant_conf.assistant_id
assistant_name = assistant_conf.assistant_name
urls = url_conf.urls
prompt_instruction = assistant_conf.prompt_instruction

class OpenAIAssistant:
    def __init__(self):
        self.client = OpenAI()


    def create_assistant(self, file_ids):
        "Create the assistant with retrieval type"
        assistant = self.client.beta.assistants.create(
            instructions= prompt_instruction,
            name= assistant_name,
            model="gpt-4-1106-preview",
            tools=[{"type": "retrieval"}],
            file_ids=file_ids
        )
        return assistant
    

    def modify_assistant(self, assistant, file_ids):
        "Update the assistant"
        assistant = self.client.beta.assistants.update(
            assistant_id=assistant.id,
            name= assistant_name,
            instructions= prompt_instruction,
            model="gpt-4-1106-preview",
            tools=[{"type": "retrieval"}],
            file_ids=file_ids
        )
        print('Updated assistant.')
        return assistant


    def create_thread(self):
        "Create a thread"
        thread = self.client.beta.threads.create()
        return thread


    def create_message(self, thread_id, role, content):
        "Create a message"
        message = self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role=role,
            content=content
        )
        return message


    def display_assistant_response(self, thread_id):
        "Display assistant response"
        messages = self.client.beta.threads.messages.list(
            thread_id=thread_id
        )
        print("\nMessages:")
        print(messages.data[0].role + ": " + messages.data[0].content[0].text.value)

        return messages.data[0].content[0].text.value


    def run_assistant(self, thread_id, assistant_id):
        "Run the assistant"
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        return run


    def check_run_status(self, thread_id, run_id):
        "Check the run status"
        run = self.client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )
        return run


    def create_files_from_directory(self, directory_path):
        "Create files from directory"
        file_ids = []

        # List all files in the specified directory
        files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
        print("Files:",files)
        for file_name in files:
            file_path = os.path.join(directory_path, file_name)
            # Upload a file with an "assistants" purpose
            file = self.client.files.create(
                file=open(file_path, "rb"),
                purpose='assistants'
            )
            file_ids.append(file.id)

        return file_ids

    
    def save_webpage_content_from_urls(self, urls, directory_path="upload_docs"):
        "Save urls contents to file"
        # Initialize the ReadabilityWebPageReader
        loader = download_loader("ReadabilityWebPageReader")

        # Create the output directory if it doesn't exist
        os.makedirs(directory_path, exist_ok=True)

        for url in urls:
            try:
                # Create an instance of ReadabilityWebPageReader
                reader_instance = loader()

                # Load data for each URL using the instance
                documents = reader_instance.load_data(url=url)

                # Extract webpage content from the loaded documents
                webpage_content = documents[0].text

                # Extract the path from the URL and unquote it
                url_path = urlparse(url).path
                file_name = os.path.basename(unquote(url_path))

                # Remove invalid characters from the file name
                file_name = "".join(c for c in file_name if c.isalnum() or c in {'-', '_'}) 

                # Generate the full file path
                file_path = os.path.join(directory_path, file_name + ".txt")

                # Open the file in write mode ('w' for writing)
                with open(file_path, 'w', encoding='utf-8') as file:
                    # Write the webpage content to the file
                    file.write(webpage_content)

                print(f"Content for {url} has been saved to {file_path}")

            except Exception as e:
                print(f"Error processing {url}: {str(e)}")


    def wait_for_assistant_process_completion(self, thread_id, run_id):
        "Polling loop to wait for the run to complete"
        while True:
            run_status = self.check_run_status(thread_id, run_id)
            if run_status.status == 'completed':
                break
            elif run_status.status == 'failed':
                print("Run failed. Check the error details.")
                break
            time.sleep(5) # Wait for 5 seconds before checking again
            print("Waiting for assistant process completion")

        return run_status


    def new_conversion(self,assistant):
        "assistant flow for new conversion"
        thread = self.create_thread()
        
        # Take user input for the message content
        user_content = input("How Can I help you ? \nUser: ")
        user_content = "Please follow provided instructions carefully. " + user_content
        print ("Users input:", user_content)
        self.create_message(thread.id, "user", user_content)
        run = self.run_assistant(thread.id, assistant.id)
        self.wait_for_assistant_process_completion(thread.id, run.id)
        self.display_assistant_response(thread.id)

        return thread


    def continue_conversion(self, assistant, thread):
        "Assistant flow to continue conversion"
        # Take user input for the message content
        user_content = input("Can you please provide your feedback to my previous response? \nUser: ")
        user_content = "Please follow provided instructions carefully. " + user_content
        print ("Users input:", user_content)
        self.create_message(thread.id, "user", user_content)
        run = self.run_assistant(thread.id, assistant.id)
        self.wait_for_assistant_process_completion(thread.id, run.id)
        self.display_assistant_response(thread.id)


    def run(self):
        "Main function to execute the assistant flow"
        directory_path = "upload_docs"
        new_assistant = input("Can I use existing Qxf2's Assistant or create new assistant? (Type 'existing' or 'new') \n User: ")
        
        #If user want to create new assistant:
        if new_assistant.lower() == "new":
            self.save_webpage_content_from_urls(urls,directory_path)
            files_id = self.create_files_from_directory(directory_path)
            #print(files_id)
            assistant = self.create_assistant(files_id)
            print('New Assistant ID:',assistant.id)
            print('Note: Update config/assistant_config file with above id to use it later.')

        #Use existing assistant
        elif new_assistant.lower() == "existing":
            assistant = SimpleNamespace(id=assistant_id)
            new_files = input("Is there any new file/updated file to upload for assistant or any modification to prompt instruction. (Type yes/no) \nUser: ")
            if new_files.lower() == "yes":
                self.save_webpage_content_from_urls(urls,directory_path)
                files_id = self.create_files_from_directory(directory_path)
                assistant = self.modify_assistant(assistant,files_id)
 
        thread = self.new_conversion(assistant)

        while True:
            # Ask the user if they want to continue the conversation
            conversion_flow = input("\nDo you want to continue the conversation or start a new one or exit? (Type 'yes' to continue, 'no' to start a new one or 'exit' to stop conversation) \nUser: ")
            
            # If the user wants to continue conversation
            if conversion_flow.lower() == 'yes':
                self.continue_conversion(assistant,thread)

            # If the user want to start new conversion 
            elif conversion_flow.lower() == 'no':
                thread = self.new_conversion(assistant)

            # If the user doesn't want to continue, break out of the loop
            elif conversion_flow.lower() == 'exit':
                break


if __name__ == "__main__":
    assistant_instance = OpenAIAssistant()
    assistant_instance.run()
