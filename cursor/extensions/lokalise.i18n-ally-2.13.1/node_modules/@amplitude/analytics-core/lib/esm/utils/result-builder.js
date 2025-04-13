import { Status } from '@amplitude/analytics-types';
export var buildResult = function (event, code, message) {
    if (code === void 0) { code = 0; }
    if (message === void 0) { message = Status.Unknown; }
    return { event: event, code: code, message: message };
};
//# sourceMappingURL=result-builder.js.map