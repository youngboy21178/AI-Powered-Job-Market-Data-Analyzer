from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch, re, json, time
from models import AI_PROMPT  
from huggingface_hub import login
from config import ai_token
import os
from transformers.utils import logging as hf_logging




class JobInfoExtractor:
    _counter = 0
    
    def __init__(self, model_name: str = "Qwen/Qwen3-8B"):
        login(token=ai_token)
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            use_fast=True,
            trust_remote_code=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            quantization_config=bnb_config,
            torch_dtype=torch.float16,
            trust_remote_code=True
        )
        self.model.eval()
        os.environ["TRANSFORMERS_VERBOSITY"] = "error"
        hf_logging.set_verbosity_error()
        hf_logging.disable_progress_bar()

    def extract(self, job_description: dict) -> str:
        start = time.time()
        modified_job_description = str(
            "Job Title: " + str(job_description.get('job_title', 'N/A')) + "Main Description: " + str(job_description.get("job_description", "N/A"))
        )

        prompt = AI_PROMPT.format(description=modified_job_description)

        try:
            with torch.inference_mode():
                inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=500,
                    do_sample=False,
                    use_cache=True,
                    eos_token_id=self.tokenizer.encode("}")[0] 
                )

                content = self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
            if content.startswith(prompt.strip()):
                content = content[len(prompt.strip()):].strip()
            
            matches = re.findall(r"\{(?:[^{}]|(?:\{[^{}]*\}))*\}", content, re.DOTALL)
            
            valid_json = None
            for m in matches:
                try:
                    json.loads(m)
                    valid_json = m
                    break
                except json.JSONDecodeError:
                    continue

            if not valid_json:
                print(f"🟥  [{self._counter}]")
                raise ValueError("No valid JSON found in model output.")
            content = valid_json.replace("None", "null").replace("'", '"')
            
            try:
                json.loads(content)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON extracted: {e}")

            
            self._counter += 1

            print(f"🟩  [{self._counter}]")
            return content

        except Exception as e:
            print(f"Error running Qwen locally: {e}")
            return "{}"
        finally:
            print(f"⏱️ Processed job in {time.time() - start:.2f} seconds")


