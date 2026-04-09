#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.error

def call_deepseek_reasoner(prompt):
    """Calls the DeepSeek Reasoner API with the given prompt."""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("Error: DEEPSEEK_API_KEY environment variable not set.")
        sys.exit(1)

    url = "https://api.deepseek.com/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-reasoner",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    req = urllib.request.Request(
        url, 
        data=json.dumps(data).encode("utf-8"), 
        headers=headers, 
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            
            # DeepSeek Reasoner might return reasoning content in a separate field, 
            # but the final answer is in message.content
            message = result.get("choices", [{}])[0].get("message", {})
            
            # Print reasoning if available (optional, but good for debugging/understanding)
            reasoning = message.get("reasoning_content")
            if reasoning:
                print("--- Reasoning Process ---")
                print(reasoning)
                print("--- End Reasoning ---\n")
                
            content = message.get("content", "")
            print("--- Result ---")
            print(content)
            
            return content
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"HTTP Error {e.code}: {e.reason}")
        print(f"Response body: {error_body}")
        sys.exit(1)
    except Exception as e:
        print(f"Error calling DeepSeek API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 call_deepseek.py \"Your prompt here\"")
        sys.exit(1)
        
    prompt = sys.argv[1]
    call_deepseek_reasoner(prompt)
