# Rebuild the pre-built Tailwind stylesheet (static/css/site.css) after adding Tailwind classes to templates.
# Needs the standalone Tailwind CLI v3.4.17 on PATH as `tailwindcss`:
#   https://github.com/tailwindlabs/tailwindcss/releases/tag/v3.4.17  (tailwindcss-macos-arm64 → chmod +x)
TAILWIND ?= tailwindcss

css:
	$(TAILWIND) -c tailwind.config.js -i static/css/tailwind.src.css -o static/css/site.css --minify

.PHONY: css
