.PHONY: test  # to be able to call task test
curr_dir = $(shell pwd)

black:
	docker run --rm -it -v $(curr_dir):/tmp kiwicom/black:20.8b1 black /tmp
