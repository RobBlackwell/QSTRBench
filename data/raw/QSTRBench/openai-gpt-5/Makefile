GOLEM = ~/git/golem/golem.py

TEMP := $(shell date +%Y%m%d%H%M%S).jsonl

answers.jsonl: ../prompts.jsonl
	$(GOLEM) -v --provider openai --model gpt-5 --repeat "0:3"  -f $< > $(TEMP)
	mv $(TEMP) $@

clean:
	rm *.jsonl
