from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Optional, Union
from uuid import uuid4

from orjson import dumps as orjson_dumps
from orjson import loads as orjson_loads

from app.globals import DEFAULT_LLM_MODEL, OPENAI_API_KEY
from gpt.tokenizers import BaseTokenizer, LlamaTokenizer, OpenAITokenizer


class UTC:
    def __init__(self):
        self.utc_now = datetime.utcnow()

    @classmethod
    def now(cls, hour_diff: int = 0) -> datetime:
        return cls().utc_now + timedelta(hours=hour_diff)

    @classmethod
    def date(cls, hour_diff: int = 0) -> date:
        return cls.now(hour_diff=hour_diff).date()

    @classmethod
    def timestamp(cls, hour_diff: int = 0) -> int:
        return int(cls.now(hour_diff=hour_diff).strftime("%Y%m%d%H%M%S"))

    @classmethod
    def timestamp_to_datetime(cls, timestamp: int, hour_diff: int = 0) -> datetime:
        return datetime.strptime(str(timestamp), "%Y%m%d%H%M%S") + timedelta(
            hours=hour_diff
        )

    @classmethod
    def date_code(cls, hour_diff: int = 0) -> int:
        return int(cls.date(hour_diff=hour_diff).strftime("%Y%m%d"))


@dataclass
class LLMModel:
    name: str  # model name
    max_total_tokens: int
    max_tokens_per_request: int
    token_margin: int
    tokenizer: BaseTokenizer


@dataclass
class OpenAIModel(LLMModel):
    api_url: str = "https://api.openai.com/v1/chat/completions"
    api_key: str | None = field(repr=False, default=None)


@dataclass
class MessageHistory:
    role: str
    content: str
    tokens: int
    is_user: bool
    timestamp: int = field(default_factory=UTC.timestamp)
    uuid: str = field(default_factory=lambda: uuid4().hex)
    model_name: str | None = None

    def __post_init__(self):
        self.role = GptRoles.get_value(self.role)

    def __repr__(self) -> str:
        return f'<{self.role} uuid="{self.uuid}" date="{self.datetime}" tokens="{self.tokens}">{self.content}</>'

    @property
    def datetime(self) -> datetime:
        return UTC.timestamp_to_datetime(self.timestamp)


@dataclass
class LlamaCppModel(LLMModel):
    model_path: str  # The path to the Llama model file.
    lora_base: Optional[str] = None  # The path to the Llama LoRA base model.
    lora_path: Optional[
        str
    ] = None  # The path to the Llama LoRA. If None, no LoRa is loaded.
    n_parts: int = (
        -1
    )  # Number of parts to split the model into. If -1, the number of parts is automatically determined.
    seed: int = -1  # Seed. If -1, a random seed is used.
    f16_kv: bool = True  # Use half-precision for key/value cache.
    logits_all: bool = False  # Return logits for all tokens, not just the last token.
    vocab_only: bool = False  # Only load the vocabulary, no weights.
    use_mlock: bool = False  # Force system to keep model in RAM.
    n_batch: int = 8  # Number of tokens to process in parallel. Should be a number between 1 and n_ctx.
    last_n_tokens_size: int = (
        64  # The number of tokens to look back when applying the repeat_penalty.
    )
    use_mmap: bool = True  # Whether to use memory mapping for the model.
    streaming: bool = True  # Whether to stream the results, token by token.
    n_threads: Optional[
        int
    ] = None  # Number of threads to use. If None, the number of threads is automatically determined.
    suffix: Optional[
        str
    ] = None  # A suffix to append to the generated text. If None, no suffix is appended.
    temperature: Optional[float] = 0.8  # The temperature to use for sampling.
    top_p: Optional[float] = 0.95  # The top-p value to use for sampling.
    logprobs: Optional[
        int
    ] = None  # The number of logprobs to return. If None, no logprobs are returned.
    echo: Optional[bool] = False  # Whether to echo the prompt.
    stop: Optional[list[str]] = field(
        default_factory=lambda: ["\u200b"]
    )  # A list of strings to stop generation when encountered.
    repeat_penalty: Optional[float] = 1.1  # The penalty to apply to repeated tokens.
    top_k: Optional[int] = 40  # The top-k value to use for sampling.
    description: Optional[
        str
    ] = None  # A prefix to prepend to the generated text. If None, no prefix is prepended.

    def __post_init__(self):
        if self.description is not None:
            self.description_tokens = self.tokenizer.tokens_of(self.description)


