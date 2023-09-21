install-deps:
	pip install -r tools/requirements.txt
run-auth-check: install-deps
	@# bgt_inrichtingselementen is known to fail due to
	@# a flaw in the mappyfile mapfile grammar
	@# addresseerbare_objecten fails because the mappyfile mapfile grammar
	@# does not support the BINDVALS directive
	./tools/auth_check.py -e bgt_inrichtingselementen adresseerbare_objecten
