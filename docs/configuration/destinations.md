# Destinations

## Console
```yaml
checks:
  - console_destination:
      source:
        type: reminder
      destinations:
        - type: console
          template: "Hello Console!"
      period: 30s
```

Console will simply print the rendered template to the console.


## Discord
```yaml
checks:
  - discord_destination:
      source:
        type: reminder
      destinations:
        - type: discord
          webhookURL: ${PYREMINDER_DISCORD_WEBHOOK_URL}
          color: 1ABC9C
          template: "Hello Discord!"
      period: 30s
```

Discord will send the rendered template as an embed in a discord message. Optionally, a color for the embed can be supplied.

