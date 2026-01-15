"""
Shared Gemini AI Service for All 7 Apps
Provides text generation, analysis, and content creation
"""

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from google.cloud import bigquery
import json
from datetime import datetime
from typing import Optional, Dict, Any, List

PROJECT_ID = 'aialgotradehits'
LOCATION = 'us-central1'

vertexai.init(project=PROJECT_ID, location=LOCATION)

MODELS = {
    'pro': 'gemini-2.0-flash-exp',
    'flash': 'gemini-1.5-flash-002',
}


class GeminiService:
    def __init__(self, app_name: str, dataset_name: str):
        self.app_name = app_name
        self.dataset_name = dataset_name
        self.bq_client = bigquery.Client(project=PROJECT_ID)
        self.pro_model = GenerativeModel(MODELS['pro'])
        self.flash_model = GenerativeModel(MODELS['flash'])

    def generate_text(self, prompt: str, system_instruction: str = None, use_pro: bool = True, max_tokens: int = 4096, temperature: float = 0.7) -> Dict[str, Any]:
        model = self.pro_model if use_pro else self.flash_model
        config = GenerationConfig(max_output_tokens=max_tokens, temperature=temperature)
        try:
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
            response = model.generate_content(full_prompt, generation_config=config)
            return {'text': response.text, 'success': True, 'model': MODELS['pro'] if use_pro else MODELS['flash']}
        except Exception as e:
            return {'text': None, 'error': str(e), 'success': False}

    def analyze_json(self, data: Dict, analysis_type: str, context: str = None) -> Dict[str, Any]:
        prompt = f"Analyze this data for {analysis_type}:\n{json.dumps(data, indent=2)}\n{f'Context: {context}' if context else ''}\nReturn JSON with: summary, key_findings, recommendations, risk_factors, score (1-100)."
        result = self.generate_text(prompt, f"You are an expert analyst for {self.app_name}. Return ONLY valid JSON.", True, 4096, 0.3)
        if result['success']:
            try:
                text = result['text']
                if '```json' in text: text = text.split('```json')[1].split('```')[0]
                elif '```' in text: text = text.split('```')[1].split('```')[0]
                result['analysis'] = json.loads(text.strip())
            except: result['analysis'] = {'raw_text': result['text']}
        return result

    def generate_list(self, topic: str, content_type: str, count: int = 5, language: str = 'en') -> Dict[str, Any]:
        lang = "Respond in Urdu" if language == 'ur' else ""
        prompt = f"Generate {count} {content_type} about: {topic}\n{lang}\nFormat as JSON array with: title, description, priority."
        result = self.generate_text(prompt, f"Expert for {self.app_name}. Return ONLY valid JSON array.", False, 2048, 0.8)
        if result['success']:
            try:
                text = result['text']
                if '```' in text: text = text.split('```')[1].split('```')[0].replace('json', '')
                result['items'] = json.loads(text.strip())
            except: result['items'] = []
        return result


def get_gemini_service(app_name: str, dataset_name: str) -> GeminiService:
    return GeminiService(app_name, dataset_name)
