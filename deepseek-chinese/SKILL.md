---
name: deepseek-chinese
description: Flexible utilization of the DeepSeek Reasoner API for enhanced Chinese writing, comprehension, and Classical Chinese tasks. Use this skill when the user requests high-quality Chinese content generation, complex Chinese text analysis, translation involving Chinese (especially Classical Chinese/文言文), or when the project instructions explicitly ask to use the DeepSeek custom API for Chinese processing.
---

# DeepSeek Chinese

## Overview

This skill provides tools and guidelines for leveraging the DeepSeek Reasoner API (`deepseek-reasoner`) to perform advanced Chinese language tasks. The DeepSeek Reasoner model excels at complex reasoning, nuance comprehension, and generating high-quality Chinese text, including Classical Chinese (文言文).

## Core Capabilities

1. **High-Quality Chinese Writing**: Generate professional, academic, or creative Chinese content with native fluency and appropriate tone.
2. **Complex Chinese Comprehension**: Analyze intricate Chinese texts, extract key information, and understand subtle cultural or contextual nuances.
3. **Classical Chinese (文言文) Processing**: Translate between Classical Chinese and Modern Chinese, or analyze Classical Chinese texts with high accuracy.
4. **Translation**: Perform high-fidelity translations between English (or other languages) and Chinese, preserving meaning, tone, and cultural context.

## Workflow

When a task requires advanced Chinese processing, follow these steps:

### 1. Identify the Task Type
Determine if the task involves:
- Modern Chinese writing or editing
- Complex Chinese text comprehension
- Classical Chinese translation or analysis

### 2. Prepare the Prompt
Craft a clear and detailed prompt in Chinese (or English, if translating) for the DeepSeek Reasoner API. 
- For **Analytical Tasks**: Instruct the model to break down the text, explain nuances, and provide structured output.
- For **Writing Tasks**: Specify the desired tone, style, format, and any specific constraints.
- For **Classical Chinese**: Explicitly state whether you need translation to Modern Chinese, translation to English, or literary analysis.

### 3. Invoke the DeepSeek API
Use the provided Python script `scripts/call_deepseek.py` to interact with the DeepSeek Reasoner API. This script handles authentication and API communication.

**Usage:**
```bash
python3 /home/ubuntu/skills/deepseek-chinese/scripts/call_deepseek.py "Your prompt here"
```
Or use it as a module in your own Python scripts.

### 4. Process the Output
Review the output from the DeepSeek API. If the result is not satisfactory, refine your prompt and call the API again. Once you have the desired output, incorporate it into your final deliverable.

## Guidelines for Chinese Prompts

To get the best results from the DeepSeek Reasoner model:

- **Be Specific**: Clearly state the objective, target audience, and desired format.
- **Provide Context**: If analyzing a specific text, provide the full text or relevant excerpts.
- **Set the Persona**: For writing tasks, define the persona (e.g., "You are an expert historian," "You are a professional copywriter").
- **Classical Chinese specific**: When dealing with Classical Chinese, ask the model to provide annotations for difficult words before providing the full translation.

## Example Usage

**Scenario**: The user wants to translate a paragraph of Classical Chinese into Modern Chinese and English.

1. **Prompt Formulation**:
   "请将以下文言文翻译成现代汉语和英语，并对其中的生僻字词进行注释：[文言文内容]"

2. **API Invocation**:
   ```bash
   python3 /home/ubuntu/skills/deepseek-chinese/scripts/call_deepseek.py "请将以下文言文翻译成现代汉语和英语，并对其中的生僻字词进行注释：学而时习之，不亦说乎？有朋自远方来，不亦乐乎？人不知而不愠，不亦君子乎？"
   ```

3. **Result Integration**: Take the output and format it nicely for the user.
