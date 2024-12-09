# openAIRelay

It's a relay between openAI API and local network API. Useful for things like [Home Assistant](https://www.home-assistant.io/).

> You DO NEED an openAI API key (paid).

## `.env` file
No fields are mandatory except for `OPENAI_API_KEY`

```.dotenv
OPENAI_API_KEY="your-open-api-key"

# Defaults to ./airelay/settings/system_roles.yaml
SYSTEM_ROLES=./airelay/settings/system_roles.yaml
# Defaults to ./logging.yaml
LOGGING_CONFIG=./logging.yaml
```

## Run
```shell
fastapi run src/airelay.py --host=0.0.0.0 --port=8088 --reload
```
Accessible at: http://localhost:8088/docs

## Home Assistant

```yaml
# configuration.yaml
rest_command:
    ai_get_reply:
    # Here you can select which system role to use in the bellow case 'default' role is selected (e.g.: '.../default/...')
    url: http://my-ip-or-host:8088/api/v1/roles/predefined/default/{{ prompt }}
    # Or define a select or text input for selecting predefined system roles:
    # url: http://my-ip-or-host:8088/api/v1/roles/predefined/{{ 'default' if states('input_text.ai_default_system_role') | length == 0 else states('input_text.ai_default_system_role')}}/{{ prompt }}
    verify_ssl: false
    method: POST

# automations.yaml
actions:
- action: rest_command.ai_get_reply
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
