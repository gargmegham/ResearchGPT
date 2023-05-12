import asyncio
import logging
import os
import pickle
import re
import threading
import time
import traceback
from typing import Literal

import openai
import tiktoken
from colorama import Fore, Style

from .globals import *
from .utils import create_response, time_now_str, warn

logger = logging.getLogger(__name__)


class ResearchGPT(object):
    MAX_TOKENS: int = 4096
    REPLY_COST: int = 2  # every reply is primed with <im_start>assistant, minus 2
    MIN_TOKEN_PER_MSG: int = (
        4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
    )

    def __init__(
        self,
        *,
        api_key: str,
        api_org: str,
        prompts_dir: str = "./prompts",
        model_name: Literal[
            "gpt-3.5-turbo", "gpt-3.5-turbo-0301"
        ] = "gpt-3.5-turbo-0301",
        temperature: float = 1.0,
        min_reply_tokens: int = 800,
        network_err_text: str = "[encountering unknown network error]",
    ):
        """

        :param api_key:
        :param api_org:
        :param prompts_dir:
        :param model_name:
        :param temperature:
        """
        assert model_name in [
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-0301",
        ], f"'model_name' must be one of ['gpt-3.5-turbo', 'gpt-3.5-turbo-0301'] but received '{model_name}'"
        self.model_name = model_name
        assert os.path.exists(prompts_dir), f"prompts_dir '{prompts_dir}' is not found!"
        self.prompts_dir: str = prompts_dir
        self.temperature: float = temperature  # 0.0 ~ 1.0
        self.min_reply_tokens = min_reply_tokens
        self.max_tokens: int = self.MAX_TOKENS - self.REPLY_COST - self.min_reply_tokens

        self.tokenizer = self.load_tokenizer(self.model_name)
        self.prompts_dict = self.load_prompts_dict()
        self.network_err_text = network_err_text

        if api_key is not None:
            openai.api_key = api_key
        if api_org is not None:
            openai.organization = api_org

    def load_prompts_dict(self):
        prompt_fnames = os.listdir(self.prompts_dir)
        if ".DS_Store" in prompt_fnames:
            prompt_fnames.remove(".DS_Store")

        prompts_dict = {}
        for fname in prompt_fnames:
            prompts_dict[fname] = os.path.join(self.prompts_dir, fname)
        return prompts_dict

    def get_prompt(self, prompt: str):
        prompts_dict = self.prompts_dict
        if prompt in prompts_dict:
            with open(prompts_dict[prompt], "r") as f:
                return "".join(f.readlines())
        else:
            self.prompts_dict = prompts_dict = self.load_prompts_dict()
            if prompt in prompts_dict:
                with open(prompts_dict[prompt], "r") as f:
                    return "".join(f.readlines())
            else:
                warn(f"prompt file '{prompt}' under directory '{self.prompts_dir}'")
                return ""

    def launch_researchgpt(self):
        model_name = self.model_name
        status = False

        # noinspection PyBroadException
        try:
            model_list = openai.Model.list().data
            for model_info in model_list:
                if model_info.id == model_name:
                    status = True
                    break
        except Exception:
            traceback.print_exc()
        return status

    @staticmethod
    def load_tokenizer(model_name):
        try:
            tokenizer = tiktoken.encoding_for_model(model_name)
        except KeyError:
            tokenizer = tiktoken.get_encoding("cl100k_base")
        return tokenizer

    def encode_tokens(self, text: str):
        tokens = self.tokenizer.encode(text)
        return tokens

    def decode_tokens(self, tokens):
        return self.tokenizer.decode(tokens)

    def count_context_tokens(self, context: list):
        """
        reference
        https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
        under section: 6. Counting tokens for chat API calls

        See https://github.com/openai/openai-python/blob/main/chatml.md for information on how
        messages are converted to tokens.
        """
        min_token_per_msg = self.MIN_TOKEN_PER_MSG
        num_tokens_list = []
        for message in context:
            num_tokens = min_token_per_msg  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(self.tokenizer.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += -1  # role is always required and always 1 token
            num_tokens_list.append(num_tokens)
        # num_tokens_list.append(self.REPLY_COST)  # every reply is primed with <im_start>assistant
        return num_tokens_list

    def __send_message_stream__(self, context: list):
        """
        Args:
            context:
                    [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Who won the world series in 2020?"},
                        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
                    ]
        Return:
             content: string
             status:  bool, True upon final return
        """

        # noinspection PyBroadException
        try:
            model_name = self.model_name
            temperature = self.temperature

            iterator = openai.ChatCompletion.create(
                model=model_name,
                stream=True,
                temperature=temperature,  # 0.0 ~ 1.0
                # max_tokens=4096,  # <= 4096
                messages=context,
            )

            for res in iterator:
                choice = res.choices[0]
                delta = choice.delta
                # finish_reason = choice.finish_reason
                status = choice.finish_reason is not None
                if len(delta) > 0 and "content" in delta:
                    content = delta.content
                    yield content, status
                if status:
                    break

        except Exception as err:
            traceback.print_exc()
            print("exception text")
            print(str(err))
            print(f"context token size: {self.count_context_tokens(context)}")
            content = self.network_err_text
            status = True
            yield content, status
        finally:
            pass

    def __send_message__(self, context: list):
        model_name = self.model_name
        temperature = self.temperature

        res = openai.ChatCompletion.create(
            model=model_name,
            stream=False,
            temperature=temperature,  # 0.0 ~ 1.0
            # max_tokens=4096,  # <= 4096
            messages=context,
        )
        content: str = res.choices[0].message.content
        return content

    @staticmethod
    def create_context(text: str):
        context = [
            {"role": "user", "content": str(text)},
        ]
        return context

    @staticmethod
    def update_context(context: list, content: str):
        context.append({"role": "assistant", "content": str(content)})
        return context

    def consolidate_context(
        self, context: list, keep_left: int = 2, keep_right: int = 1, max_try: int = 3
    ):
        max_tokens: int = self.max_tokens
        num_tokens_list = self.count_context_tokens(context)
        if sum(num_tokens_list) < max_tokens:
            return context

        """
        summarize aged messages
        """
        summary_request: str = self.get_prompt("context-summarizer.txt")
        summary_req_context: list = [{"role": "system", "content": summary_request}]
        summary_req_n_tokens: int = sum(self.count_context_tokens(summary_req_context))
        try_i = 1
        while sum(num_tokens_list) >= max_tokens:
            if try_i > max_try:
                raise ValueError(
                    f"""\
Hitting max_try({max_try}) while trying to consolidate context.
Consider changing the parameters "keep_left" and "keep_right",
as well as reducing length of the prompts."""
                )

            left_queue: list = context
            left_tokens_list = num_tokens_list
            right_queue: list = []
            right_tokens_list = []
            """ [1] save messages that are not to be altered"""
            for _ in range(keep_right):
                right_queue.insert(0, left_queue.pop(-1))
                right_tokens_list.insert(0, left_tokens_list.pop(-1))
            """ [2] keep moving messages from left to right until a summary request can be executed """
            while sum(left_tokens_list) + summary_req_n_tokens > max_tokens:
                right_queue.insert(0, left_queue.pop(-1))
                right_tokens_list.insert(0, left_tokens_list.pop(-1))
            """ [3] summarize """
            context = left_queue + summary_req_context
            summarized_content = self.__send_message__(context)
            summarized_context = [{"role": "system", "content": summarized_content}]
            """ [4] putting back context messages from the queues """
            context = left_queue[:keep_left] + summarized_context + right_queue
            num_tokens_list = self.count_context_tokens(context)
            try_i += 1
        return context

    def send_message(
        self,
        *,
        text: str = None,
        context: list = None,
        stream: bool = False,
    ):
        """
        Args:

            text:       query text
            context:    list of dictionaries specifying {"role": "system"/"user"/"assistant", "content": strings}
            stream:     bool

        Yield (if stream) or Return (if not stream):

            content:        str
            status:         bool, stopping signal, currently not implemented
            context:        updated context
            full_content:   str
        """
        if text is None and context is None:
            raise ValueError(f"either 'text' or 'context' needs to be provided")
        if (text is not None) and len(text) > 0:
            _context = self.create_context(text)
            if (context is not None) and isinstance(context, list):
                context += _context
            else:
                context = _context
        if (context is None) or (not isinstance(context, list)):
            raise ValueError(f"unknown context value: {context}")
        context = self.consolidate_context(context, keep_right=1)

        """
        [1] send request、receive text
        """
        if stream:
            content_list = []
            for content, _ in self.__send_message_stream__(context):
                content_list.append(content)
                yield content, False, context, None
            full_content = "".join(content_list)
        else:
            full_content = self.__send_message__(context)

        """
        [2] consolidate context
        """
        context = self.update_context(context, full_content)
        context = self.consolidate_context(context, keep_right=1)

        """
        [3] return 
        """
        content = ""
        status: bool = True
        context: list = context
        full_content: str = full_content
        if stream:
            yield content, status, context, full_content
        else:
            return content, status, context, full_content


class ResearchGPTDebug(ResearchGPT):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.reply_text = """\
1. sample text
    2. sample text
3. sample text
    4. sample text
5. sample text
    6. sample text
7. sample text
    8. sample text
9. sample text
    10. sample text
11. sample text
    12. sample text
```python
print('hello world')
```
```html
<head>
  <link rel="stylesheet" href="prismjs/themes/prism.css" />
  <script src="prismjs/prism.js"></script>
</head>
```"""

    def send_message(
        self,
        *,
        text: str = None,
        context: list = None,
        stream: bool = False,
    ):
        """
        Args:

            text:       query text
            context:    list of dictionaries specifying {"role": "system"/"user"/"assistant", "content": strings}
            stream:     bool

        Yield (if stream) or Return (if not stream):

            content:        str
            status:         bool, stopping signal, currently not implemented
            context:        updated context
            full_content:   str
        """
        reply_text = self.reply_text

        """
        [1] send request、receive text
        """
        full_content = reply_text
        if stream:
            text_ls = reply_text.split("\n")
            for content in text_ls:
                content = "\n" + content
                yield content, False, context, None
                time.sleep(0.5)

        """
        [3] return 
        """
        content = ""
        status: bool = True
        context: list = context
        full_content: str = full_content
        if stream:
            yield content, status, context, full_content
        else:
            return content, status, context, full_content


class ResearchGPTThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        self.uname = "ResearchGPT"
        super().__init__(target=self.main, *args, **kwargs)

    @staticmethod
    def launch_researchgpt():
        # noinspection PyBroadException
        try:
            model = ResearchGPT if not RESEARCHGPT_DEBUG_MODE else ResearchGPTDebug
            researchgpt = model(
                api_key=OPENAI_API_KEY,
                api_org=OPENAI_ORG_ID,
                prompts_dir=PROMPTS_DIR,
                network_err_text=UNKNOWN_NETWORK_ERR_MSG,
            )
            print(f"researchgpt launched")
            print(f"--------------------------\n")
            return researchgpt
        except Exception:
            traceback.print_exc()
            raise ValueError(
                f"{Fore.RED}check env OPENAI_API_KEY and OPENAI_ORG_ID{Style.RESET_ALL}"
            )

    @staticmethod
    def is_asking_for_response(text: str):
        res = re.findall(re.compile(r"@researchgpt", re.IGNORECASE), text)
        return len(res) > 0

    def process_data(self, data: dict):
        # noinspection PyBroadException
        try:
            sender: str = data["sender"]
            text: str = data["message"]
            asking_for_response = self.is_asking_for_response(text=text)
            if asking_for_response:
                text = re.sub(RESEARCHGPT_WAKING_PATTERN, "", text).strip()
        except Exception:
            sender: str = ""
            text: str = ""
            asking_for_response: bool = False
        return sender, text, asking_for_response

    async def alert_empty_input(self, receiver: str):
        response = create_response(
            f"{EMPTY_INPUT_MSG}",
            time_str=f"{time_now_str()}",
            sender=f"{self.uname}",
            receiver=f"{receiver}",
            color=RESEARCHGPT_TEXT_COLOR,
        )

    @staticmethod
    def get_user_context(*, researchgpt, user: str):
        context = USER_CONTEXT_DICT[user] if user in USER_CONTEXT_DICT else None
        if context is None:
            context = [
                {"role": "system", "content": researchgpt.get_prompt("chat-agent.txt")},
                {"role": "system", "content": f"user: {user}"},
            ]
        return context

    async def broadcast_head_lines(self, receiver: str, text: str):
        query_summary_html = f"[Q]\n{text[:17]}...\n\n[A]\n"
        response = create_response(
            query_summary_html,
            time_str=f"{time_now_str()}",
            sender=f"{self.uname}",
            receiver=f"{receiver}",
            color=RESEARCHGPT_TEXT_COLOR,
            complete=False,
        )

    @staticmethod
    def text_to_html(text: str):
        return text

    @staticmethod
    def text_to_prompt(text: str):
        return text

    async def broadcast_stream_body(
        self,
        *,
        researchgpt,
        receiver: str,
        text: str,
        context: List,
        verbose: bool = True,
    ):
        prompt: str = self.text_to_prompt(text)
        full_content: str = ""

        if verbose:
            print(f"[{time_now_str()}] {self.uname} >> {receiver}")
        iterator = researchgpt.send_message(text=prompt, context=context, stream=True)
        for content, status, context, full_content in iterator:
            response = create_response(f"{content}", complete=False)
            if verbose:
                print(content, end="")
            USER_CONTEXT_DICT[receiver] = context
        if verbose:
            print()

        response = create_response(
            f"{self.text_to_html(full_content)}",
            time_str=f"{time_now_str()}",
            sender=f"{self.uname}",
            receiver=f"{receiver}",
            color=RESEARCHGPT_TEXT_COLOR,
            complete=True,
        )

    async def researchgpt_main(self):
        researchgpt = self.launch_researchgpt()
        response = create_response(
            f"{self.uname} {ENTER_ROOM_MSG} ", italic=True, color=RESEARCHGPT_TEXT_COLOR
        )
        # noinspection PyBroadException
        try:
            while True:
                # noinspection PyBroadException
                try:
                    if queue_pop is None:
                        continue

                    """ process input data """
                    data: dict = pickle.loads(queue_pop[1])
                    sender, text, asking_for_response = self.process_data(data)
                    if not asking_for_response:
                        continue
                    if len(text) == 0:
                        await self.alert_empty_input(receiver=sender)
                        continue
                    """ call ResearchGPT API """
                    print(f"[{time_now_str()}] {sender}")
                    print(text)
                    context: List[Dict] = self.get_user_context(
                        researchgpt=researchgpt, user=sender
                    )
                    await self.broadcast_head_lines(receiver=sender, text=text)
                    await self.broadcast_stream_body(
                        researchgpt=researchgpt,
                        receiver=sender,
                        text=text,
                        context=context,
                        verbose=True,
                    )
                    n_tokens_list = researchgpt.count_context_tokens(
                        USER_CONTEXT_DICT[sender]
                    )
                    print(
                        f"[context size]: {n_tokens_list} -> total {sum(n_tokens_list)} tokens"
                    )
                    print()

                except ConnectionError:
                    break
                except ValueError:
                    break
                except KeyboardInterrupt:
                    break
                except Exception:
                    traceback.print_exc()
                    response = create_response(
                        f"{UNKNOWN_RUNTIME_ERR_MSG}",
                        time_str=f"{time_now_str()}",
                        sender=f"{self.uname}",
                        color=f"{RESEARCHGPT_TEXT_COLOR}",
                    )
        except Exception:
            logger.error(f"researchgpt_main error:::\n{traceback.format_exc()}")
        finally:
            pass

    def main(self):
        asyncio.run(self.researchgpt_main())
