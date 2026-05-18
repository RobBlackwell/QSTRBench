GOLEM = ~/git/golem/golem.py

TEMP := $(shell date +%Y%m%d%H%M%S).jsonl

answers.jsonl: ../prompts.jsonl
	$(GOLEM) -v --provider gemini --model "gemini-2.5-pro" --temperature 0.0 --seed 123 --repeat "0:3" -f $< > $(TEMP)
	mv $(TEMP) $@

clean:
	rm *.jsonl
