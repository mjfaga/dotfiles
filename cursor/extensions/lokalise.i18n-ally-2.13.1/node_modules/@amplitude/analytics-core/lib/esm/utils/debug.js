import { __assign, __values } from "tslib";
/* eslint-disable @typescript-eslint/no-unsafe-assignment */
/* eslint-disable @typescript-eslint/no-unsafe-member-access */
/* eslint-disable @typescript-eslint/no-unsafe-call */
/* eslint-disable @typescript-eslint/no-non-null-assertion */
import { LogLevel } from '@amplitude/analytics-types';
export var getStacktrace = function (ignoreDepth) {
    if (ignoreDepth === void 0) { ignoreDepth = 0; }
    var trace = new Error().stack || '';
    return trace
        .split('\n')
        .slice(2 + ignoreDepth)
        .map(function (text) { return text.trim(); });
};
// This hook makes sure we always get the latest logger and logLevel.
export var getClientLogConfig = function (client) { return function () {
    var _a = __assign({}, client.config), logger = _a.loggerProvider, logLevel = _a.logLevel;
    return {
        logger: logger,
        logLevel: logLevel,
    };
}; };
// This is a convenient function to get the attribute from object with string path, similar to lodash '#get'.
export var getValueByStringPath = function (obj, path) {
    var e_1, _a;
    path = path.replace(/\[(\w+)\]/g, '.$1'); // convert indexes to properties
    path = path.replace(/^\./, ''); // strip a leading dot
    try {
        for (var _b = __values(path.split('.')), _c = _b.next(); !_c.done; _c = _b.next()) {
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
export var getClientStates = function (client, paths) { return function () {
    var e_2, _a;
    var res = {};
    try {
        for (var paths_1 = __values(paths), paths_1_1 = paths_1.next(); !paths_1_1.done; paths_1_1 = paths_1.next()) {
            var path = paths_1_1.value;
            res[path] = getValueByStringPath(client, path);
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
export var debugWrapper = function (fn, fnName, getLogConfig, getStates, fnContext) {
    if (fnContext === void 0) { fnContext = null; }
    return function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        var _a = getLogConfig(), logger = _a.logger, logLevel = _a.logLevel;
        // return early if possible to reduce overhead
        if ((logLevel && logLevel < LogLevel.Debug) || !logLevel || !logger) {
            return fn.apply(fnContext, args);
        }
        var debugContext = {
            type: 'invoke public method',
            name: fnName,
            args: args,
            stacktrace: getStacktrace(1),
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
//# sourceMappingURL=debug.js.map