"""Page observability tooling."""
import datetime

class ObservabilityHelper:
    """Abstract logging, metrics and traces."""

    def log_completion(self, completion, user_sid, active_tool,  active_step):
        """Log completion data. Not used here."""
        completion_usage  = completion['usage']
        prompt_tokens     = completion_usage['prompt_tokens']
        completion_tokens = completion_usage['completion_tokens']
        total_tokens      = completion_usage['total_tokens']

        message = f'''
            Logging - for user {user_sid} in tool {active_tool} and step {active_step} {prompt_tokens} prompt tokens, 
            {completion_tokens} completion_tokens, {total_tokens} total_tokens'''

        self.log(message, verbose=True)

    def log(self, message, verbose=False):
        """Log messages."""
        # Time format
        now = datetime.datetime.now()
        milliseconds = now.microsecond // 1000
        timestamp = f"{now.strftime('%Y-%m-%d %H:%M:%S')}.{milliseconds:03d}"
        
        if verbose:
            print(f"LOG - {timestamp} - {message}")
