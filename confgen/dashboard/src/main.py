from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from httpx import AsyncClient
import uvicorn
from typing import Optional
import os
import re
from nhlib import *

app = FastAPI(title="Nighthawk Dashboard")
client = AsyncClient(timeout=None) 

STATIC_FOLDER = "../static"

app.mount("/static", StaticFiles(directory=STATIC_FOLDER), name="static")

@app.get("/")
async def read_root():
    return FileResponse(f"{STATIC_FOLDER}/index.html")

@app.post("/prompt")
async def prompt(request: Request):
    try:
       
        body = await request.json()  

        if 'prompt' not in body:
            raise HTTPException(status_code=400, detail="Missing 'prompt' key in request body")

        user_prompt = body['prompt']
        selection_prompt = get_selection_prompt(user_prompt)  
        body = {'prompt': selection_prompt}

        res = await client.post(os.getenv('LLM_URL'), json=body)        
 
        probes = res.json()['response']
        
        probes = probes.replace("```json", "").replace("```", "").strip() # removing entual markdown
        response = {'probes': []}
        print(probes)
        pattern = r'\[\s*\{.*?\}\s*\](?=\s*$)'  
        matches = re.findall(pattern, probes, re.DOTALL)
        if matches:
            probes = matches[-1] 
            print("PARSED: " + probes)

        probes = json.loads(probes)
        # Gen the config for each probe
        for probe in probes:
            try:
                confgen_prompt = get_confgen_prompt(probe['probe'], user_prompt)
                confgen_prompt = confgen_prompt + "\nYou now have to configure: " + probe['host'] 
                body = {'prompt': confgen_prompt}
                res = await client.post(os.getenv('LLM_URL'), json=body)
                config = res.json()['response']
                config = config.replace("```json", "").replace("```", "").strip() # removing entual markdown
            except Exception as e: 
                config = "TODO"
            response['probes'].append({'host': probe['host'], 'name': probe['probe'], 'config': config})

        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    return FileResponse(f"{STATIC_FOLDER}/404.html", status_code=404)

if __name__ == "__main__":
    os.makedirs(STATIC_FOLDER, exist_ok=True)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        workers=4,  
        proxy_headers=True,
        forwarded_allow_ips="*",
        access_log=True
    )
