import reflex as rx

config = rx.Config(
    app_name="reflex_ui",
    tailwind=None,
    plugins=[rx.plugins.TailwindV3Plugin()],
    telemetry_enabled=False,
)
