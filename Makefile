# var
MODULE = $(notdir $(CURDIR))
PEPS   = E26,E302,E305,E401,E402,E701,E702

# dir
CWD   = $(CURDIR)
TMP   = $(CWD)/tmp

# tool
CURL   = curl -L -o
CF     = clang-format
PY     = python3
PIP    = pip3
PEP    = autopep8

# src
Y  += $(MODULE).py
F  += lib/$(MODULE).ini
S  += $(Y) $(F)

lic: LICENSE
LICENSE:
	wget -c https://github.com/ponyatov/Fx/raw/dev/LICENSE
# all
.PHONY: all
all: $(Y) $(F)
	$(PY) $^

# format
.PHONY: format
format: tmp/format_py

tmp/format_py: $(Y)
	$(PEP) --ignore $(PEPS) -i $? && touch $@

# dox
.PHONY: doxy
doxy: doxy.gen
	rm -rf docs ; doxygen $< 1>/dev/null

# install
.PHONY: install update updev
install update:
	sudo apt update
	sudo apt install -yu `cat apt.txt`
	pip3 install --user -U pip autopep8 pytest
	pip3 install --user -U -r requirements.txt
