from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
import logging
from typing import Optional
import os
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
from transformers import BitsAndBytesConfig
from dotenv import load_dotenv
import regex

# Backend server to receive prompts and relay them to the model
load_dotenv()

MAX_LENGTH = int(os.getenv('MAX_LENGTH'))  # Maximum length of generated text
TEMP = float(os.getenv('TEMP'))  # Temperature 

class PromptRequest(BaseModel):
    prompt: str = Field(..., description="User prompt to send to the model")
    max_length: Optional[int] = Field(default=MAX_LENGTH, description="Maximum length of generated text")
    temperature: Optional[float] = Field(default=TEMP, description="Temperature for text generation")

class PromptResponse(BaseModel):
    response: str
    timestamp: datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()

try:
    model_id = "Qwen/Qwen2.5-Coder-14B-Instruct"
    
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
        
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,  # Use half precision
        device_map="auto",  # Automatically distribute model across available devices
        low_cpu_mem_usage=True,  # Optimize CPU memory usage
    )
    
    # Ensure model and tokenizer are aligned on padding token
    model.config.pad_token_id = tokenizer.pad_token_id
    
    # Create text generation pipeline 
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        torch_dtype=torch.float16,
        device_map="auto",
    )
    
    logger.info("Model pipeline initialized successfully with optimizations")
except Exception as e:
    logger.error(f"Failed to initialize model pipeline: {str(e)}")
    raise

# Just for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error handler caught: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error"
        }
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/prompt")
async def process_prompt(request: Request):
    try:
        content_type = request.headers.get('content-type', '').lower()
        
        body = await request.json()
        prompt = body.get('prompt', '')
        max_length = body.get('max_length', MAX_LENGTH)
        temperature = body.get('temperature', TEMP)

    
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")

        #print(prompt)

        messages = [
            {"role": "user", "content": prompt}
        ]

        with torch.amp.autocast('cuda'): 
            response = pipe(
                messages,
                max_length=max_length,
                temperature=temperature,
                do_sample=True, 
                top_p=0.95,  
                num_return_sequences=1,
                batch_size=1,
                pad_token_id=tokenizer.pad_token_id,
            )

        generated_text = response[0]['generated_text']
        pattern = regex.compile(r'\{(?:[^{}]|(?R))*\}')

        response = ""
        for text in generated_text:
            if text.get("role") == "assistant":
                response = text
        # Clean up CUDA memory after generation
        torch.cuda.empty_cache()
        
        return JSONResponse(content={
            "response": response["content"]
        })
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing prompt: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing prompt: {str(e)}"
        )

if __name__ == "__main__":
    host = os.getenv("API_HOST")
    port = int(os.getenv("API_PORT"))
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )