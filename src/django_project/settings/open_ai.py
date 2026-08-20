from django_project.settings import env

OPENAI_API_KEY = env("OPENAI_API_KEY", default="unset")
ANALYZER_LLM_MODEL = env("ANALYZER_LLM_MODEL", default="gpt-5.4")
