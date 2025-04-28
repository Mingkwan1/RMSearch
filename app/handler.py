import runpod
from llm import get_answer

queries = ["How to make LLM?", "What's the capital of Japan?"] * 5
keys = ["LLM is Large Language Model which can be made ...", "Japanese capital is ..."] * 5

print(">>> handler.py loaded ✅")
def handler(event):
    """
    This function processes incoming requests to your Serverless endpoint.
    
    Args:
        event (dict): Contains the input data and request metadata
        
    Returns:
        Any: The result to be returned to the client
    """
    
    print(">>> handler.py called ✅")
    # Extract input data
    print(f"Worker Start")
    try:
        input = event['input']
        
        prompt = input.get('prompt')  
        seconds = input.get('seconds', 0)  

        print(f"Received prompt: {prompt}")
        print(f"Sleeping for {seconds} seconds...")
        
        # You can replace this sleep call with your Python function to generate images, text, or run any machine learning workload
        result = get_answer(queries= prompt, keys = keys)
        return result 
    except Exception as e:
        print(f"Error in handler: {str(e)}")
        print(f"CRITICAL: {str(e)}", flush=True)  # Visible in RunPod logs
        raise # Ensure the error gets captured
    
# Start the Serverless function when the script is run
if __name__ == '__main__':
    print("🔧 Starting serverless handler...")
    runpod.serverless.start({'handler': handler })