"""
This module is useful for OpenAPI interoworking
"""
from utilities.observability_helper import ObservabilityHelper

import json
import random
import requests

class OpenAPIHelper:
    """
    This class abstract OpenAPI operations
    """
################################ INITIALIZATION METHODS ########################################
    """
    def __init__(self, openapi_spec_file):
        self.openapi_json_spec_file = openapi_spec_file
        self.openapi_spec = self._extract_spec()

        self.server_list = [server['url'][0:-1] for server in self.openapi_spec['servers']]
        self.function_dict = self._create_function_dict()
    """
    VERBOSE = False

    @staticmethod
    def _extract_spec(openapi_json_spec_file):
        with open(openapi_json_spec_file, 'r', encoding="utf-8") as json_file:
            return json.load(json_file)

    @staticmethod
    def _create_function_dict(openapi_spec):
        function_dict = {}

        for path in openapi_spec['paths']:
            for http_method in ['get', 'post', 'put', 'delete', 'patch']:
                if http_method in openapi_spec['paths'][path]:
                    function_name = openapi_spec['paths'][path][http_method]['operationId']

                    function_dict[function_name] = {}
                    function_dict[function_name]['path'] = path
                    function_dict[function_name]['method'] = http_method
                    if 'parameters' in openapi_spec['paths'][path][http_method]:
                        function_dict[function_name]['parameters'] = openapi_spec['paths'][path][http_method]['parameters']

        return function_dict

################################ PRIVATE METHODS ########################################
    @staticmethod
    def _parse_path(json_path):
        dictionary_output = {}
        dictionary_output['name']        = json_path['operationId']
        dictionary_output['description'] = json_path['summary']

        dictionary_output['parameters'] = {}
        dictionary_output['parameters']['type'] = 'object'
        dictionary_output['parameters']['properties'] = {}
        dictionary_output['parameters']['required'] = []

        if 'parameters' in json_path:
            formatted_parameters = [ {
                'name':parameter['name'],
                'description': parameter['description'],
                'type': parameter['schema']['type']
                } for parameter in json_path['parameters']  ]

            resulting_param_dict = {d['name']: {'description': d['description'], 'type':d['type']} for d in formatted_parameters}
            dictionary_output['parameters']['properties'] = resulting_param_dict

            required_parameters = [ parameter['name'] for parameter in json_path['parameters'] if parameter['required'] == True]
            dictionary_output['parameters']['required'] = required_parameters

        return dictionary_output
    
    @staticmethod
    def _extract_openai_functions(openapi_spec):
        openai_functions = []
        for path in openapi_spec['paths']:
            #POST METHODS REQUIRE A DIFFERENT STRUCTURE. TBD
            #supported_http_methods = ['get', 'post', 'put', 'delete', 'patch']
            supported_http_methods = ['get']
            for http_method in supported_http_methods:
                if http_method in openapi_spec['paths'][path]:
                    dict_output = OpenAPIHelper._parse_path(openapi_spec['paths'][path][http_method])
                    openai_functions.append(dict_output)

        return openai_functions

    @staticmethod
    def _construct_call_fqdns(function_data, function_args, server_list):
        params = function_data.get('parameters', None)
        path   = function_data['path']

        if params is not None:
            params_in_path  = [ param for param in params if param['in'] == "path"]
            params_in_query = [ param for param in params if param['in'] == "query"]

            for param_in_path in params_in_path:
                param_name  = param_in_path['name']
                param_value = str(function_args[param_name])

                path = path.replace(param_name, param_value)

            if len(params_in_query) > 0:
                query_params = [f"{param_in_query['name']}={str(function_args[param_in_query['name']])}" for param_in_query in params_in_query]
                query_params_string = "&".join(query_params)
                path += "?" + query_params_string

            path = path.replace("{", "")
            path = path.replace("}", "")

        fqdns = [server['url'][0:-1] + path for server in server_list]

        return fqdns

################################ PUBLIC METHODS ########################################
    @staticmethod
    def validate_spec_json(new_spec_body):
        try:
            new_spec_json = json.loads(new_spec_body) 
            if ('info'   in new_spec_json and
               'paths'   in new_spec_json and 
               'servers' in new_spec_json):
                return True
            else:
                return False
        except json.JSONDecodeError:
            return False

    @staticmethod
    def extract_openai_functions_from_spec(openapi_spec):
        """
            Get a list of functions that can be passed as tools to OpenAI from an OpenAPI Spec
        """
        openapi_spec_json = json.loads(openapi_spec) 
        openai_functions = OpenAPIHelper._extract_openai_functions(openapi_spec_json)

        return openai_functions

    @staticmethod
    def call_function(function_name, function_args, openapi_spec):
        """
            Executes a function
        """
        function_dict   = OpenAPIHelper._create_function_dict(openapi_spec)
        function_data   = function_dict[function_name]
        function_method = function_data['method']

        function_args_dict = json.loads(function_args)

        #GET FQDNs We avoid calling always the first element
        call_fqdns = OpenAPIHelper._construct_call_fqdns(function_data, function_args_dict, openapi_spec['servers'])
        random.shuffle(call_fqdns)

        #Call FQDNS until proper response
        for call_fqdn in call_fqdns:
            try:
                if function_method == 'get':
                    req = requests.get(call_fqdn)
                elif function_method == 'post':
                    req = requests.post(call_fqdn, json=function_args_dict)
                else:
                    ObservabilityHelper.log(f"ERROR - Method {function_method} not implemented", OpenAPIHelper.VERBOSE)

                if req.status_code == 200:
                    response = req.text
                    return response
            except Exception:
                continue

        ObservabilityHelper.log("ERROR - No successful response from functions", OpenAPIHelper.VERBOSE)

        return "No response from function call"
    