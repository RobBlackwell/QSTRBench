GOLEM = ~/git/golem/golem.py

TEMP := $(shell date +%Y%m%d%H%M%S).jsonl

answers.jsonl.xz : answers.jsonl
	xz -k answers.jsonl

answers.jsonl: ../prompts.jsonl
	$(GOLEM) -v --provider openai --url "http://127.0.0.1:1976/v1/chat/completions" --model "system" --key "none" -f $< > $(TEMP)
	mv $(TEMP) $@

clean:
	rm *.jsonl
