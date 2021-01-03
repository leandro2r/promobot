SVC=promobot
NAMESPACE=$(SVC)
IMG=leandro2r/$(SVC)
VERSION=`cat setup.py | grep -i version | sed -E "s|\s+version='([^']+)',|\1|g"`

clean:
	@echo -e "Cleaning files..."
	@rm -rf *.egg-info build dist

config:
	@echo -e "Configuring on kubernetes..."
	@kubectl apply -f extras/k3s

install: config
	@echo -e "Installing files..."
	@cp -f extras/logrotate/pods /etc/logrotate.d/

build:
	@echo -e "Building docker image..."
	@docker build -t $(IMG):$(VERSION) . --squash
	@docker system prune -f

release:
	@echo -e "Pushing docker images..."
	@docker tag  $(IMG):$(VERSION) $(IMG):latest
	@docker push $(IMG):$(VERSION)
	@docker push $(IMG):latest

deploy: config
	@echo -e "Deploying on kubernetes..."
	@kubectl set image deploy/$(SVC) -n $(NAMESPACE) *=$(IMG):latest --all

all: clean build release deploy
	@echo -e "Done!"
