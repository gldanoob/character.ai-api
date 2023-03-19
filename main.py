import json

import aiohttp


class API():
    """
        This class is used to interact with the Character.ai API
        Call the setup method to get the history, token and ids
        Call the prompt method to get a response from the API
    """
    def __init__(self, character: str, token: str, cookies: str) -> None:
        self.character = character 
        self.internal_id = '', 
        self.external_id = '',
        self.token = token 
        self.cookies = cookies 

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': f'https://beta.character.ai/chat?char={self.character}',
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json',
            'Origin': 'https://beta.character.ai',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Cookie': self.cookies,
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }

    async def setup(self):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            # Get the history external id
            async with session.post('https://beta.character.ai/chat/history/continue/', json={
                'character_external_id': self.character,
                'history_external_id': None,
            }) as response:
                res_json = await response.json()
                self.external_id = res_json['external_id']
                self.internal_id = (user['user']['username'] for user in res_json['participants'] if user['user']['username'].startswith('internal_id')).__next__()

            # Get the history
            async with session.get('https://beta.character.ai/chat/history/msgs/user/', params={'history_external_id': self.external_id}) as response:
                res_json = await response.json()
                hist = ", ".join( 
                        f"{msg['src__name']}: {msg['text']}"
                        for msg in res_json['messages']
                    )
                return 'History: ' + hist

    async def prompt(self, msg: str):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post('https://beta.character.ai/chat/streaming/', json={
                    'history_external_id': self.external_id,
                    'character_external_id': self.character, 
                    'text': msg,
                    'tgt': self.internal_id,
                    'ranking_method': 'random',
                    'staging': False,
                    'model_server_address': None,
                    'model_server_address_exp_chars': None,
                    'override_prefix': None,
                    'override_rank': None,
                    'rank_candidates': None,
                    'filter_candidates': None,
                    'unsanitized_characters': None,
                    'prefix_limit': None,
                    'prefix_token_limit': None,
                    'stream_params': None,
                    'enable_tti': None,
                    'initial_timeout': None,
                    'insert_beginning': None,
                    'stream_every_n_steps': 16,
                    'chunks_to_pad': 8,
                    'is_proactive': False,
                    'image_rel_path': '',
                    'image_description': '',
                    'image_description_type': '',
                    'image_origin_type': '',
                    'voice_enabled': False,
                    'parent_msg_uuid': None,
                    'seen_msg_uuids': [],
                    'retry_last_user_msg_uuid': None,
                    'num_candidates': 1,
                    'give_room_introductions': True,
            }) as response:
                res_text = await response.text()
                lines = res_text.splitlines()
                try:
                    res_json = json.loads(lines[-2])
                    return res_json['replies'][0]['text']
                except IndexError:
                    return res_text