"""Exercise the HTTP handler without starting the GUI or sending real input."""
import ast
import http.server
import io
import json
from pathlib import Path
import secrets
import threading
import time
import unittest
from urllib.parse import parse_qs, urlparse

SOURCE = Path(__file__).resolve().parents[1] / 'SlideRemote.pyw'
tree = ast.parse(SOURCE.read_text())
names = {'State', 'Handler', 'device_name'}
module = ast.Module(body=[n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name in names], type_ignores=[])
namespace = dict(secrets=secrets, threading=threading, time=time, http=http,
                 urlparse=urlparse, parse_qs=parse_qs, json=json, PAGE='remote')
exec(compile(module, str(SOURCE), 'exec'), namespace)


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.state = namespace['STATE'] = namespace['State']()
        self.actions = []
        namespace['ACTIONS'] = {'next': (lambda: self.actions.append('next'), 'Next slide')}
        namespace['pyautogui'] = type('Input', (), {'moveRel': lambda _, x, y: self.actions.append((x, y))})()

    def request(self, data=None, raw=None, headers=None):
        body = json.dumps(data).encode() if raw is None else raw
        handler = object.__new__(namespace['Handler'])
        handler.path = '/a'
        handler.headers = {'Content-Length': str(len(body)), **(headers or {})}
        handler.rfile = io.BytesIO(body)
        replies = []
        handler._reply = lambda code, *args: replies.append(code)
        handler.do_POST()
        return replies[-1]

    def test_authenticated_action_and_rejected_tokens(self):
        self.assertEqual(self.request({'t': self.state.token, 'a': 'next'}), 204)
        self.assertEqual(self.actions, ['next'])
        for token in ('wrong', 'é', None, [], {}):
            self.assertEqual(self.request({'t': token, 'a': 'next'}), 403)
        old = self.state.token
        self.state.token = secrets.token_urlsafe(32)
        self.assertEqual(self.request({'t': old, 'a': 'next'}), 403)
        self.assertEqual(self.actions, ['next'])

    def test_request_bounds_and_invalid_json(self):
        for length in ('-1', '0', 'bad'):
            self.assertEqual(self.request(raw=b'{}', headers={'Content-Length': length}), 400)
        self.assertEqual(self.request(raw=b'x' * 4097), 413)
        self.assertEqual(self.request(raw=b'{'), 400)
        self.assertEqual(self.request(raw=b'\xff'), 400)
        self.assertEqual(self.request(raw=b'{}', headers={'Content-Length': '10'}), 400)
        self.assertEqual(self.request(raw=b'{}', headers={'Transfer-Encoding': 'chunked'}), 400)

    def test_malformed_commands_and_pointer_bounds(self):
        for fields in ({'a': []}, {'a': {}}, {'a': 'unknown'}, {'dx': 1}, {'dx': None, 'dy': 0}, {'dx': float('inf'), 'dy': 0}):
            self.assertEqual(self.request({'t': self.state.token, **fields}), 400)
        self.assertEqual(self.actions, [])
        self.assertEqual(self.request({'t': self.state.token, 'dx': 900, 'dy': -900}), 204)
        self.assertEqual(self.actions, [(400, -400)])

    def test_get_requires_current_token(self):
        handler = object.__new__(namespace['Handler'])
        replies = []
        handler._reply = lambda code, *args: replies.append(code)
        for path, expected in (('/', 403), ('/?t=wrong', 403), ('/?t=%C3%A9', 403), ('/?t=' + self.state.token, 200), ('/missing', 404)):
            handler.path = path
            handler.do_GET()
            self.assertEqual(replies[-1], expected)


if __name__ == '__main__':
    unittest.main()
