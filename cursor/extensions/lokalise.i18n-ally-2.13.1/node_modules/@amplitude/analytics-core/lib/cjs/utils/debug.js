Object.defineProperty(exports, "__esModule", { value: true });
exports.debugWrapper = exports.getClientStates = exports.getValueByStringPath = exports.getClientLogConfig = exports.getStacktrace = void 0;
var tslib_1 = require("tslib");
/* eslint-disable @typescript-eslint/no-unsafe-assignment */
/* eslint-disable @typescript-eslint/no-unsafe-member-access */
/* eslint-disable @typescript-eslint/no-unsafe-call */
/* eslint-disable @typescript-eslint/no-non-null-assertion */
var analytics_types_1 = require("@amplitude/analytics-types");
var getStacktrace = function (ignoreDepth) {
    if (ignoreDepth === void 0) { ignoreDepth = 0; }
    var trace = new Error().stack || '';
    return trace
        .split('\n')
        .slice(2 + ignoreDepth)
        .map(function (text) { return text.trim(); });
};
exports.getStacktrace = getStacktrace;
// This hook makes sure we always get the latest logger and logLevel.
var getClientLogConfig = function (client) { return function () {
    var _a = tslib_1.__assign({}, client.config), logger = _a.loggerProvider, logLevel = _a.logLevel;
    return {
        logger: logger,
        logLevel: logLevel,
    };
}; };
exports.getClientLogConfig = getClientLogConfig;
// This is a convenient function to get the attribute from object with string path, similar to lodash '#get'.
var getValueByStringPath = function (obj, path) {
    var e_1, _a;
    path = path.replace(/\[(\w+)\]/g, '.$1'); // convert indexes to properties
    path = path.replace(/^\./, ''); // strip a leading dot
    try {
        for (var _b = tslib_1.__values(path.split('.')), _c = _b.next(); !_c.done; _c = _b.next()) {
            var attr = _c.value;
            if (attr in obj) {
                obj = obj[attr];
            }
            else {
                return;
            }
        }
    }
    catch (e_1_1) { e_1 = { error: e_1_1 }; }
    finally {
        try {
            if (_c && !_c.done && (_a = _b.return)) _a.call(_b);
        }
        finally { if (e_1) throw e_1.error; }
    }
    return obj;
};
exports.getValueByStringPath = getValueByStringPath;
var getClientStates = function (client, paths) { return function () {
    var e_2, _a;
    var res = {};
    try {
        for (var paths_1 = tslib_1.__values(paths), paths_1_1 = paths_1.next(); !paths_1_1.done; paths_1_1 = paths_1.next()) {
            var path = paths_1_1.value;
            res[path] = (0, exports.getValueByStringPath)(client, path);
        }
    }
    catch (e_2_1) { e_2 = { error: e_2_1 }; }
    finally {
        try {
            if (paths_1_1 && !paths_1_1.done && (_a = paths_1.return)) _a.call(paths_1);
        }
        finally { if (e_2) throw e_2.error; }
    }
    return res;
}; };
exports.getClientStates = getClientStates;
var debugWrapper = function (fn, fnName, getLogConfig, getStates, fnContext) {
    if (fnContext === void 0) { fnContext = null; }
    return function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        var _a = getLogConfig(), logger = _a.logger, logLevel = _a.logLevel;
        // return early if possible to reduce overhead
        if ((logLevel && logLevel < analytics_types_1.LogLevel.Debug) || !logLevel || !logger) {
            return fn.apply(fnContext, args);
        }
        var debugContext = {
            type: 'invoke public method',
            name: fnName,
            args: args,
            stacktrace: (0, exports.getStacktrace)(1),
            time: {
                start: new Date().toISOString(),
            },
            states: {},
        };
        if (getStates && debugContext.states) {
            debugContext.states.before = getStates();
        }
        var result = fn.apply(fnContext, args);
        if (result && result.promise) {
            // if result is a promise, add the callback
            result.promise.then(function () {
                if (getStates && debugContext.states) {
                    debugContext.states.after = getStates();
                }
                if (debugContext.time) {
                    debugContext.time.end = new Date().toISOString();
                }
                logger.debug(JSON.stringify(debugContext, null, 2));
            });
        }
        else {
            if (getStates && debugContext.states) {
                debugContext.states.after = getStates();
            }
            if (debugContext.time) {
                debugContext.time.end = new Date().toISOString();
            }
            logger.debug(JSON.stringify(debugContext, null, 2));
        }
        return result;
    };
};
exports.debugWrapper = debugWrapper;
//# sourceMappingURL=debug.js.map