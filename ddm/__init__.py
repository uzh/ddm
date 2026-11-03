from importlib.metadata import PackageNotFoundError, version

try:
    VERSION = version("django-ddm")
except PackageNotFoundError:
    # Package is not installed (e.g. running from an unbuilt source checkout).
    VERSION = "0.0.0.dev0"
