GOLEM = ~/git/golem/golem.py

TEMP := $(shell date +%Y%m%d%H%M%S).jsonl

answers.jsonl: ../prompts.jsonl
	$(GOLEM) -v --provider openrouter --model "deepseek/deepseek-v3.2" --key "$$OPENROUTER_API_KEY" --temperature 0 --seed 123 --reasoning_effort "high" -f $< > $(TEMP)
	mv $(TEMP) $@

clean:
	rm *.jsonl
