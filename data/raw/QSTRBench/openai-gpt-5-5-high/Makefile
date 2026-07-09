GOLEM = ~/git/golem/golem.py

TEMP := $(shell date +%Y%m%d%H%M%S).jsonl

answers.jsonl.xz : answers.jsonl
	xz -k answers.jsonl

answers.jsonl: ../prompts.jsonl
	$(GOLEM) -v --provider openrouter --model openai/gpt-5.5 --reasoning_effort "high" -f $< > $(TEMP)
	mv $(TEMP) $@

clean:
	rm *.jsonl
