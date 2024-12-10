# openAIRelay

It's a relay between openAI API and local network API. Useful for things like [Home Assistant](https://www.home-assistant.io/).

> You DO NEED an openAI API key (paid).

## `.env` file
No fields are mandatory except for `OPENAI_API_KEY`

```.dotenv
# Defaults to `./config/logging.yaml`
LOGGING_CONFIG=./config/logging.yaml

OPENAI_API_KEY="your-open-api-key"
# If no OPENAI_ASSISTANT_ID is defined then assistant functionality can't be used.
OPENAI_ASSISTANT_ID="your-open-ai-assistant-id"

# Defaults to `./config/system_roles.yaml`
SYSTEM_ROLES=./config/system_roles.yaml
# Defaults to `./config/assistant_instructions.yaml`
ASSISTANT_INSTRUCTIONS=./config/assistant_instructions.yaml
```

## Roles and Assistant settings
You can use your own locations and files for settings as you define them with environment variables.

### Roles
Roles are predefined "personalities" for AI.

They are defined in configuration `.yaml` file, default one is `config/system_roles.yaml`.

### Assistant instructions
Assistant instructions predefined "instructions" on what we use our AI for.

Instructions are defined in configuration `.yaml` file, default one is `config/assistant_instructions.yaml`.

## Run
```shell
fastapi run src/airelay.py --host=0.0.0.0 --port=8088 --reload
```
Documentation accessible at: http://localhost:8088/docs

## Home Assistant

```yaml
# configuration.yaml
rest_command:
    ai_get_reply:
      # Here you can select which system role to use in the bellow case 'default' role is selected (e.g.: '.../default/...')
      url: http://my-ip-or-host:8088/api/v1/roles/default/{{ prompt }}
      # Or define a input_select helper for selecting predefined system roles:
      # url: http://my-ip-or-host:8088/api/v1/roles/{{ states('input_select.ai_system_role' )}}/{{ prompt }}
      verify_ssl: false
      method: POST
    
    ai_get_assistant_reply:
      url: http://192.168.0.201:8088/api/v1/assistants/default/{{ prompt }}
      timeout: 30
      verify_ssl: false
      method: POST

# automations.yaml
actions:
- action: rest_command.ai_get_reply
# or
# - action: rest_command.ai_get_assistant_reply
  data:
    # This is the {{ prompt }} variable from above
    prompt: >-
      In two sentences remind me I need to make cake.
      But I have no idea cake is lie.
  response_variable: ai_response
- if: "{{ ai_response['status'] == 200 }}"
  then:
    - action: notify_somebody_phone
      data:
        title: "Cake is a lie ain't it?"
        message: "{{ ai_response['content']['msg'] }}"
        data:
          ttl: 0
          priority: high
```
