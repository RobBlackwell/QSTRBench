GOLEM = ~/git/golem/golem.py

TEMP := $(shell date +%Y%m%d%H%M%S).jsonl

answers.jsonl: ../prompts.jsonl
	$(GOLEM) -v --provider openrouter --model "meta-llama/llama-3.3-70b-instruct" --key "$$OPENROUTER_API_KEY" --temperature 0.0 --seed 123 -f $< > $(TEMP)
	mv $(TEMP) $@

clean:
	rm *.jsonl
