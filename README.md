# openAIRelay
[![test](https://github.com/LeskoIam/openairelay/actions/workflows/test.yml/badge.svg)](https://github.com/LeskoIam/openairelay/actions/workflows/test.yml)
[![ruff](https://github.com/LeskoIam/openairelay/actions/workflows/ruff.yml/badge.svg)](https://github.com/LeskoIam/openairelay/actions/workflows/ruff.yml)

It's a relay between openAI API and local network API. Useful for things like [Home Assistant](https://www.home-assistant.io/).
> You DO NEED an openAI API key (paid).


## Features
### Basic conversations and prompt answering
Using openAI chat completion and predefined roles.

Roles are described in a file (default one is `config/system_roles.yaml`.) in `.yaml` format in the following format:
```yaml
name:
  description: "description"
```
e.g.:
```yaml
Spock:
  description: >-
    You are science officer Spock from Star Trek.

BugsBunny:
  description: >-
    You are Bugs Bunny rabbit from Looney Tunes cartoons.

Rick:
  description: >-
    You are Rick from Rick and Morty show.
```

### Predefined openAI assistant

Using AI Assistant that is already defined.

## Configuration
### `.env` file
No fields are mandatory except for `OPENAI_API_KEY`

```.dotenv
# Defaults to `./config/logging.yaml`
LOGGING_CONFIG=./config/logging.yaml

OPENAI_API_KEY="your-open-api-key"
# If no OPENAI_ASSISTANT_ID is defined then assistant functionality can't be used.
OPENAI_ASSISTANT_ID="your-open-ai-assistant-id"

# Defaults to `./config/system_roles.yaml`
SYSTEM_ROLES=./config/system_roles.yaml
```

## Run
```shell
fastapi run src/airelay.py --host=0.0.0.0 --port=8088
```
### Documentation
Small UI accessible at: http://localhost:8088

API documentation accessible at: http://localhost:8088/docs

### First setup
Head to http://localhost:8088 and check if any Threads show up. If not do the following:
- open http://localhost:8088/docs
- expand `post` `/api/vi/threads`
- click `Try it out` button
- replace data in
  ```json
  {
    "thread_id": "will be replaced",
    "name": "default",
    "description": "Your thread description.",
    "timestamp": "2024-12-12T11:39:47.071Z"
  }
  ```
- click `Execute`
- head to http://localhost:8088 default thread should be visible

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
      # Here you can select which thread to use in the bellow case 'default' role is selected (e.g.: '.../default')
      # Same as with roles you can define some input helper and have thread be dynamic 
      url: http://192.168.0.201:8088/api/v1/assistant/{{ prompt }}/default
      timeout: 60  # It can take some time for the assistant to "think" :)
      verify_ssl: false
      method: POST

# automations.yaml
actions:
- action: rest_command.ai_get_reply
# or
# - action: rest_command.ai_get_assistant_reply
  data:
    # For rest_command.ai_get_assistant_reply you must specify a thread
    #  thread: "default"
    #  This is the {{ prompt }} variable from above
    prompt: >-
      In two sentences remind me I need to make cake.
      But I have no idea cake is a lie.
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
