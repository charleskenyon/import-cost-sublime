const _ = require('ramda');
const config = require('./config');

const convertKb = _.curry(function(toDecimalPlace, v) {
	return (
		toDecimalPlace ? (v / 1000).toFixed(1) : Math.round(v / 1000)
	) + 'kB';
})(config.toDecimalPlace);

const formatHtml = _.curry(function(config, data) {
	const text = `${data.size}${config.showGzip ? `, ${data.gzip}` : ''}`;
	const style = `style="color: ${config.textColour}; padding-left: 15px;"`;
	const html = `<span ${style}>${text}</span>`;
	return { html, line: data.line };
});

const formatPayload = _.compose(
	_.map(
		_.compose(
			formatHtml(config),
			_.evolve({ gzip: convertKb, size: convertKb })
		)
	),
	_.filter(v => v.size !== 0)
);

module.exports = formatPayload;