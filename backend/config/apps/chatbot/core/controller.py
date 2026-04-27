from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import logging

from config.apps.chatbot.intent.parser import IntentParser, ParseContext, IntentParseResult
from config.apps.chatbot.validation.validator import CommandValidator, ValidationContext, ValidationResult
from config.apps.chatbot.execution.executor import CommandExecutor
from config.apps.chatbot.storage.session_store import SessionStore
from config.apps.chatbot.storage.message_store import MessageStore
from config.apps.chatbot.schema.commands import ChatCommand
from config.apps.chatbot.schema.responses import ChatResponse, generate_follow_up

logger = logging.getLogger(__name__)


@dataclass
class UserContext:
    user_id: int
    username: str
    role: str
    session_id: str


@dataclass
class CommandContext:
    command: str
    missing_fields: list[str] = field(default_factory=list)


class ChatController:
    def __init__(
        self,
        parser: IntentParser | None = None,
        validator: CommandValidator | None = None,
        executor: CommandExecutor | None = None,
        session_store: SessionStore | None = None,
        message_store: MessageStore | None = None,
    ):
        self.parser = parser or IntentParser()
        self.validator = validator or CommandValidator()
        self.executor = executor or CommandExecutor()
        self.session_store = session_store or SessionStore()
        self.message_store = message_store or MessageStore()

    def process(self, user_input: str, user_context: UserContext) -> ChatResponse:
        logger.info(f"[{user_context.session_id}] Stage: input received")
        
        session = self.session_store.get(user_context.session_id)
        if not session:
            session = self.session_store.create(user_context.session_id, user_context.user_id)
        
        self.message_store.add(user_context.session_id, "user", user_input, user_id=user_context.user_id)

        logger.info(f"[{user_context.session_id}] Stage: parsing")
        parse_result = self._parse(user_input, user_context)
        
        if parse_result.is_raw:
            reply = self._handle_raw_parse(parse_result)
            self.message_store.add(user_context.session_id, "assistant", reply, user_id=user_context.user_id)
            return ChatResponse(reply=reply, executed=False, context={"stage": "raw"})

        if parse_result.errors:
            logger.warning(f"[{user_context.session_id}] Parse errors: {parse_result.errors}")
            reply = self._format_parser_errors(parse_result.errors)
            self.message_store.add(user_context.session_id, "assistant", reply, user_id=user_context.user_id)
            return ChatResponse(reply=reply, executed=False, context={"stage": "parse"})

        if not parse_result.command:
            logger.warning(f"[{user_context.session_id}] No command parsed")
            reply = "I couldn't understand your message. Could you please rephrase?"
            self.message_store.add(user_context.session_id, "assistant", reply, user_id=user_context.user_id)
            return ChatResponse(reply=reply, executed=False, context={"stage": "parse"})

        if parse_result.missing_fields:
            logger.info(f"[{user_context.session_id}] Missing fields: {parse_result.missing_fields}")
            session.missing_fields = parse_result.missing_fields
            session.pending_command = {
                "command": parse_result.command.command,
                "parameters": parse_result.command.parameters,
            }
            self.session_store.update(
                user_context.session_id,
                missing_fields=parse_result.missing_fields,
                pending_command=session.pending_command,
            )
            reply = generate_follow_up(parse_result.command.command, parse_result.missing_fields)
            self.message_store.add(user_context.session_id, "assistant", reply, user_id=user_context.user_id)
            return ChatResponse(reply=reply, executed=False, missing_fields=parse_result.missing_fields)

        if session.pending_command and parse_result.missing_fields:
            merged_params = {**session.pending_command["parameters"], **parse_result.command.parameters}
            parse_result.command.parameters = merged_params
            parse_result.missing_fields = []
            for field in session.missing_fields:
                if field not in merged_params:
                    parse_result.missing_fields.append(field)

            if parse_result.missing_fields:
                reply = generate_follow_up(parse_result.command.command, parse_result.missing_fields)
                self.message_store.add(user_context.session_id, "assistant", reply, user_id=user_context.user_id)
                return ChatResponse(reply=reply, executed=False, missing_fields=parse_result.missing_fields)

            self.session_store.clear_pending(user_context.session_id)

        logger.info(f"[{user_context.session_id}] Stage: validating")
        validation_result = self._validate(parse_result.command, user_context)
        if not validation_result.valid:
            logger.warning(f"[{user_context.session_id}] Validation errors: {validation_result.errors}")
            reply = self._format_validation_errors(validation_result.errors)
            self.message_store.add(user_context.session_id, "assistant", reply, user_id=user_context.user_id)
            return ChatResponse(reply=reply, executed=False, context={"stage": "validation"})

        if validation_result.missing_fields:
            reply = generate_follow_up(validation_result.sanitized_command.command, validation_result.missing_fields)
            self.message_store.add(user_context.session_id, "assistant", reply, user_id=user_context.user_id)
            return ChatResponse(reply=reply, executed=False, missing_fields=validation_result.missing_fields)

        logger.info(f"[{user_context.session_id}] Stage: executing")
        execution_result = self._execute(validation_result.sanitized_command, user_context)
        if execution_result.success:
            logger.info(f"[{user_context.session_id}] Execution successful")
            reply = execution_result.result.get("message", "Done!") if execution_result.result else "Done!"
        else:
            if execution_result.missing_fields:
                missing = execution_result.missing_fields[0]
                reply = execution_result.errors[0] if execution_result.errors else f"Could you provide the {missing}?"
                self.message_store.add(user_context.session_id, "assistant", reply, user_id=user_context.user_id)
                return ChatResponse(
                    reply=reply,
                    executed=False,
                    missing_fields=execution_result.missing_fields,
                )
            reply = self._format_execution_errors(execution_result.errors)

        self.message_store.add(user_context.session_id, "assistant", reply, user_id=user_context.user_id)
        return ChatResponse(
            reply=reply,
            executed=execution_result.success,
            context={"result": execution_result.result} if execution_result.result else None,
        )

    def _parse(self, user_input: str, user_context: UserContext) -> IntentParseResult:
        try:
            context = ParseContext(
                user_id=user_context.user_id,
                username=user_context.username,
                role=user_context.role,
            )
            return self.parser.parse_intent(user_input, context)
        except Exception:
            return IntentParseResult(command=None, errors=["Failed to parse input"])

    def _validate(self, command: ChatCommand, user_context: UserContext) -> ValidationResult:
        try:
            context = ValidationContext(
                user_id=user_context.user_id,
                username=user_context.username,
                role=user_context.role,
            )
            return self.validator.validate(command, context)
        except Exception:
            return ValidationResult(valid=False, errors=["Failed to validate command"], sanitized_command=None)

    def _execute(self, command: ChatCommand, user_context: UserContext) -> Any:
        try:
            return self.executor.execute(command, {"user_id": user_context.user_id, "role": user_context.role})
        except Exception as e:
            from config.apps.chatbot.execution.registry import ExecutionResult
            return ExecutionResult(success=False, errors=[str(e)])

    def _format_parser_errors(self, errors: list[str]) -> str:
        return "I had trouble understanding that. " + "; ".join(errors)

    def _handle_raw_parse(self, parse_result: IntentParseResult) -> str:
        if parse_result.errors:
            error = parse_result.errors[0]
            if "invalid_json" in error:
                return "I couldn't understand that. Could you rephrase as a specific command? For example: 'create a project called MyApp' or 'list my projects'."
        return "I couldn't understand your request. Please try rephrasing it as a specific command like 'create a project' or 'list tasks'."

    def _format_validation_errors(self, errors: list[str]) -> str:
        return "I couldn't process that request: " + "; ".join(errors)

    def _format_execution_errors(self, errors: list[str] | None) -> str:
        if not errors:
            return "Something went wrong. Please try again."
        return "Operation failed: " + "; ".join(errors)

    def _format_success(self, result: dict | None) -> str:
        if not result:
            return "Done!"
        return result.get("message", "Operation completed successfully.")