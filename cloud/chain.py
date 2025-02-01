from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

class chain:
    def __init__(self):
        self.llm = ChatGroq(
        groq_api_key ='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',
        temperature = 0.1,
        model_name = 'llama3-70B-8192'    
        )
    
    def generate(self, cpu_usage, network_in, network_out, disk_read, disk_write): 
        # Define the prompt template with corrected input variables
        template = PromptTemplate(
            input_variables=["cpu_usage", "network_in", "network_out", "disk_read", "disk_write"],
            template="""
            ## Data:
            - CPU Usage: {cpu_usage}
            - Incoming Network Traffic: {network_in}
            - Outgoing Network Traffic: {network_out}
            - Disk Read Rate: {disk_read}
            - Disk Write Rate: {disk_write}
            
            ## Instruction:
            This data has been collected from Azure during usage by multiple users.
            Based on the data, an anomaly has been detected in the cloud infrastructure. 
            Please identify the anomaly, determine which parameter is causing it, 
            provide possible reasons for the anomaly, and suggest steps to overcome it.
            """
        )

        # Create the chain
        chain = template | self.llm

        # Invoke the chain with correct variable names
        res = chain.invoke({
            "cpu_usage": cpu_usage,
            "network_in": network_in,
            "network_out": network_out,
            "disk_read": disk_read,
            "disk_write": disk_write
        })
        
        return res.content
    
    
    def email( self , summary):
            print("3")
            mail_template = PromptTemplate(
            input_variables=["summary"],
            template="""  
            #data
            {summary}

            #instruction:
            Write an email to the supervisor of Azure cloud, alerting them about the issue given above, 
            and also mention the reason for the anomaly and how to solve it. Please start the 
            email by addressing him/her as "Hi Sir/Madam."
            """
        )

            # Instead of chaining with self, just use the LLM
            email_chain = mail_template | self.llm  # Use the LLM directly here

            # Invoke the email chain with the summary
            f_res = email_chain.invoke({
                "summary": summary
            })

            return f_res.content


        