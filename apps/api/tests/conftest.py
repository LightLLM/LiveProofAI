"""Pytest fixtures: force stub You + disabled Sanity for tests."""
import os

# Force stub mode and no Sanity so tests don't hit real APIs
os.environ["YOU_STUB"] = "true"
os.environ.pop("SANITY_TOKEN", None)
os.environ.pop("SANITY_PROJECT_ID", None)
