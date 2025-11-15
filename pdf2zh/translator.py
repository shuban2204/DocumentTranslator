import html
import json
import logging
import os
import re
import unicodedata
from copy import copy
from string import Template
from typing import cast

import requests
from dotenv import load_dotenv

from google import genai

from pdf2zh.cache import TranslationCache
from pdf2zh.config import ConfigManager

load_dotenv()

logger = logging.getLogger(__name__)


def remove_control_characters(s):
    return "".join(ch for ch in s if unicodedata.category(ch)[0] != "C")


# ============================================================
#                        BASE TRANSLATOR
# ============================================================
class BaseTranslator:
    name = "base"
    envs = {}
    lang_map: dict[str, str] = {}
    CustomPrompt = False

    def __init__(self, lang_in: str, lang_out: str, model: str, ignore_cache: bool):
        lang_in = self.lang_map.get(lang_in.lower(), lang_in)
        lang_out = self.lang_map.get(lang_out.lower(), lang_out)
        self.lang_in = lang_in
        self.lang_out = lang_out
        self.model = model
        self.ignore_cache = ignore_cache

        # Cache system
        self.cache = TranslationCache(
            self.name,
            {
                "lang_in": lang_in,
                "lang_out": lang_out,
                "model": model,
            },
        )

    def set_envs(self, envs):
        """Loads environment variables and configuration overrides"""
        self.envs = copy(self.envs)
        if ConfigManager.get_translator_by_name(self.name):
            self.envs = ConfigManager.get_translator_by_name(self.name)

        needUpdate = False
        for key in self.envs:
            if key in os.environ:
                self.envs[key] = os.environ[key]
                needUpdate = True

        if needUpdate:
            ConfigManager.set_translator_by_name(self.name, self.envs)

        if envs is not None:
            for key in envs:
                self.envs[key] = envs[key]
            ConfigManager.set_translator_by_name(self.name, self.envs)

    def add_cache_impact_parameters(self, k: str, v):
        self.cache.add_params(k, v)

    def translate(self, text: str, ignore_cache: bool = False) -> str:
        if not (self.ignore_cache or ignore_cache):
            cached = self.cache.get(text)
            if cached is not None:
                return cached

        output = self.do_translate(text)
        self.cache.set(text, output)
        return output

    def do_translate(self, text: str) -> str:
        raise NotImplementedError

    # Prompt Builder
    def prompt(self, text: str, prompt_template: Template | None = None):
        try:
            return [
                {
                    "role": "user",
                    "content": cast(Template, prompt_template).safe_substitute(
                        {
                            "lang_in": self.lang_in,
                            "lang_out": self.lang_out,
                            "text": text,
                        }
                    ),
                }
            ]
        except:
            pass

        return [
            {
                "role": "user",
                "content": (
                    "You are a professional translation engine.\n"
                    "Return **only translated text**, no explanations.\n"
                    f"Translate this text into {self.lang_out}.\n"
                    "Do NOT break formatting.\n\n"
                    f"Source Text:\n{text}\n\nTranslated Text:"
                ),
            }
        ]


# ============================================================
#                     GEMINI TRANSLATOR
# ============================================================

decomposition_prompt = Template(
    "Translate the following text from ${lang_in} to ${lang_out}.\n"
    "Maintain formatting, table structure, line breaks, and math placeholders.\n"
    "Text:\n${text}"
)


class GeminiTranslator(BaseTranslator):
    name = "gemini"
    envs = {
        "GEMINI_API_KEY": None,
        "GEMINI_MODEL": "gemini-2.5-flash",
    }
    CustomPrompt = True

    def __init__(
        self,
        lang_in,
        lang_out,
        model=None,
        prompt=decomposition_prompt,
        ignore_cache=False,
        envs=None,
        **kwargs,
    ):
        # Load envs
        self.set_envs(envs)

        # Load API key
        self.api_key = os.getenv("GEMINI_API_KEY") or self.envs["GEMINI_API_KEY"]
        if not self.api_key:
            raise ValueError("❌ Missing GEMINI_API_KEY in .env")

        # Determine model
        self.model = model or os.getenv("GEMINI_MODEL") or self.envs["GEMINI_MODEL"]

        # Init BaseTranslator AFTER model/envs
        super().__init__(lang_in, lang_out, self.model, ignore_cache)

        # Save prompt template
        self.prompttext = prompt

        # Gemini Python Client
        self.client = genai.Client(api_key=self.api_key)

        # Cache prompt impact
        self.add_cache_impact_parameters("prompt", self.prompt("", self.prompttext))

    def do_translate(self, text: str, **kwargs) -> str:
        """Send translation request to Gemini using new models.generate_content() API"""

        user_prompt = self.prompt(text, self.prompttext)[0]["content"]

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=user_prompt
            )

            return response.text

        except Exception as e:
            raise Exception(f"Gemini API Error: {str(e)}")
