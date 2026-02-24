import os
import json

def validate_action(intent_json, policy_path="armor/policy.json"):
    # Load Policy
    with open(policy_path, 'r') as f:
        policy = json.load(f)

    target = os.path.abspath(intent_json['intent']['target_resource'])
    command = intent_json['intent']['proposed_command']

    # 1. Scope Check: Must be in allowed workspace
    is_in_allowed = any(target.startswith(os.path.abspath(path)) for path in policy['allowed_scopes'])
    # 2. Safety Check: Must NOT be in blocked workspace
    is_in_blocked = any(target.startswith(os.path.abspath(path)) for path in policy['blocked_scopes'])
    # 3. Command Check: Check for forbidden strings
    is_command_safe = not any(forbidden in command for forbidden in policy['restricted_commands'])

    if is_in_allowed and not is_in_blocked and is_command_safe:
        return True, "ACTION_APPROVED: Intent aligns with defined safety policy."
    else:
        reason = "Out of scope" if not is_in_allowed else "Accessing restricted directory" if is_in_blocked else "Forbidden command"
        return False, f"ACTION_BLOCKED: Policy Violation - {reason}."

# For the demo: Test the gatekeeper
if __name__ == "__main__":
    test_intent = {
        "intent": {
            "target_resource": "C:/Users/lenovo/Desktop/claw/project/workspace/app.py",
            "proposed_command": "write app.py"
        }
    }
    status, msg = validate_action(test_intent)
    print(f"Status: {status} | Message: {msg}")