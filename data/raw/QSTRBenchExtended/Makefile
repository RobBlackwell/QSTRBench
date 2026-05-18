JSONT=~/git/jsont/jsont.py

prompts.jsonl: questions.jsonl template.jsont
	$(JSONT) --remove-line-endings template.jsont questions.jsonl > prompts.jsonl

clean:
	rm -f prompts.jsonl
