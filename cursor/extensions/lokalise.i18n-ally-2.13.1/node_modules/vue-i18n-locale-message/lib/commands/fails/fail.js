"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function typeGuard(o, className) {
    return o instanceof className;
}
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function defineFail(UserError, code) {
    return (msg, err) => {
        if (msg) {
            // TODO: should refactor console message
            console.error(msg);
            process.exit(1);
        }
        else {
            if (typeGuard(err, UserError)) {
                // TODO: should refactor console message
                console.warn(err.message);
                process.exit(code);
            }
            else {
                // preserve statck! see the https://github.com/yargs/yargs/blob/master/docs/api.md#failfn
                throw err;
            }
        }
    };
}
exports.default = defineFail;
