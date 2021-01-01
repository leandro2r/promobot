SVC=promobot
IMG=leandro2r/$(SVC)
VERSION=`cat setup.py | grep -i version | sed -E "s|\s+version='([^']+)',|\1|g"`

install:
	@kubectl apply -f extras/k3s
	@cp -f extras/logrotate/pods /etc/logrotate.d/

clean:
	@echo -e "Cleaning files"
	@rm -rf *.egg-info build dist

build:
	@echo -e "Building docker image"
	@docker build -t $(IMG):$(VERSION) . --squash
	@docker system prune -f

release:
	@echo -e "Pushing docker images"
	@docker tag  $(IMG):$(VERSION) $(IMG):latest
	@docker push $(IMG):$(VERSION)
	@docker push $(IMG):latest

deploy:
	@echo -e "Restarting pods"
	@kubectl scale --replicas=0 deploy $(SVC) -n $(SVC)
	@kubectl scale --replicas=1 deploy $(SVC) -n $(SVC)

all: clean build release deploy
	@echo -e "Done!"
