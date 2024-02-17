
class ObservabilityHelper:
        
    def log_completion(self, completion, user_sid, active_tool,  active_step):
        completion_usage  = completion['usage']
        prompt_tokens     = completion_usage['prompt_tokens']
        completion_tokens = completion_usage['completion_tokens']
        total_tokens      = completion_usage['total_tokens']

        message = f"Logging - for user {user_sid} in tool {active_tool} and step {active_step} {prompt_tokens} prompt tokens, {completion_tokens} completion_tokens, {total_tokens} total_tokens"

        self.log_message(message, verbose=True)


    def log_message(self, message, verbose=False):
        if verbose:
            print(f"LOG - {message}")