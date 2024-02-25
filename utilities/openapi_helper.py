"""
This module is useful for OpenAPI interoworking
"""

import json
import random
import requests

class OpenAPIHelper:
    """
    This class abstract OpenAPI operations
    """
################################ INITIALIZATION METHODS ########################################

    def __init__(self, openapi_spec_file):
        self.openapi_json_spec_file = openapi_spec_file
        self.openapi_spec = self._extract_spec()

        self.server_list = [server['url'][0:-1] for server in self.openapi_spec['servers']]
        self.function_dict = self._create_function_dict()

    def _extract_spec(self):
        with open(self.openapi_json_spec_file, 'r', encoding="utf-8") as json_file:
            return json.load(json_file)

    def _create_function_dict(self):
        function_dict = {}

        for path in self.openapi_spec['paths']:
            for http_method in ['get', 'post', 'put', 'delete', 'patch']:
                if http_method in self.openapi_spec['paths'][path]:
                    function_name = self.openapi_spec['paths'][path][http_method]['operationId']

                    function_dict[function_name] = {}
                    function_dict[function_name]['path'] = path
                    function_dict[function_name]['method'] = http_method
                    if 'parameters' in self.openapi_spec['paths'][path][http_method]:
                        function_dict[function_name]['parameters'] = self.openapi_spec['paths'][path][http_method]['parameters']

        return function_dict

################################ PRIVATE METHODS ########################################

    def _parse_path(self, json_path):
        dictionary_output = {}
        dictionary_output['type'] = 'function'
        dictionary_output['function'] = {}
        dictionary_output['function']['name']        = json_path['operationId']
        dictionary_output['function']['description'] = json_path['summary']

        if 'parameters' in json_path:
            dictionary_output['function']['parameters'] = {}
            dictionary_output['function']['parameters']['type'] = 'object'
            dictionary_output['function']['parameters']['properties'] = {}

            formatted_parameters = [ {
                'name':parameter['name'],
                'description': parameter['description'],
                'type': parameter['schema']['type']
                } for parameter in json_path['parameters']  ]

            resulting_dict = {d['name']: {'description': d['description'], 'type':d['type']} for d in formatted_parameters}
            dictionary_output['function']['parameters']['properties'] = resulting_dict

        return dictionary_output

    def _extract_openai_functions(self):
        openai_functions = []
        for path in self.openapi_spec['paths']:
            for http_method in ['get', 'post', 'put', 'delete', 'patch']:
                if http_method in self.openapi_spec['paths'][path]:
                    dict_output = self._parse_path(self.openapi_spec['paths'][path][http_method])
                    openai_functions.append(dict_output)

        return openai_functions

    def _construct_call_fqdns(self, function_data, function_args):
        params = function_data['parameters']
        path   = function_data['path']

        if params is not None:
            params_in_path  = [ param for param in params if param['in'] == "path"]
            params_in_query = [ param for param in params if param['in'] == "query"]

            for param_in_path in params_in_path:
                param_name  = param_in_path['name']
                param_value = str(function_args[param_name])

                path = path.replace(param_name, param_value)

            if len(params_in_query) > 0:
                query_params = [f"{param_in_query['name']}={str(function_args[param_in_query])}" for param_in_query in params_in_query]
                query_params_string = "&".join(query_params)
                path += "?" + query_params_string

            path = path.replace("{", "")
            path = path.replace("}", "")

        fqdns = [server + path for server in self.server_list]

        return fqdns

################################ PUBLIC METHODS ########################################

    def extract_openai_functions_from_spec(self):
        """
            Get a list of functions that can be passed as tools to OpenAI from an OpenAPI Spec
        """
        openai_functions = self._extract_openai_functions()

        return openai_functions

    def call_function(self, function_name, function_args):
        """
            Executes a function
        """
        function_data   = self.function_dict[function_name]
        function_method = function_data['method']

        function_args_dict = json.loads(function_args)

        #GET FQDNs We avoid calling always the first element
        call_fqdns = self._construct_call_fqdns(function_data, function_args_dict)
        random.shuffle(call_fqdns)

        #Call FQDNS until proper response
        for call_fqdn in call_fqdns:
            try:
                if function_method == 'get':
                    req = requests.get(call_fqdn)
                elif function_method == 'post':
                    req = requests.post(call_fqdn, json=function_args_dict)
                else:
                    print(f"ERROR - Method {function_method} not implemented")

                if req.status_code == 200:
                    response = req.text
                    return response
            except Exception:
                continue

        print("ERROR")

        return None
    