class LLMModels(Enum):  # gpt models for openai api
    gpt_3_5_turbo = OpenAIModel(
        name="gpt-3.5-turbo",
        max_total_tokens=4096,
        max_tokens_per_request=2048,
        token_margin=8,
        tokenizer=OpenAITokenizer("gpt-3.5-turbo"),
        api_url="https://api.openai.com/v1/chat/completions",
        api_key=OPENAI_API_KEY,
    )
    gpt_3_5_turbo_proxy = OpenAIModel(
        name="gpt-3.5-turbo",
        max_total_tokens=4096,
        max_tokens_per_request=2048,
        token_margin=8,
        tokenizer=OpenAITokenizer("gpt-3.5-turbo"),
        api_url="https://whocars123-oai-proxy.hf.space/proxy/openai/v1/chat/completions",
        api_key="SOME_API_KEY",
    )
    gpt_4 = OpenAIModel(
        name="gpt-4",
        max_total_tokens=8192,
        max_tokens_per_request=4096,
        token_margin=8,
        tokenizer=OpenAITokenizer("gpt-4"),
        api_url="https://api.openai.com/v1/chat/completions",
        api_key=OPENAI_API_KEY,
    )
    gpt_4_proxy = OpenAIModel(
        name="gpt-4",
        max_total_tokens=8192,
        max_tokens_per_request=4096,
        token_margin=8,
        tokenizer=OpenAITokenizer("gpt-4"),
        api_url="https://whocars123-oai-proxy.hf.space/proxy/openai/v1/chat/completions",
        api_key="SOME_API_KEY",
    )
    vicuna = LlamaCppModel(
        name="wizard-vicuna-13B-ggml-q5-1",
        max_total_tokens=2048,  # context tokens (n_ctx)
        max_tokens_per_request=1024,  # The maximum number of tokens to generate.
        token_margin=8,
        tokenizer=LlamaTokenizer("junelee/wizard-vicuna-13b"),
        model_path="./llama_models/ggml/wizard-vicuna-13B.ggml.q5_1.bin",
        description="""The following is a friendly conversation between a {user} and an {gpt}. The {gpt} is talkative and provides lots of specific details from its context. If the {gpt} does not know the answer to a question, it truthfully says it does not know:\n""",
    )
    vicuna_uncensored = LlamaCppModel(
        name="wizard-vicuna-7B-uncensored-ggml-q4-2",
        max_total_tokens=2048,  # context tokens (n_ctx)
        max_tokens_per_request=1024,  # The maximum number of tokens to generate.
        token_margin=8,
        tokenizer=LlamaTokenizer("junelee/wizard-vicuna-13b"),
        model_path="./llama_models/ggml/WizardLM-7B-uncensored.ggml.q4_2.bin",
        description="""The following is a conversation between a {user} and an {gpt}. The {gpt} is talkative and provides lots of specific details from its context. If the {gpt} does not know the answer to a question, it truthfully says it does not know:\n""",
    )
    gpt4x = LlamaCppModel(
        name="gpt4-x-vicuna-13B-GGML",
        max_total_tokens=2048,  # context tokens (n_ctx)
        max_tokens_per_request=1024,  # The maximum number of tokens to generate.
        token_margin=8,
        tokenizer=LlamaTokenizer("junelee/wizard-vicuna-13b"),
        model_path="./llama_models/ggml/gpt4-x-vicuna-13B.ggml.q4_0.bin",
        description="""The following is a conversation between a {user} and an {gpt}. The {gpt} is talkative and provides lots of specific details from its context. If the {gpt} does not know the answer to a question, it truthfully says it does not know:\n""",
    )


