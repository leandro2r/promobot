SVC=promobot
NAMESPACE=$(SVC)
IMG=leandro2r/$(SVC)
VERSION=`cat setup.py | grep -i version | sed -E "s|\s+version='([^']+)',|\1|g"`

clean:
	@echo "Cleaning files..."
	@rm -rf *.egg-info build dist

install: deploy
	@echo "Installing files..."
	@cp -f extras/logrotate/pods /etc/logrotate.d/

update:
	@echo "Updating pods..."
	@kubectl scale --replicas=0 deploy $(SVC) -n $(NAMESPACE)
	@kubectl scale --replicas=1 deploy $(SVC) -n $(NAMESPACE)

build:
	@echo "Building docker image..."
	@docker build -t $(IMG):$(VERSION) . --squash
	@docker system prune -f

release:
	@echo "Pushing docker images..."
	@docker tag  $(IMG):$(VERSION) $(IMG):latest
	@docker push $(IMG):$(VERSION)
	@docker push $(IMG):latest

deploy:
	@echo "Deploying on kubernetes..."
	@kubectl apply -f .kube/deployment.yml -f .kube/db-deployment.yml -f .kube/rbac-role.yml

all: clean build release deploy
	@echo "Done!"
