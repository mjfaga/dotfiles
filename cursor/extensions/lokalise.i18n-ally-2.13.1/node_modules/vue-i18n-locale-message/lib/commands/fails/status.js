"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.fail = exports.TranslationStatusError = void 0;
const fail_1 = __importDefault(require("./fail"));
class TranslationStatusError extends Error {
}
exports.TranslationStatusError = TranslationStatusError;
exports.fail = fail_1.default(TranslationStatusError, 4 /* NotYetTranslation */);
exports.default = {
    TranslationStatusError,
    fail: exports.fail
};
