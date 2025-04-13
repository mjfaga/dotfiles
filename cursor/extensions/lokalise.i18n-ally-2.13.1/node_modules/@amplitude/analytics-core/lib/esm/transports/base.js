/* eslint-disable @typescript-eslint/no-unsafe-argument */
/* eslint-disable @typescript-eslint/no-unsafe-assignment */
/* eslint-disable @typescript-eslint/no-unsafe-call */
import { Status } from '@amplitude/analytics-types';
var BaseTransport = /** @class */ (function () {
    function BaseTransport() {
    }
    BaseTransport.prototype.send = function (_serverUrl, _payload) {
        return Promise.resolve(null);
    };
    BaseTransport.prototype.buildResponse = function (responseJSON) {
        var _a, _b, _c, _d, _e, _f, _g, _h, _j, _k, _l, _m, _o, _p, _q, _r, _s, _t, _u, _v, _w, _x;
        if (typeof responseJSON !== 'object') {
            return null;
        }
        var statusCode = responseJSON.code || 0;
        var status = this.buildStatus(statusCode);
        switch (status) {
            case Status.Success:
                return {
                    status: status,
                    statusCode: statusCode,
                    body: {
                        eventsIngested: (_a = responseJSON.events_ingested) !== null && _a !== void 0 ? _a : 0,
                        payloadSizeBytes: (_b = responseJSON.payload_size_bytes) !== null && _b !== void 0 ? _b : 0,
                        serverUploadTime: (_c = responseJSON.server_upload_time) !== null && _c !== void 0 ? _c : 0,
                    },
                };
            case Status.Invalid:
                return {
                    status: status,
                    statusCode: statusCode,
                    body: {
                        error: (_d = responseJSON.error) !== null && _d !== void 0 ? _d : '',
                        missingField: (_e = responseJSON.missing_field) !== null && _e !== void 0 ? _e : '',
                        eventsWithInvalidFields: (_f = responseJSON.events_with_invalid_fields) !== null && _f !== void 0 ? _f : {},
                        eventsWithMissingFields: (_g = responseJSON.events_with_missing_fields) !== null && _g !== void 0 ? _g : {},
                        eventsWithInvalidIdLengths: (_h = responseJSON.events_with_invalid_id_lengths) !== null && _h !== void 0 ? _h : {},
                        epsThreshold: (_j = responseJSON.eps_threshold) !== null && _j !== void 0 ? _j : 0,
                        exceededDailyQuotaDevices: (_k = responseJSON.exceeded_daily_quota_devices) !== null && _k !== void 0 ? _k : {},
                        silencedDevices: (_l = responseJSON.silenced_devices) !== null && _l !== void 0 ? _l : [],
                        silencedEvents: (_m = responseJSON.silenced_events) !== null && _m !== void 0 ? _m : [],
                        throttledDevices: (_o = responseJSON.throttled_devices) !== null && _o !== void 0 ? _o : {},
                        throttledEvents: (_p = responseJSON.throttled_events) !== null && _p !== void 0 ? _p : [],
                    },
                };
            case Status.PayloadTooLarge:
                return {
                    status: status,
                    statusCode: statusCode,
                    body: {
                        error: (_q = responseJSON.error) !== null && _q !== void 0 ? _q : '',
                    },
                };
            case Status.RateLimit:
                return {
                    status: status,
                    statusCode: statusCode,
                    body: {
                        error: (_r = responseJSON.error) !== null && _r !== void 0 ? _r : '',
                        epsThreshold: (_s = responseJSON.eps_threshold) !== null && _s !== void 0 ? _s : 0,
                        throttledDevices: (_t = responseJSON.throttled_devices) !== null && _t !== void 0 ? _t : {},
                        throttledUsers: (_u = responseJSON.throttled_users) !== null && _u !== void 0 ? _u : {},
                        exceededDailyQuotaDevices: (_v = responseJSON.exceeded_daily_quota_devices) !== null && _v !== void 0 ? _v : {},
                        exceededDailyQuotaUsers: (_w = responseJSON.exceeded_daily_quota_users) !== null && _w !== void 0 ? _w : {},
                        throttledEvents: (_x = responseJSON.throttled_events) !== null && _x !== void 0 ? _x : [],
                    },
                };
            case Status.Timeout:
            default:
                return {
                    status: status,
                    statusCode: statusCode,
                };
        }
    };
    BaseTransport.prototype.buildStatus = function (code) {
        if (code >= 200 && code < 300) {
            return Status.Success;
        }
        if (code === 429) {
            return Status.RateLimit;
        }
        if (code === 413) {
            return Status.PayloadTooLarge;
        }
        if (code === 408) {
            return Status.Timeout;
        }
        if (code >= 400 && code < 500) {
            return Status.Invalid;
        }
        if (code >= 500) {
            return Status.Failed;
        }
        return Status.Unknown;
    };
    return BaseTransport;
}());
export { BaseTransport };
//# sourceMappingURL=base.js.map