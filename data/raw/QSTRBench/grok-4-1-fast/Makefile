GOLEM = ~/git/golem/golem.py

TEMP := $(shell date +%Y%m%d%H%M%S).jsonl

answers.jsonl: ../prompts.jsonl
	$(GOLEM) -v --provider openrouter --model "x-ai/grok-4.1-fast" --key "$$OPENROUTER_API_KEY" --repeat "0:3" --temperature 0.0 --seed 123 -f $< > $(TEMP)
	mv $(TEMP) $@

clean:
	rm *.jsonl
