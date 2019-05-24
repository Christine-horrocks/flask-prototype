NODE_SASS=./node_modules/.bin/node-sass

compile:
	$(NODE_SASS) ./node_modules/govuk-frontend/src/all.scss -o ./application/static/style.css