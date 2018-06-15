const winston = require('winston');
const customColors = {
	error: 'red',
	warn: 'yellow',
	info: 'cyan',
	debug: 'green'
};
const logFormat = winston.format.printf(info => {
	return `${info.timestamp} [${info.level}] ${info.message}`;
});

winston.addColors(customColors);

let logger = winston.createLogger({
		transports: [
			new winston.transports.Console({
				level: 'debug',
				format: winston.format.combine(
					winston.format.colorize({all:true}),
					winston.format.simple(),
					winston.format.timestamp(),
					logFormat
				)
			})
		]
});

module.exports = logger;