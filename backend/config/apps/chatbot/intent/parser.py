import json
from dataclasses import dataclass
from typing import Optional

from config.apps.chatbot.llm.ollama_client import OllamaClient
from config.apps.chatbot.schema.commands import ChatCommand, IntentParseResult, VALID_COMMANDS, CommandType


SYSTEM_PROMPT = """You are a strict JSON translator. Your ONLY job is to convert user messages into valid command JSON.

RULES:
1. Output ONLY valid JSON - no text before, during, or after
2. Never explain your reasoning - only output JSON
3. Use EXACTLY these commands: {valid_commands}
4. Parameters must match the capability contract exactly
5. If unsure or cannot determine intent → return: {{"command": "unknown", "parameters": {{}}, "missing_fields": []}}
6. NEVER invent commands, fields, or values outside the contract
7. If user asks a question (not a command) → return unknown
8. Provide INTELLIGENT DEFAULTS when user doesn't specify: 
   - project_description → use project_name as description if not provided
   - status → always use "active" if not specified
   - progress → use 0 if not specified
   - milestone → use null if not provided for tasks

Capability Contract:
- create_project: project_name (REQUIRED), project_description (optional, defaults to project_name), status (optional, defaults to "active"), progress (optional, defaults to 0), start_date (optional), due_date (optional), team_members (optional)
- update_project: project_id, project_name (optional), project_description (optional), status (optional), progress (optional), start_date (optional), due_date (optional), team_members (optional)
- delete_project: project_id
- create_task: title (REQUIRED), project (REQUIRED), milestone (optional), description (optional), status (optional, defaults to "todo"), assignee (optional)
- update_task: task_id, title (optional), description (optional), status (optional), project (optional), milestone (optional), assignee (optional)
- delete_task: task_id
- list_projects: (all, no parameters required)
- list_tasks: project (optional), status (optional)
- get_milestones: project
- create_risk: project, description, severity (optional)
- generate_report: (all, no parameters required)

Output format (JSON ONLY, no explanations):
{{
    "command": "command_name",
    "parameters": {{"field": "value"}},
    "missing_fields": [],
    "uncertain": false
}}

If unable to parse intent, respond with EXACTLY:
{{"command": "unknown", "parameters": {{}}, "missing_fields": []}}"""


@dataclass
class ParseContext:
    user_id: int
    username: str
    role: str


class IntentParser:
    def __init__(self, llm_client: Optional[OllamaClient] = None):
        self.llm = llm_client or OllamaClient()

    def parse_intent(
        self,
        user_input: str,
        context: ParseContext,
    ) -> IntentParseResult:
        if not user_input or not user_input.strip():
            return IntentParseResult(
                command=None,
                errors=["Empty user input"],
            )

        prompt = self._build_prompt(user_input, context)
        llm_result = self.llm.generate(prompt, system_prompt=SYSTEM_PROMPT)

        if not llm_result.success:
            return IntentParseResult(
                command=None,
                errors=[f"LLM error: {llm_result.error}"],
            )

        return self._parse_response(llm_result.content)

    def _build_prompt(self, user_input: str, context: ParseContext) -> str:
        return f"""User ({context.username}, role={context.role}): {user_input}

Respond with JSON only:"""

    def _parse_response(self, raw_output: str) -> IntentParseResult:
        if not raw_output or not raw_output.strip():
            return IntentParseResult(
                command=None,
                errors=["invalid_json"],
                raw_text=raw_output,
            )

        cleaned = self._clean_json_output(raw_output)

        command_result = self._try_parse_command(cleaned)
        if command_result is not None:
            return command_result

        return IntentParseResult(
            command=None,
            errors=["invalid_json"],
            raw_text=raw_output,
        )

    def _clean_json_output(self, raw: str) -> str:
        cleaned = raw.strip()
        
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        cleaned = cleaned.strip()
        
        cleaned = cleaned.replace("{{", "{").replace("}}", "}")
        
        import re
        cleaned = re.sub(r'//.*?$', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)
        
        return cleaned.strip()

    def _try_parse_command(self, cleaned: str) -> Optional[IntentParseResult]:
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            return None

        if not isinstance(data, dict):
            return None

        command = data.get("command")
        if command not in VALID_COMMANDS:
            return IntentParseResult(
                command=None,
                errors=[f"unknown_intent: {command}"],
                raw_text=cleaned,
            )

        return IntentParseResult(
            command=ChatCommand(
                command=command,
                parameters=data.get("parameters", {}),
            ),
            missing_fields=data.get("missing_fields", []) or [],
        )