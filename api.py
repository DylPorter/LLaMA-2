import asyncio
import html
import json
import sys
import websockets

host = 'localhost:5005'
url = f'ws://{host}/api/v1/chat-stream'

history = {'internal': [], 'visible': []}

async def run(user_input, history):
    request = {
        'user_input': user_input,
        'history': history,
        'mode': 'chat',  # Valid options: 'chat', 'chat-instruct', 'instruct'
        'character': 'None',
        'instruction_template': 'Vicuna-v1.1',
        'your_name': 'Human',

        'regenerate': False,
        '_continue': False,
        'stop_at_newline': False,
        'chat_prompt_size': 2048,
        'chat_generation_attempts': 1,
        'chat_instruct_command': 'Continue the chat dialogue below. Write a single reply for the character "Assistant"\n\n',

        'max_new_tokens': 200,
        'do_sample': True,
        'temperature': 0.7,
        'top_p': 0.9,
        'typical_p': 1,
        'epsilon_cutoff': 0,
        'eta_cutoff': 0,
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1.15,
        'top_k': 20,
        'min_length': 0,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 1,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,
        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 2048,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': ['\n### Assistant:', '\n### Human:']
    }

    async with websockets.connect(url, ping_interval=None) as websocket:
        await websocket.send(json.dumps(request))

        while True:
            incoming_data = await websocket.recv()
            incoming_data = json.loads(incoming_data)

            match incoming_data['event']:
                case 'text_stream':
                    yield incoming_data['history']
                case 'stream_end':
                    return

async def print_response_stream(user_input, history):
    cur_len = 0
    async for new_history in run(user_input, history):
        cur_message = new_history['visible'][-1][1][cur_len:]
        cur_len += len(cur_message)
        print(html.unescape(cur_message), end='')
        sys.stdout.flush()
        history['internal'][-1][1] = new_history['visible'][-1][1]
        history['visible'][-1][1] = new_history['visible'][-1][1]

while (prompt := input("\n[\"q\" to quit] >>> ")) != "q":
    history['internal'].append([prompt, ''])
    history['visible'].append([prompt, ''])
    asyncio.run(print_response_stream(prompt, history))
