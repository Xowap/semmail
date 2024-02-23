SRC_PTH:=.venv/lib/python3.*/site-packages/semmail_src.pth

sync: requirements.txt .venv $(SRC_PTH)
	uv pip sync requirements.txt

.venv:
	uv venv

requirements.txt: requirements.in
	uv pip compile requirements.in -o requirements.txt

$(SRC_PTH): .venv
	@if [ ! -f $(SRC_PTH) ]; then \
		PYTHON_VERSION=$$(basename $$(dirname $$(find .venv/lib -type d -name "site-packages"))); \
		echo "$(shell pwd)/src" > .venv/lib/$$PYTHON_VERSION/site-packages/semmail_src.pth; \
		echo "Added src to Python path."; \
	fi

serve:
	.venv/bin/python -m flask --app semmail.app run

format:
	.venv/bin/python -m isort --profile black src tests
	.venv/bin/python -m black src tests
