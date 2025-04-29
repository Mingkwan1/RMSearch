from rmsearch.rmsearch import Search
from model_loader import confirm_model_downloaded

model_dir = confirm_model_downloaded()

search = Search(model_name = model_dir,
        tensor_parallel_size = 1,
        pipeline_parallel_size = 2,)

async def get_answer(queries, keys):
    output = await search(queries, keys)
    print(output)
    return output