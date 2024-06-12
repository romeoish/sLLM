import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, pipeline
from utils.prompter import Prompter

bnb_config = BitsAndBytesConfig(
    quant_type="int8",  # Specify 8-bit quantization
    compute_dtype=torch.float32  # Set the compute dtype for 8-bit quantization
)

model_id = "nlpai-lab/kullm-polyglot-12.8b-v2"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, quantization_config=bnb_config, device_map='auto')

pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
prompter = Prompter("kullm")

def infer(instruction="", input_text=""):
    prompt = prompter.generate_prompt(instruction, input_text)
    output = pipe(
        prompt, max_length=1025,
        do_sample=True,
        #truncation = True,
        #min_length = 100,
        temperature=0.3,
        repetition_penalty=3.0,
        num_beams=5,
        eos_token_id=2
    )
    s = output[0]["generated_text"]
    result = prompter.get_response(s)

    return result