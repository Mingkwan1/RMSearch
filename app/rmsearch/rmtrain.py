from trl import RewardTrainer, RewardConfig
from peft import LoraConfig, TaskType
import accelerate
from peft import get_peft_model

import random
import pandas as pd
from operator import itemgetter
import torch
import torch.nn as nn
import warnings
warnings.filterwarnings('ignore')
from datasets import Dataset, load_dataset, load_from_disk
from transformers import AutoModelForSequenceClassification,AutoTokenizer,TrainingArguments,AutoConfig,AutoModelForCausalLM



class CustomRewardTrainer(RewardTrainer):
    _tag_names = ["trl", "reward-trainer"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def train(self, *args, **kwargs): # You need this because it will use RewardTrainer compute_loss method without this. To use a subclass function, some method in the subclass must be called from main directly. 
        return super().train(*args, **kwargs)

    def evaluate(self, *args, **kwargs):
        return super().evaluate(num_print_samples=1, *args, **kwargs)


class RMTrainer:

    def __init__(self,
             model_name = "llama3b-rm",
             num_gpus = None,
        ):

        self.model_name = model_name
        
        tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side="left", add_eos_token=True, add_bos_token=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            config.pad_token_id = config.eos_token_id
        self.tokenizer = tokenizer
        
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=1)


    def prepare_dataset(self,
                        save_file,
                        file_type = "txt",
                       ):

        with open(save_file) as f:
            json_data = json.load(f)

        """
        json_data should be like
        [
            {
                “query”:[{“system”:”…”}, …],
                “chosen_key”:[{“assistant”:”…”},…],
                “rejected_key”:[{“assistant”:”…”},…],
                **kwargs,
            }
            ...
        ] 
        """
        
        dataset1 = Dataset.from_list(json_data)
        print(dataset1.to_pandas())

        if not os.path.exists(dataset_save_path):
            
            def formatting_func(examples):
                kwargs = {"padding": "max_length", "truncation": True, "max_length": 4000, "return_tensors": "pt", "add_special_tokens":False}
                answer = examples['output'][:4000]
                problem = examples['problem']
                chosen_advice = examples['chosen_advice']
                rejected_advice = examples['rejected_advice']
                chosen_id = examples['chosen_advice_id']
                rejected_id = examples['rejected_advice_id']
            
        
                message = [
                  {'role': 'user', 'content': f"Give me an advice to the problem and answer below;\n\nProblem:{problem}\n\nAnswer:{answer}"},
                  {'role': 'assistant', 'content': f"{chosen_advice}"}
                ]
                prompt_plus_chosen_response = self.tokenizer.apply_chat_template(message, tokenize=False)
        
            
        
                message = [
                  {'role': 'user', 'content': f"Give me an advice to the problem and answer below;\n\nProblem:{problem}\n\nAnswer:{answer}"},
                  {'role': 'assistant', 'content': f"{rejected_advice}"}
                ]
                prompt_plus_rejected_response = self.tokenizer.apply_chat_template(message, tokenize=False)
        
                
                #prompts = chosen_prompts+rejected_prompts
                #inputs = tokenizer(prompts, **kwargs)
        
                #chosen_reject_similarities = advice_similarities[chosen_ids][:, rejected_ids]
        
                tokens_chosen = tokenizer.encode_plus(prompt_plus_chosen_response, **kwargs)
                tokens_rejected = tokenizer.encode_plus(prompt_plus_rejected_response, **kwargs)
                
                return {
                    "input_ids_chosen": tokens_chosen["input_ids"][0], "attention_mask_chosen": tokens_chosen["attention_mask"][0],
                    "input_ids_rejected": tokens_rejected["input_ids"][0], "attention_mask_rejected": tokens_rejected["attention_mask"][0]
                }
        
                '''
                return {
                    "num_chosen":len(chosen_prompts), "num_rejected":len(rejected_prompts),
                    "input_ids":inputs["input_ids"], "attention_mask":inputs["attention_mask"],
                    
                    #"chosen_reject_similarities":chosen_reject_similarities,
                }
                '''
        
            formatted_dataset = dataset1.map(formatting_func)
        
            if os.path.exists(train_ids_save_path) and os.path.exists(test_ids_save_path):
                with open(train_ids_save_path) as f:
                    train_indices = json.load(f)
                with open(test_ids_save_path) as f:
                    test_indices = json.load(f)
                    
                #formatted_dataset['test'] = formatted_dataset.select(test_indices)
                #formatted_dataset['train'] = formatted_dataset.select(train_indices)
        
                from datasets import DatasetDict
                formatted_dataset = DatasetDict({
                    "train": formatted_dataset.select(train_indices),
                    "test": formatted_dataset.select(test_indices)
                })
        
            else:
                # Get the total number of samples in the dataset
                total_samples = len(formatted_dataset)
                
                # Generate random indices for the test set using PyTorch
                test_indices = torch.randperm(total_samples)[:test_size]
                
                # Create the train set by excluding the test indices using set difference
                all_indices = set(range(total_samples))
                test_indices_set = set(test_indices.tolist())
                train_indices = list(all_indices - test_indices_set)
        
                from datasets import DatasetDict
                formatted_dataset = DatasetDict({
                    "train": formatted_dataset.select(train_indices),
                    "test": formatted_dataset.select(test_indices.tolist())
                })
        
                with open(train_ids_save_path, "w") as f:
                    json.dump(train_indices, f)
                with open(test_ids_save_path, "w") as f:
                    json.dump(test_indices.tolist(), f)
                
                #formatted_dataset['test'] = formatted_dataset.select(test_indices.tolist())
                #formatted_dataset['train'] = formatted_dataset.select(train_indices)
        
            #formatted_dataset = formatted_dataset.train_test_split(test_size=test_size)
            formatted_dataset.save_to_disk(dataset_save_path)
        else:
            formatted_dataset = load_from_disk(dataset_save_path)
            

        return formatted_dataset

    
    def train(self,
              formatted_dataset,
              training_args = None,
              peft_config = None,
             ):

        # Configuring the training arguments
        if not training_args:
            training_args = RewardConfig(  #TrainingArguments(   #CustomRewardTrainer( #
                output_dir=model_save_dir,
                per_device_train_batch_size=batch_size_per_device,
                per_device_eval_batch_size=eval_batch_size_per_device,
                evaluation_strategy="steps",
                eval_steps=20,
                eval_on_start=True,
                save_steps=20,
                logging_steps=1,
                num_train_epochs = 3,
                report_to=None,
                remove_unused_columns=False,
            )
        
        
        if not peft_config:
            peft_config = LoraConfig(
                task_type=TaskType.SEQ_CLS,
                inference_mode=False,
                target_modules=["k_proj","q_proj","o_proj", "v_proj","down_proj","gate_proj","up_proj",],
                layers_to_transform=[25,26,27],
                r=16,
                lora_alpha=16,
                lora_dropout=0.1,
            )
        
        self.model = get_peft_model(self.model, peft_config)
        
        def custom_data_collator(features):
            batch = {}
            
            # For fields that are tensors, we stack them.
            
            tensor_fields = [
                "input_ids", "attention_mask",
            ]
            '''
            tensor_fields = [
                "input_ids_chosen", "attention_mask_chosen",
                "input_ids_rejected", "attention_mask_rejected"
            ]
            '''
            
            for field in tensor_fields:
                batch[field] = torch.stack([torch.tensor(f[field]) for f in features])  #[num_gpus, num_advice_per_batch, max_length]
            
            # For the original prompts (strings), we simply collect them in a list.
            non_tensor_fields = ["num_chosen", "num_rejected", "problem_id"]
            for field in non_tensor_fields:
                batch[field] = [f[field] for f in features]
            
            return batch
        
        if num_gpu*batch_size_per_device != 1:
            num_trash = len(formatted_dataset["train"])%(num_gpu*batch_size_per_device)
            formatted_dataset["train"] = formatted_dataset["train"].select(range(len(formatted_dataset["train"])-num_trash))
            num_trash = len(formatted_dataset["test"])%(num_gpu*batch_size_per_device)
            formatted_dataset["test"] = formatted_dataset["test"].select(range(len(formatted_dataset["test"])-num_trash))
            
        # Loading the RewardTrainer from TRL
        trainer = CustomRewardTrainer(
        #trainer = RewardTrainer(
            model=self.model,
            args=training_args,
            tokenizer=self.tokenizer,
            train_dataset=formatted_dataset["train"],
            eval_dataset=formatted_dataset["test"],
            #data_collator=custom_data_collator,
            #peft_config=peft_config,
        )
        
        accelerator = trainer.accelerator
        model = model.to(accelerator.device)
        
        train_output = trainer.train()





