build:
	docker build . -t 10.131.0.2:5000/e2e-mate:latest --push

publish:
	kubectl -n jialei delete statefulsets.apps e2e-mate
	kubectl -n jialei apply -f e2e-mate.yaml