class GptRoles(str, Enum):
    GPT = "assistant"
    SYSTEM = "system"
    USER = "user"

    @classmethod
    def get_name(cls, role: Union["GptRoles", str]) -> str:
        if isinstance(role, cls):  # when role is member
            return role.name
        elif not isinstance(role, str):
            raise ValueError(f"Invalid role: {role}")
        elif role in cls._value2member_map_:  # when role is value
            return cls._value2member_map_[role].name
        elif role.upper() in cls._member_map_:  # when role is name
            return role
        else:
            raise ValueError(f"Invalid role: {role}")

    @classmethod
    def get_value(cls, role: Union["GptRoles", str]) -> str:
        if isinstance(role, cls):  # when role is member
            return role.value
        elif not isinstance(role, str):
            raise ValueError(f"Invalid role: {role}")
        elif role in cls._value2member_map_:  # when role is value
            return role
        elif role.upper() in cls._member_map_:  # when role is name
            return cls._member_map_[role.upper()].value
        else:
            raise ValueError(f"Invalid role: {role}")

    @classmethod
    def get_member(cls, role: Union["GptRoles", str]) -> Enum:
        if isinstance(role, cls):  # when role is member
            return role
        elif role in cls._value2member_map_:  # when role is value
            return cls._value2member_map_[role]
        elif not isinstance(role, str):
            raise ValueError(f"Invalid role: {role}")
        elif role.upper() in cls._member_map_:  # when role is name
            return cls._member_map_[role.upper()]
        else:
            raise ValueError(f"Invalid role: {role}")


@dataclass
class UserGptProfile:  # user gpt profile for user and gpt
    user_id: int
    chatroom_id: int
    created_at: int = field(default_factory=lambda: UTC.timestamp(hour_diff=9))
    user_role: str = field(default=GptRoles.USER.value)
    gpt_role: str = field(default=GptRoles.GPT.value)
    system_role: str = field(default=GptRoles.SYSTEM.value)
    temperature: float = 0.9
    top_p: float = 1.0
    presence_penalty: float = 0
    frequency_penalty: float = 1.1


