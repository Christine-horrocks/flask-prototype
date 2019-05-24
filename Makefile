NODE_SASS=./node_modules/.bin/node-sass

compile:
	$(NODE_SASS) ./node_modules/govuk-frontend/all.scss  ./application/static/style.css