const _ = require('ramda');
const Maybe = require('data.maybe');
const config = require('./config');

const verifyImportChange = _.compose(
	_.not,
	_.apply(_.equals),
	_.map(
		_.compose(
			x => x.getOrElse(null),
			_.map(
				_.compose(
					_.filter(_.test(/\bimport\s|\brequire\(/)),
					_.addIndex(_.map)((v, i) => v + i),
					_.split('\n'),
					_.prop('file_string')
				)
			),
			Maybe.fromNullable
		)
	)
);

const parseKb = _.curry(function(toDecimalPlace, v) {
	return (
		config.toDecimalPlace ? (v / 1000).toFixed(1) : Math.round(v / 1000)
	) + 'kB';
});

const parseHtml = _.curry(function(config, parseKb, data) {
	let text = parseKb(data.size);
	if (config.showGzip) text += `, gzip ${parseKb(data.gzip)}`;
	const styles = `style="color: ${config.textColour}; padding-left: 15px;"`;
	
	return {
		line: data.line,
		html: `<span ${styles}>${text}</span>`
	};
});

const parsePackagesData = _.compose(
	_.map(parseHtml(config, parseKb(config.toDecimalPlace))),
	_.filter(v => v.size !== 0)
);

module.exports = { verifyImportChange, parsePackagesData }