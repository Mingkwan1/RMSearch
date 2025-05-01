import runpod, logging
from rmsearch.rmsearch import Search
from model_loader import confirm_model_downloaded

# Setup logging
logging.basicConfig(
    level=logging.INFO,  # default to INFO level
    format="%(asctime)s [%(levelname)s] %(message)s",
)

queries = ["How to make LLM?", "What's the capital of Japan?"] * 5
keys = ["LLM is Large Language Model which can be made ...", "Japanese capital is ..."] * 5

logging.info(">>> handler.py loaded ✅")

model_dir = confirm_model_downloaded()

search = Search(model_name = model_dir,
        tensor_parallel_size = 1,
        pipeline_parallel_size = 1,) #change it to 1

async def get_answer(queries, keys):
    output = await search(queries, keys)
    logging.info(output)
    return output

def handler(event):
    """
    This function processes incoming requests to your Serverless endpoint.
    
    Args:
        event (dict): Contains the input data and request metadata
        
    Returns:
        Any: The result to be returned to the client
    """
    
    logging.info(">>> handler.py called ✅")
    # Extract input data
    logging.info(f"Worker Start")
    try:
        input = event['input']
        
        prompt = input.get('prompt')  
        seconds = input.get('seconds', 0)  

        logging.info(f"Received prompt: {prompt}")
        logging.info(f"Sleeping for {seconds} seconds...")
        
        # You can replace this sleep call with your Python function to generate images, text, or run any machine learning workload
        result = get_answer(queries= prompt, keys = keys)
        return result 
    except Exception as e:
        logging.info(f"Error in handler: {str(e)}")
        logging.info(f"CRITICAL: {str(e)}", flush=True)  # Visible in RunPod logs
        raise # Ensure the error gets captured
    
# Start the Serverless function when the script is run
if __name__ == '__main__':
    logging.info("🔧 Starting serverless handler...")
    runpod.serverless.start({'handler': handler })