@dataclass
class UserGptContext:
    """
    user gpt context for user and gpt
    """

    user_gpt_profile: UserGptProfile
    gpt_model: LLMModels
    # message histories
    user_message_histories: list[MessageHistory] = field(default_factory=list)
    gpt_message_histories: list[MessageHistory] = field(default_factory=list)
    system_message_histories: list[MessageHistory] = field(default_factory=list)
    # message tokens
    user_message_tokens: int = field(init=False, default=0)
    gpt_message_tokens: int = field(init=False, default=0)
    system_message_tokens: int = field(init=False, default=0)

    optional_info: dict = field(default_factory=dict)

    def __post_init__(self):
        for role in tuple(
            key.split("_")[0]
            for key in self.__annotations__.keys()
            if "message_tokens" in key.lower()
        ):
            setattr(
                self,
                f"{role}_message_tokens",
                sum([m.tokens for m in getattr(self, f"{role}_message_histories")]),
            )

    @classmethod
    def parse_stringified_json(cls, stred_json: str) -> "UserGptContext":
        stored: dict = orjson_loads(stred_json)
        return cls(
            user_gpt_profile=UserGptProfile(**stored["user_gpt_profile"]),
            gpt_model=LLMModels._member_map_[stored["gpt_model"].replace(".", "_").replace("-", "_")],  # type: ignore
            user_message_histories=[
                MessageHistory(**m) for m in stored["user_message_histories"]
            ],
            gpt_message_histories=[
                MessageHistory(**m) for m in stored["gpt_message_histories"]
            ],
            system_message_histories=[
                MessageHistory(**m) for m in stored["system_message_histories"]
            ],
        )

    def json(self) -> dict:
        return {
            "user_gpt_profile": asdict(self.user_gpt_profile),
            "gpt_model": self.gpt_model.name,
            "user_message_histories": [m.__dict__ for m in self.user_message_histories],
            "gpt_message_histories": [m.__dict__ for m in self.gpt_message_histories],
            "system_message_histories": [
                m.__dict__ for m in self.system_message_histories
            ],
        }

    def to_stringified_json(self) -> str:
        return orjson_dumps(self.json()).decode("utf-8")

    def tokenize(self, message: str) -> list[int]:
        return self.gpt_model.value.tokenizer.encode(message)

    def get_tokens_of(self, message: str) -> int:
        return len(self.tokenize(message))

    @property
    def left_tokens(self) -> int:
        return (
            self.gpt_model.value.max_total_tokens
            - self.total_tokens
            - self.gpt_model.value.token_margin
            - int(getattr(self.gpt_model.value, "description_tokens", 0))
        )

    @property
    def total_tokens(self) -> int:
        return (
            self.user_message_tokens
            + self.gpt_message_tokens
            + self.system_message_tokens
        )

    @property
    def token_per_request(self) -> int:
        return self.gpt_model.value.max_tokens_per_request

    @property
    def user_id(self) -> str:
        return str(self.user_gpt_profile.user_id)

    @property
    def chatroom_id(self) -> str:
        return self.user_gpt_profile.chatroom_id

    def __repr__(self) -> str:
        gpt_model: LLMModels = self.gpt_model
        time_string: str = datetime.strptime(
            str(self.user_gpt_profile.created_at),
            "%Y%m%d%H%M%S",
        ).strftime("%Y-%m-%d %H:%M:%S")
        return f"""# User Info
- Your ID: `{self.user_id}`
- This chatroom ID: `{self.chatroom_id}`
- Your profile created at: `{time_string}`

# LLM Info
- Model Name: `{gpt_model.name}`
- Actual Model Name: `{gpt_model.value.name}`
- Temperature: `{self.user_gpt_profile.temperature}`
- Top P: `{self.user_gpt_profile.top_p}`
- Presence Penalty: `{self.user_gpt_profile.presence_penalty}`
- Frequency Penalty: `{self.user_gpt_profile.frequency_penalty}`

# Token Info
- Maximum Token Limit: `{gpt_model.value.max_total_tokens}`
- User Token Consumed: `{self.user_message_tokens}`
- GPT Token Consumed: `{self.gpt_message_tokens}`
- System Token Consumed: `{self.system_message_tokens}`
- Total Token Consumed: `{self.total_tokens}`
- Remaining Tokens: `{self.left_tokens}`

# Message Histories
- User Message_Histories={self.user_message_histories}

- GPT Message Histories={self.gpt_message_histories}

- System Message Histories={self.system_message_histories}
"""

    @classmethod
    def construct_default(
        cls,
        user_id: int,
        chatroom_id: int,
        gpt_model: LLMModels = getattr(
            LLMModels,
            DEFAULT_LLM_MODEL,
            LLMModels.gpt_3_5_turbo,
        ),
    ):
        return cls(
            user_gpt_profile=UserGptProfile(user_id=user_id, chatroom_id=chatroom_id),
            gpt_model=gpt_model,
        )

    def reset(self):
        for k, v in self.construct_default(
            self.user_id,
            self.chatroom_id,
            self.gpt_model,
        ).__dict__.items():
            setattr(self, k, v)

    def copy_from(self, user_gpt_context: "UserGptContext") -> None:
        for k, v in user_gpt_context.__dict__.items():
            setattr(self, k, v)

    def ensure_token_not_exceed(self) -> int:
        deleted_histories: int = 0
        while (
            len(self.user_message_histories) > 0
            and len(self.gpt_message_histories) > 0
            and self.left_tokens < 0
        ):
            deleted_histories += 1
            self.user_message_tokens -= self.user_message_histories.pop(0).tokens
            self.gpt_message_tokens -= self.gpt_message_histories.pop(0).tokens
        return deleted_histories

    def clear_tokens(self, tokens_to_remove: int) -> int:
        deleted_histories: int = 0
        removed_tokens: int = 0
        while (
            len(self.user_message_histories) > 0
            and len(self.gpt_message_histories) > 0
            and removed_tokens < tokens_to_remove
        ):
            deleted_histories += 1
            self.user_message_tokens -= self.user_message_histories.pop(0).tokens
            self.gpt_message_tokens -= self.gpt_message_histories.pop(0).tokens
        return deleted_histories
