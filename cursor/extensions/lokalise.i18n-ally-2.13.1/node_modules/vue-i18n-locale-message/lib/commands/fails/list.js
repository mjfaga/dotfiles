"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.fail = exports.LocaleMessageUndefindError = void 0;
const fail_1 = __importDefault(require("./fail"));
class LocaleMessageUndefindError extends Error {
}
exports.LocaleMessageUndefindError = LocaleMessageUndefindError;
exports.fail = fail_1.default(LocaleMessageUndefindError, 5 /* UndefinedLocaleMessage */);
exports.default = {
    LocaleMessageUndefindError,
    fail: exports.fail
};
